import os

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17\docs"

content_dict = {
    "databricks/architecture.md": r"""# Databricks Architecture (Control Plane vs Data Plane)

### 1. 【エンジニアの定義】Professional Definition

> **Control Plane (コントロールプレーン)**:
> Databricksが自社クラウド内でホスト・管理する中央管理領域。Web UI、ノートブックストレージ、ワークスペース管理、ジョブスケジューラ、およびクラスタ管理機能（DBR/VMの制御コマンド）が含まれます。
> 
> **Data Plane (データプレーン)**:
> 顧客(あなた)のクラウド環境（Azure/AWS/GCP）内にデプロイされる計算リソース領域。実際のVM（Sparkクラスタ）が立ち上がり、顧客のデータストア（ADLSやS3）に対してデータを処理します。データ自体がControl Planeに送信されることはありません。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 🔑 「誰が何を管理するのか？」(責任共有モデル)
Databricksが「セキュア」と言われる理由がここにあります。
通常、フルマネージドのSaaSを使うと「自社の機密データを外部サービスに渡す」ことになり、セキュリティ審査が厳しくなります。しかし、Databricksアーキテクチャでは**「データは自室(Data Plane)から一歩も外に出ない。シェフ(Control Plane)はレシピと指示だけを自室に送ってくる」**という仕組みを採用しています。

#### 🌩️ クラスタが立ち上がる裏で何が起きている？
Web UIで「クラスタ起動」ボタンを押すと、以下の通信が発生します。
1. **Control Plane**がクラウドのAPI（Azure Resource Manager等）に「VMを3台作れ」と指示を出します。
2. 顧客のVNet（Data Plane）内にVMが立ち上がります。
3. 立ち上がったVMが**Control Plane**の司令塔に対して「準備できました」と安全な返事(セキュア通信)を返します。
4. ノートブックに書いたSparkコードがData Planeに送られ、顧客のデータレイク（ADLS等）のデータを直接処置・加工します。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

Databricksの分離アーキテクチャの全体像。

```mermaid
graph TD
    subgraph "Databricks Cloud (Control Plane)"
        UI["Web UI / Notebooks"]
        ClusterMgr["Cluster Manager"]
        Jobs["Job Scheduler"]
    end

    subgraph "Customer Cloud - VNet (Data Plane)"
        Driver["Spark Driver Node (VM)"]
        Exec1["Spark Worker Node (VM)"]
        Exec2["Spark Worker Node (VM)"]
        
        Driver --- Exec1
        Driver --- Exec2
    end
    
    subgraph "Customer Storage"
        DataLake[("Data Lake (ADLS/S3)")]
    end

    UI -->|"1. クラスタ起動指示"| ClusterMgr
    ClusterMgr -.->|"2. VM作成(API)"| Driver
    Driver -->|"3. データの読み書き"| DataLake
    Exec1 -->|"3. 分散処理"| DataLake
    Exec2 -->|"3. 分散処理"| DataLake
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **Control Plane**: Databricks社が管理する「脳とUI」。ノートブックやメタデータを持つ。
*   **Data Plane**: 自社のクラウド上に作られる「手足」。データ加工を実際に行う。
*   **セキュリティの核心**: 生のデータは絶対にControl Planeには流れ込まない。
""",

    "databricks/delta_lake.md": r"""# Delta Lake Core Dynamics

### 1. 【エンジニアの定義】Professional Definition

> **Delta Lake**:
> 既存のデータレイク（Parquetファイル群）の上に、ACIDトランザクション、タイムトラベル（履歴管理）、スキーマの強制/進化などの機能を追加するオープンソースのストレージレイヤー。
> 
> **_delta_log**:
> Delta Lakeにおける全てのトランザクション記録（コミット）を保持するJSON/Parquetファイルを含む隠しディレクトリ。データの「現在の正式な状態」は、実際のParquetファイルとこのログの組み合わせで決定される。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 💾 なぜParquetだけではダメなのか？
かつてのデータレイクは、単にADLSやS3にParquetファイルを積み上げるだけでした。しかし、この手法には致命的な弱点がありました。
**「もしデータ更新（UPDATE）中にサーバーが落ちたら？」**
半分だけ更新された壊れたParquetファイルが生まれ、分析クエリはエラーで死にます。
Delta Lakeは、RDBMS（MySQL等）が持っていた「トランザクションログ（失敗したらロールバックする仕組み）」をデータレイクに持ち込みました。それが `_delta_log` フォルダです。

#### ⏳ タイムトラベルの魔法
Delta Lakeで「間違えてデータを消したから昨日の状態に戻して！」と言われたら、1行のSQLで直ります。
`RESTORE TABLE my_table TO TIMESTAMP AS OF '2023-10-01'`
なぜこれが可能かというと、Delta LakeはデータをUPDATEやDELETEしても、**古いParquetファイルをすぐには物理削除しない**からです。`_delta_log`が「今はVer.2を見ろ、Ver.1のファイルは無視しろ」と指示しているだけなので、ログの読み込み先を切り替えるだけで時間を遡れます（※不要になった古いファイルは `VACUUM` コマンドで物理削除します）。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

Delta Lakeの読み込みとコミットログの解決ステップ。

```mermaid
sequenceDiagram
    participant User as "Spark (分析クエリ)"
    participant Log as "_delta_log (コミットログ)"
    participant S3 as "Data Lake (Parquet Files)"

    User->>Log: "SELECT * FROM my_table"
    Log-->>User: "有効なファイルは A.parquet と C.parquet のみ！<br/>(B.parquetは古いから無視して)"
    
    User->>S3: "A.parquet と C.parquet をスキャン"
    S3-->>User: "データ返却 (一貫性の保証された結果)"
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **Delta Lake**: Parquetファイル + トランザクションログ（`_delta_log`）の組み合わせ技術。
*   **ACIDトランザクション**: 途中で落ちてもデータが壊れない。データレイクの弱点を克服。
*   **Time Travel & VACUUM**: 古いデータは保持されるためタイムトラベル可。ゴミ掃除には `VACUUM` が必要。
""",

    "databricks/performance.md": r"""# Databricks Performance & Optimization

### 1. 【エンジニアの定義】Professional Definition

> **Adaptive Query Execution (AQE)**:
> Hiveや今までのSparkではクエリ実行前に「実行計画」を固定していましたが、Spark 3.0(AQE)ではクエリ実行中の段階的な結果を見て、「シャッフルのパーティション数を調整する」「Join戦略をブロードキャストJoinに変更する」など、動的に計画を**最適化**する機能。
> 
> **OPTIMIZE & Z-ORDER**:
> たくさんの小さなファイルを少数の中規模ファイルにまとめる（Bin-packing: `OPTIMIZE`）と同時に、指定したカラムのデータが物理的に近くに配置されるよう並べ替える（`Z-ORDER`）Delta Lake専用のファイルレイアウト最適化技術。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 🐢 クラスタをデカくしても遅い理由
Databricksで「とにかく遅い」という相談の9割は、**Small File Problem（小ファイル問題）**か**Data Skew（データの偏り）**です。
*   **Small File Problem**: 毎分ストリーミングでデータを保存すると、1KBの小さなParquetファイルが数百万個できます。Sparkがこのデータを読み込む時、「ファイルを開きメタデータを取得する時間」だけで全体の80%を消費し激遅になります。解決策は定期的な `OPTIMIZE` コマンドです。

#### 🎲 Z-ORDER という最強のインデックス
SQLでいう「インデックス」に近いのが `Z-ORDER` です。
例えば「顧客ID」で頻繁にWHERE絞り込みをする場合、`OPTIMIZE table_name ZORDER BY (customer_id)` を実行すると、ファイルをまたいで顧客IDの順番が揃うように整理されます。
クエリ時、Databricksはファイルのメタデータ（このファイルにはID:100〜200が入っている）だけを読み取り、目当てのIDがないファイル群は**丸ごとスキップ（Data Skipping）**します。数百GBの読み込みが瞬時に終わる魔法です。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

OPTIMIZE と Z-ORDER による Data Skipping の仕組み。

```mermaid
graph LR
    subgraph "Before OPTIMIZE (分散)"
        F1["File A (ID: 1, 99, 45)"]
        F2["File B (ID: 3, 2, 88)"]
        F3["File C (ID: 55, 4, 12)"]
    end

    subgraph "After OPTIMIZE ZORDER BY ID"
        F4["File X (ID: 1, 2, 3)"]
        F5["File Y (ID: 4, 12, 45)"]
        F6["File Z (ID: 55, 88, 99)"]
    end

    Q["Query: SELECT * WHERE ID = 2"]
    Q -->|"File A,B,C 全部開く必要がある..."| F1
    Q -->|"Skip!"| F5
    Q -->|"Skip!"| F6
    Q -->|"File X だけ開けばヨシ (爆速)"| F4
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **AQE**: エンジン実行中に動的に賢くなるSpark 3.0の標準機能。
*   **OPTIMIZE**: 大量のゴミ箱（小ファイル）を大きなコンテナに整理して、スキャン速度を劇的に上げる。
*   **Z-ORDER**: 特定の列で「Data Skipping」を発動させるための物理的ソート機能。
""",

    "python/pyspark.md": r"""# PySpark Fundamentals

### 1. 【エンジニアの定義】Professional Definition

> **PySpark**:
> Apache Spark（分散処理エンジン）をPythonから呼び出すためのAPI。裏側ではPy4Jというライブラリを通じてJava Virtual Machine (JVM) 上のSparkコアエンジンと通信し、高速なビッグデータ処理を行う。
> 
> **Lazy Evaluation (遅延評価)**:
> PySparkは、「変換処理（`filter`, `select` 等）」を実行してもすぐには計算を行わず、結果の出力が必要になる「アクション処理（`show`, `count`, `write` 等）」が呼ばれた段階で初めて、全体の最適化された計算ルートを設計して一気に実行する仕組み。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 🐍 DataFrame と Pandas の決定的な違い
ローカルで動くPandasを使っていた人がPySparkに触れると、データが「見えない」ことにイライラします。
*   **Pandas**: `df = df[df['age'] > 20]` を実行すると、即座にメモリ上で計算が行われ、`df.head()` ですぐ見れます。
*   **PySpark**: `df = df.filter(df.age > 20)` を実行しても、**何も起きていません**。Sparkは「ああ、後でage>20でフィルターすればいいのね」と計画書（DAG）にメモするだけです。（これが Lazy Evaluation）。
*   そして `df.count()` (アクション) が呼ばれた瞬間、100台のサーバーに計画書を配り、一斉に計算を開始します。

#### 💻 OOM (Out Of Memory) はなぜ起きるか？
PySpark開発で最も多いエラーは「ドライバーノードのメモリ枯渇」です。
`df.collect()` や `df.toPandas()` というコマンドは、100台のサーバーに分散している数TBのデータを、**たった1台の司令塔（Driver）のメモリに一挙に集約**しようとします。容量が数GBしかないDriverは一瞬でクラッシュします。
集計や絞り込みを終えて、出力結果が確実に小さくなった（数万行程度）時だけ `collect` するのが鉄則です。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

Sparkの遅延評価（Lazy Evaluation）とアクションの挙動。

```mermaid
graph TD
    Code["実行: df.filter().select().groupBy()"] -->|"Transformation: まだ計算しない"| DAG["計画書 (Lineage) を作成"]
    DAG -->|"アクションまで待機..."| Wait["何も起きない"]
    
    Action["実行: df.show() または df.write()"] -->|"Action: ここで初めて動く"| Optimizer["Catalyst Optimizer (最適化)"]
    Optimizer --> Workers["複数WorkerにTaskを分配して一斉計算"]
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **PySpark**: 分散処理エンジンSparkを操るPythonの魔法の杖。裏はJVM。
*   **Lazy Evaluation**: 「実行！」と言われるまでギリギリまでサボる（最適化を考える）仕組み。
*   **Driver OOM**: 巨大データを `collect()` や `toPandas()` で一箇所に集める行為は自爆行為。
""",

    "dbt/index.md": r"""# dbt (Data Build Tool) Fundamentals

### 1. 【エンジニアの定義】Professional Definition

> **dbt (Data Build Tool)**:
> データウェアハウス内にロードされた生データに対して、SQLのみを使ってデータ変換（Transform）処理を行うためのオープンソースツール。ETLの「T」の部分に特化している。
> 
> **Analytics Engineering**:
> バックエンド（システム設計）とデータ分析（ビジネス理解）の橋渡しをする新しいロール。dbtを用いて、ソフトウェアエンジニアリングのベストプラクティス（Gitバージョン管理、CI/CD、テスト）をSQLデータ変換パイプラインに持ち込む。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 🔧 「ただのSQL群」から「データプロダクト」へ
昔のデータ分析は、誰が書いたか分からない数千行のストアドプロシージャや、毎朝動く巨大なバッチ処理SQLの塊（負債）でした。
dbtはこれに革命を起こしました。
*   **依存関係の自動解決**: `ref('stg_users')` のような独自のJinjaテンプレート関数を使うことで、「どのSQLを実行すれば、次のSQLが動くか」という依存グラフ（DAG）を自動で作成し、正しい順序で実行してくれます。
*   **自動テストの力**: YAMLファイルに `not_null` や `unique` と数行書くだけで、「このカラムに空データが入ってこないか？」を毎朝自動でテストしてくれます。バグのあるデータがBIツール（TableauやLooker）に表示される前に防げます。

#### 🌟 なぜ今、dbtが必須級スキルなのか？
Snowflake、BigQuery、DatabricksといったクラウドDWHが超高速になったため、データを外部サーバーで加工せず、**直接DWHの中で加工する（ELTアーキテクチャ）**のが主流になりました。このDWH内部での「T（変換）」の指揮を執るオーケストレーターとして、dbtはデファクトスタンダードになりました。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

モダンデータスタックにおけるdbt（ELTアーキテクチャ）の位置づけ。

```mermaid
graph LR
    subgraph "Extract & Load (Fivetran/Airbyte)"
        Sources["SaaS / DBs"] -->|"そのままコピー(生データ)"| Raw["Raw Area<br>(DWH / Databricks)"]
    end
    
    subgraph "Transform (dbt)"
        Raw -->|"dbt (SQL + Jinja)"| Staging["Staging Models"]
        Staging -->|"dbt Docs / Tests"| Marts["Data Marts<br>(Business Ready)"]
    end
    
    subgraph "BI / AI"
        Marts --> Dashboard["Tableau / Looker / AI"]
    end
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **dbt**: 分析SQLの世界に、Gitやテストといった「ソフトウェア開発の規律」をもたらした革命的ツール。
*   **Jinjaとref関数**: テーブル名の手打ちハードコードを廃止し、依存関係（DAG）を自動生成する。
*   **ELTの絶対的王者**: データを事前に加工せず、DWHの「中で」加工する現代アーキテクチャに必須。
""",

    "airflow/index.md": r"""# Apache Airflow Core Mechanics

### 1. 【エンジニアの定義】Professional Definition

> **Apache Airflow**:
> Pythonコードを用いて複雑なデータ処理パイプラインの定義、スケジュールリング、および監視を行うためのプラットフォーム。Airbnbが開発しオープンソース化。
> 
> **DAG (Directed Acyclic Graph)**:
> 「有向非巡回グラフ」。Airflowにおけるワークフロー全体を定義する単位。「タスクAが終わったらタスクBとCを並行して実行する。一巡してAには戻らない」という実行順序をノードとエッジで表現したもの。
> 
> **Operators**:
> Airflow内で単一のタスクを実行するためのテンプレート。Pythonスクリプトを実行する`PythonOperator`や、Bashコマンドを実行する`BashOperator`などがある。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### ⏱️ ただのCronと何が違うのか？
Linuxの`cron`を使えば「毎朝3時にスクリプトを動かす」ことは簡単です。しかしデータ基盤では限界があります。
「APIからデータを取るスクリプトが**失敗したら**どうなる？」「もし1日止まってしまって、**過去3日分を再実行**したい時は？」
Airflowは、データエンジニアリング特有のエラーハンドリングに極めて強いです。特定のタスクが失敗すればアラートを鳴らし、途中から安全に再実行できるGUIと仕組みが備わっています。

#### 🐘 AirflowとDatabricksの連携
「Airflowで重いデータ処理を書く」のは**アンチパターン**です。
Airflowはあくまで「オーケストレーター（指揮者）」です。Airflow自体（ワーカー）のメモリ上で数GBのデータを処理してはいけません。
正しい使い方は、Airflowの`DatabricksSubmitRunOperator`を使って、「Databricks(実行部隊)よ、この巨大なクエリを実行して結果を保存せよ」と**API経由で指示だけ送る**ことです。指揮者は指揮棒を振るだけで、楽器（データ処理）は演奏しません。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

Airflowがオーケストレーターに徹するモダン構成。

```mermaid
graph TD
    subgraph "Airflow (指揮者)"
        DAG["Airflow DAG (Python)"]
        T1["Task 1: S3 Sensor<br>(ファイルの到着を待つ)"]
        T2["Task 2: DatabricksOperator<br>(指示を送る)"]
        T3["Task 3: EmailOperator<br>(完了通知)"]
        DAG --> T1 --> T2 --> T3
    end

    subgraph "Databricks (実行部隊)"
        DL["Data Lake"]
        Spark["Spark Cluster"]
        
        T2 -.->|"APIでジョブ起動指示"| Spark
        Spark -->|"テラバイト級の重いデータ処理"| DL
    end
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **Airflow**: コード(Python)としてデータパイプラインを定義できる最強の指揮者。
*   **DAG**: 依存関係と実行順を示す一本道のグラフ。ループはしない（Acyclic）。
*   **指揮者のルール**: Airflowに重たい計算をさせてはいけない。計算はDatabricksやSnowflakeに投げ、Airflowは進捗を見守るだけ。
""",

    "certifications/gcp_ace.md": r"""# Google Cloud ACE (Associate Cloud Engineer) Roadmap

### 1. 【エンジニアの定義】Professional Definition

> **Google Cloud ACE**:
> Google Cloud環境でのアプリケーションのデプロイ、エンタープライズソリューションのモニタリングや運用管理能力を問う登竜門的資格。GCPの広範なサービス（Compute, Storage, Network, IAM等）の基礎とCLI操作の理解が必要となる。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### ☁️ "gcloud" コマンドラインの圧倒的重要度
他のクラウド資格（AWSやAzure）と比べ、GCP ACEが際立っている特徴は**コマンドラインツール（CLI）からの出題が非常に多い**ことです。
「Web画面のどこをクリックするか」ではなく、`gcloud compute instances create ...` や `gsutil cp ...` のような具体的なコマンド体系を理解しているか問われます。実務ではシェルスクリプトでインフラ自動化を行うため、この知識は即戦力になります。

#### 🔑 IAMとプロジェクト構造の独自性
Azureの「サブスクリプション/リソースグループ」やAWSの「アカウント」にあたるのが、GCPの「Project」です。
そしてGCPの**IAM（権限管理）**は強力ですが独特です。「プリミティブロール（閲覧者、編集者、オーナー）」と「事前定義ロール」の違いを明確にし、原則として「最小特権の原則を満たす事前定義ロール」を付与するアーキテクチャがテストで問われます。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

GCP ACEで必ず理解すべき、プロジェクト・リソース群の階層モデル。

```mermaid
graph TD
    Org["Organization<br>(会社全体・組織)"]
    Folder["Folder<br>(事業部/環境 - オプション)"]
    Proj["Project<br>(全リソースの境界・課金単位)"]
    
    subgraph "GCP Resource Types"
        GCE["Compute Engine (VM)"]
        GCS["Cloud Storage (S3相当)"]
        IAM["IAM (権限)"]
    end

    Org --> Folder
    Folder --> Proj
    Proj --> GCE
    Proj --> GCS
    Proj --> IAM
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **CLIの徹底**: `gcloud` (全体管理), `gsutil` (ストレージ), `bq` (BigQuery), `kubectl` (K8s) の使い分けをマスターする。
*   **Project単位の管理**: GCPの課金と権限の基本単位は「Project」である。
*   **IAMと最小特権**: 常に「最も権限の少ない事前定義ロール」を選ぶ選択肢が正解になるケースが多い。
"""
}

# Ensure directories exist and write files
for filepath, content in content_dict.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Brushed up {len(content_dict)} core mkdocs pages successfully!")
