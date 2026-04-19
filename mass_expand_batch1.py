import os
import glob
import json
import time

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")
os.makedirs(docs_dir, exist_ok=True)

deep_content = {
    # ==========================
    # Axis 02: Python Core & Internals
    # ==========================
    "python/gil_and_multiprocessing.md": r"""# GIL & Multiprocessing Architecture
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「スレッドを増やせば速くなる」はPythonでは通用しない**
JavaやC#の背景を持つエンジニアがPythonで重い計算（CPUバウンド）を行う際、真っ先に使おうとするのが `threading` モジュールです。ところが、4コアのCPUでもCPU使用率が25%（1コア分）から上がらず、まったく高速化されないという壁にぶつかります。
これは Python (厳密にはCPython実装) の中核にある **GIL (Global Interpreter Lock)** という「1度に1つのスレッドしかPythonのバイトコードを実行してはならない」という絶対的なロック機構が存在するためです。この制限を回避し、マシンの全コアをフルに使い切るための正解が、OSレベルでメモリ空間をごと分割する `multiprocessing` の活用です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**OSプロセスのフォークとIPC (Inter-Process Communication)**
マルチスレッドが「同じ部屋（メモリ空間）で複数人が交代で作業する（Pythonでは大蔵省の許可=GILが必要）」のに対し、マルチプロセスは「部屋（メモリ）ごと複製し、全く別の独立した作業空間を作る」アプローチです。
Windowsでは `spawn`、Unix系では `fork` の仕組みでプロセスが分身を生成します。別々のプロセスになるためGILの制約は受けませんが、今度はプロセス間でデータを受け渡すために「Pickle（シリアライゼーション）」と「IPC通信（パイプやソケット）」という重いオーバーヘッドが発生します。

```mermaid
graph TD
    classDef main fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef sub fill:#312e81,stroke:#8b5cf6,stroke-width:2px;
    
    A[Main Process <br/> Memory A]:::main -->|Fork/Spawn + Pickle Data| B(Sub Process 1 <br/> Memory B):::sub
    A -->|Fork/Spawn + Pickle Data| C(Sub Process 2 <br/> Memory C):::sub
    
    B -->|CPU 100%| B1[Process Heavy Data]:::sub
    C -->|CPU 100%| C1[Process Heavy Data]:::sub
    
    B1 -->|Return Pickled Result| A
    C1 -->|Return Pickled Result| A
```

### 3. 【実務への応用】Practical Application
* **使い分けの極意**:
  * **I/Oバウンド（通信・ファイル待ち）**: APIを叩くだけ、巨大ファイルをダウンロードするだけ等の処理は `threading` または `asyncio` を使用します（待ち状態の間にGILが解放されるため）。
  * **CPUバウンド（演算待ち）**: 画像処理、巨大なJSONテキストのパース、機械学習の純粋な計算などは `multiprocessing.Pool` または `concurrent.futures.ProcessPoolExecutor` を使用してコア数分だけプロセスを散らします。
* **アンチパターン**: プロセス間通信で数ギガバイトのPandas DataFrameをそのまま渡すと、Pickle/Unpickle処理だけでCPUとメモリを食いつぶし、逆に激遅になります。巨大データはS3やファイル（Parquet）に一度書き出し、各プロセスに「ファイルパス（文字列）」だけを渡して各個に読み込ませるのがプロの設計です。
""",

    "python/memory_management.md": r"""# Memory Management & Garbage Collection
### 1. 【課題解決のメカニズム】Mechanism of Problems
**OOM (Out of Memory) キラーの恐怖**
データパイプラインにおいて、「ローカルで動いたスクリプトが、本番の10GBのデータを読み込んだ瞬間にコンテナが死ぬ」という事故。Pythonは自動でメモリを掃除する機能（Garbage Collection: GC）を持っていますが、オブジェクトの参照が残っていたり、巨大なリストを作成しっぱなしにすると、メモリは解放されずプロセスごとOSから強制終了（OOM Kill）されます。
メモリ管理の裏側を知ることで、メモリ消費量を1/100に抑えるようなエコなコードを書くことがデータエンジニアの義務です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Reference Counting vs Generational GC**
Pythonメモリ管理には2つのエンジンが搭載されています。
1. **参照カウント (Reference Counting)**:
   ある変数（オブジェクト）が誰から何回参照されているかをカウント（`ob_refcnt`）します。ローカル変数のスコープを抜けるなどでカウントが `0` になった瞬間、即座にメモリから消去されます。これが第一の防衛線です。
2. **世代別ガベージコレクション (Generational GC)**:
   `A` が `B` を参照し、`B` が `A` を参照しているような「循環参照」が発生すると、カウントは永遠に0になりません。これを検知して掃除するのが世代別GCです。オブジェクトを「若い世代」「中堅世代」「古い世代」に分け、若い世代を頻繁に掃除し、長生きしているオブジェクトは極力チェックを省くことでパフォーマンスを落とさずに循環参照を破壊します。

### 3. 【実務への応用】Practical Application
* **明示的な `del` と `gc.collect()`**:
  巨大な辞書やデータフレームを処理した後、もう使わないのであれば `del df` で明示的に参照を切り、直後に `import gc; gc.collect()` を呼ぶことで強制的にヒープメモリをOSに返還させることができます（メモリギリギリのコンテナでおこなう防御的プログラミング）。
* **`__slots__` の活用**:
  Pythonのクラスは通常、内部に可変な辞書 (`__dict__`) を持って属性を管理するため、インスタンス一つあたりのメモリが重いです。数千万のデータクラスインスタンスをメモリに抱える場合は、クラス定義に `__slots__ = ['id', 'name']` と書くだけで辞書の生成を防ぎ、メモリ消費を半分以下に抑えることができます。
""",

    "python/generators.md": r"""# Generators, Iterators & Lazy Evaluation
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「全部メモリに乗せる」という破滅的な思考**
100GBのCSVファイルを処理しろと言われたとき、`lines = open('data.csv').readlines()` と書いた時点で、Pythonは100GBのデータをすべてメモリ（RAM）上の List オブジェクトに展開しようと試み、即座にサーバーをクラッシュさせます。
無限に続くデータや、RAMの限界を超えるデータを「1行ずつ安全に、舐めるように処理する」ための仕組みが「ジェネレーター (Generators)」による遅延評価 (Lazy Evaluation) です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**`yield` による「状態の一時停止と再開」**
関数内で `return` ではなく `yield` を使うと、その関数は「値を返して終了する」のではなく「値を返した時点で状態（ローカル変数など）をフリーズして一時停止し、次に `next()` が呼ばれるまで待機する」特殊なオブジェクトになります。
ジェネレーターは「今処理している1つの要素」しかメモリ空間に置かないため、1万行のファイルだろうと1億行のファイルだろうと、メモリ消費量は「数バイト」で一定を保ちます。

```mermaid
sequenceDiagram
    participant Caller as 呼び出し元 (for_loop)
    participant Gen as ジェネレーター関数
    
    Caller->>Gen: next(gen) - 最初の値ちょうだい
    Gen->>Gen: 1行目をディスクから読む
    Gen-->>Caller: yield "行1" (そして停止)
    Caller->>Caller: "行1"をパース・DBにInsert
    Caller->>Gen: next(gen) - 次の値ちょうだい
    Gen->>Gen: 【再開】2行目を読む (1行目は破棄)
    Gen-->>Caller: yield "行2" (そして停止)
    Note over Caller,Gen: メモリには常に1行分しか存在しない
```

### 3. 【実務への応用】Practical Application
* **超絶省メモリなETLパイプライン**:
  AWS S3上の巨大なファイルをBoto3でストリーム読み込みし、`yield` でチャンク（1000行ずつなど）ごとに後段のAPIやデータベースに流し込むことで、コンテナのメモリサイズを最小（256MB程度）に抑えつつ無限のデータを処理するパイプラインが構築できます。
* **メモリ枯渇のアンチパターン**:
  ジェネレータから受け取った値を、うっかり `result_list.append(data)` のようにループ内で巨大なリストに貯め込んでしまっては遅延評価の意味がありません。受け取った端から外部（DBなど）に吐き出す（Sink）アーキテクチャにすることが肝要です。
""",

    # ==========================
    # Axis 03: PySpark Optimization
    # ==========================
    "pyspark/shuffles.md": r"""# Spark Shuffle Mechanics & Optimization
### 1. 【課題解決のメカニズム】Mechanism of Problems
**シャッフル：分散処理における最悪のペナルティ**
Sparkを用いた分散処理において、特定のノード内で完結する処理（`map`, `filter`）は非常に高速です。しかし、`groupBy`、`join`、`window` といった「全体を見渡さないと答えが出ない演算」を行うと、クラスター内のすべてのワーカーノード間でデータの「大移動と再配分」が発生します。これが「シャッフル（Shuffle）」です。
シャッフルは「ディスクへの書き込み」「ネットワーク越しのシリアライズ通信」「別ノードでの読み込みとソート」という最もコストの高いI/Oを伴うため、Sparkジョブの遅延要因の90%以上を占めます。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Shuffle Write と Shuffle Read**
Sparkは処理を「ステージ (Stage)」という単位で区切ります。シャッフルが発生する境界でステージは分断されます。
1. **Shuffle Write (Map側)**: 前のステージの各タスクは、次にデータをどのパーティション（ノード）へ送るべきか計算します（通常はハッシュ値による `HashPartitioner`）。送信先ごとに一旦ローカルのディスクへデータを書き出します（メモリ枯渇防止のため）。
2. **Shuffle Read (Reduce側)**: 次のステージのタスクは、クラスター全域から自分宛てに書かれたローカルファイルをネットワーク越しに取りに行き（Fetch）、メモリ上でマージしてソートなどの後続処理を行います。

ここで、ある特定キー（例: ユーザーID `null` や、巨大店舗のID）にデータが異常に集中している場合（Data Skew）、特定のReducerだけが数テラバイトのシャッフルリードを行う羽目になり、1つのタスクだけが延々と終わらない悲劇が発生します。

### 3. 【実務への応用】Practical Application
* **Data Skew（データの偏り）の解消**:
  結合（Join）キーにある少数の巨大な値を意図的に分散させるため、結合キーにランダムな塩（Salt: `1~10`の乱数など）を付与して結合する「Salting（ソルティング）」が実務の究極奥義です。これにより、重いタスクを強制的に10個のノードに均等分散させます。
* **AQE (Adaptive Query Execution)**:
  近年のSpark（Databricks）では、AQEを有効 (`spark.sql.adaptive.enabled = true`) にするだけで、シャッフル中に偏りを動的に検知し、裏側で勝手にパーティションを分割・最適化してくれます。ただしAQEでも救えないような巨大Skewには、依然としてSalting等の論理的アプローチが必要です。
""",
    
    "pyspark/broadcast_joins.md": r"""# Broadcast Hash Join (The Silver Bullet)
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「シャッフルを消滅させる」究極のJoin手法**
10億行のトランザクションテーブル（数TB）と、数万行のカテゴリーマスターテーブル（数MB）を結合（Join）したい場合、通常なら両方のテーブル間で「ID」を基準にした大シャッフル（Sort Merge Join）が発生し、膨大な時間がかかります。
一方が明らかにメモリに収まるような小規模テーブルであると分かっている場合、「全ノードにマスターテーブルのコピーを配る」ことで、**シャッフルを完全にゼロにする**魔法のアプローチが存在します。それが `Broadcast Hash Join` です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
どのようにしてシャッフルを回避するのでしょうか？
1. **Driverへの収集**: 小さい方のテーブル（マスター）を一度Sparkの司令塔（Driverノード）にすべて集めます (`collect()`)。
2. **Broadcast（同報通信）**: Driverからクラスター内の全Executor（ワーカー）のメモリへ、その小さなテーブルをそのまま送信し、ハッシュテーブルとしてキャッシュします。
3. **Map-Side Join**: 巨大なトランザクションテーブルの処理を行うワーカーは、自分の横（同じメモリ空間）にマスターテーブルがあるため、ネットワーク通信もディスク書き込みも一切行わず、流れてくる1行1行に対してメモリ上でルックアップ（結合）を済ませてしまいます。

```mermaid
graph TD
    classDef main fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef sub fill:#312e81,stroke:#8b5cf6,stroke-width:2px;
    classDef warn fill:#7f1d1d,stroke:#f87171,stroke-width:2px;
    
    A[Small Table]:::sub -->|Collect| B(Driver Node):::warn
    B -->|Broadcast via BitTorrent protocol| E1[Executor 1 Memory]:::sub
    B -->|Broadcast| E2[Executor 2 Memory]:::sub
    
    C[Huge Table pt.1]:::main -->|Map Task (No Shuffle)| E1
    D[Huge Table pt.2]:::main -->|Map Task (No Shuffle)| E2
    
    E1 --> F[Joined Output]:::main
    E2 --> F
```

### 3. 【実務への応用】Practical Application
* **明示的なヒント (Hint)**:
  Sparkエンジンがテーブルサイズを見誤り、勝手にSort Merge Joinを選んで激遅になることが実務では多発します（特に複雑なフィルタリングを重ねた後）。この場合、`df_massive.join(broadcast(df_small), "id")` と明示的にヒントを渡すことで、強制的にBroadcastさせることができます。
* **OOMのリスク**:
  ブロードキャストするテーブルがDriverのメモリ（通常は比較的小さい）やExecutorのメモリに乗らないほど大きい場合、Driver OOMでジョブが突然死します。デフォルト閾値（`spark.sql.autoBroadcastJoinThreshold` = 約10MB）を無闇にギガバイト単位まで引き上げるのは非常に危険なアンチパターンです。
""",

    # ==========================
    # Axis 04: Lakehouse Storage
    # ==========================
    "storage/delta_lake.md": r"""# Delta Lake Architecture & Transaction Logs
### 1. 【課題解決のメカニズム】Mechanism of Problems
**データレイクの「更新できない・壊れる」という致命傷**
単なるS3等の上のParquetファイルの集まり（データレイク）では、ファイルが処理中にクラッシュした場合、不完全な「中途半端なファイル群」が残されます。これにより、後続のBIツールが不正なデータやゴミを読み込んでしまう「ダーティーリード」が発生します。また、更新（UPDATE）や削除（DELETE）も、全ファイルを読み込んで書き直すという地獄の運用になります。
この問題を解決し、S3上のただのファイル群にRDBMSのようなACIDトランザクション（完全性の保証）をもたらすレイヤーが Delta Lake です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**`_delta_log` ディレクトリの美しき仕組み**
Delta Lakeの正体は、データフォルダの直下に作られる `_delta_log` という隠しディレクトリに格納される「JSON（コミットログ）」の集まりです。
テーブルにデータが追記（Append）されたり、削除されたりするたびに、`000000.json`, `000001.json` といったシーケンシャルなファイルが生成されます。この中には「どのParquetファイルが追加され(`add`)、どのファイルが削除されたか(`remove`)」という明細が記載されています。

リーダー（読み込む側）は、まずこの `_delta_log` の最新のJSONを読み、「現在有効なParquetファイルのリスト」を完全に特定します。裏で古いファイルが消されていようと、新しいファイルが中途半端に書かれている最中だろうと、「コミットログに書かれているファイルしか絶対に読まない」ため、読み取りの一貫性（Snapshot Isolation）が完璧に保証されます。

### 3. 【実務への応用】Practical Application
* **Time Travel（タイムトラベル）**:
  間違って全データを消してしまった（DROP/DELETE）としても、Delta Lakeでは「実際には裏のParquetファイルは直ちには消えない（ログ上で `remove` 扱いになるだけ）」という仕様です。そのため、`SELECT * FROM table VERSION AS OF 5` と打つだけで、1秒で過去の正常なバージョンの中身を「復活」させることができます。
* **OPTIMIZEとVACUUMの重要性**:
  何度も追記を繰り返すと、数KBの微小なParquetファイルが数万個発生し（Small Files Problem）、読み出しが極端に遅くなります。これを定期的に結合するのが `OPTIMIZE` コマンドです。また、タイムトラベル用に残っている「ログ上は消したことになっている古いParquetファイル」の実体を物理削除してストレージ料金を節約するのが `VACUUM` コマンドです。この保守ジョブの定期実行設定は必須です。
""",

    "storage/zorder.md": r"""# Z-Ordering & Data Skipping
### 1. 【課題解決のメカニズム】Mechanism of Problems
**フルスキャンの悪夢とパーティションの限界**
Date（日付）による物理フォルダ分割（Partitioning）は優秀ですが、「特定のProductID」や「特定のCustomerID」で検索をかけた場合、パーティションが切られていない軸での検索となるため、結局全ファイルを走査（フルスキャン）することになります。
かといって「ProductID」でパーティションを切ると、IDの種類が多すぎて「1ファイルのサイズが異常に小さく、フォルダが数千万個できるオーバーパーティション問題」を引き起こしクラスタが死にます。
このトレードオフを次元を超えて解決する数学的アルゴリズムが **Z-Ordering**（多次元クラスタリング）です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Z-Order Curve（Z階数曲線）と Data Skipping**
Databricks（Delta Lake）は裏側で各Parquetファイルごとに「このファイルにはID 100〜500のデータが入っている」という統計情報（Min-Maxステータス）を持っています。
これを利用し、クエリエンジンは「探しているIDが 999 の場合、このファイルはMin=100, Max=500の範囲だから絶対に存在しない」と判断し、**ファイルをS3から読むことすらスキップ**します（Data Skipping）。

しかし、データが完全にバラバラに散らばっていると、全ファイルのMin-Maxが重複してしまいスキップできません。
`OPTIMIZE table ZORDER BY (category, price)` を実行すると、エンジンは2つの次元（カテゴリと価格）の値をビット単位で交差（インターリーブ）させた「Z値」を計算し、多次元空間において近いデータ同士を同じParquetファイル内に物理的に固めて再配置します。
これにより、特定のカテゴリで検索しても、特定の価格帯で検索しても、圧倒的な精度でファイルをスキップできるようになります。

```mermaid
graph LR
    classDef box fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef skip fill:#334155,stroke:#475569,stroke-width:2px,stroke-dasharray: 5 5;
    
    Query(Query: WHERE ID = 800) --> Filter{Min-Max Check}
    Filter -->|File 1: Min=100, Max=500| F1[File Parquet 1]:::skip
    Filter -->|File 2: Min=600, Max=900| F2[File Parquet 2]:::box
    Filter -->|File 3: Min=1000, Max=1500| F3[File Parquet 3]:::skip
    
    note default
    Only File 2 is physically read from Object Storage.
    Incredible IO savings.
    end note
```

### 3. 【実務への応用】Practical Application
* **何をZ-Orderの対象にするか？**:
  カーディナリティ（値の種類）が中規模〜大規模で、よくダッシュボードやクエリの `WHERE` 句のフィルター条件や `JOIN` キーとして使われるカラムに対してZ-Orderをかけます。
* **アンチパターン**:
  すでにPartitioningしているカラム（例: `date`）に対してZ-Orderをかけるのは無意味です。また、Z-Orderに4つも5つもカラムを指定すると効力が激減し、ただのソート処理にCPU/DBUコストを浪費するだけになります（最大で2〜3個のカラムに絞るのが定石）。
"""
}

# 1. 物理ファイル書き出し
for filepath, content in deep_content.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
        
print(f"Generated {len(deep_content)} extremely deep modules. Now rebundling into payload...")

# 2. 中立化・再バンドル・JS書き出し（neutralize_and_expandのエコシステム利用）
# (In order to ensure everything picks up, we read all MDs, format, and push to JS)
bad_words = ["Kazaneya", "KAZANEYA", "Kanazeya", "KAZ", "KANAZEYA", "kanazeya", "kazaneya"]
def neutralize_text(text):
    for w in bad_words:
        if w.isupper():
            text = text.replace(w, "EXPERT")
        elif w.istitle():
            text = text.replace(w, "Advanced")
        else:
            text = text.replace(w, "advanced")
    return text

axes_structure = [
    {"title": "01. Architecture Deep Dives", "filter": "databricks/roi_photon_deep.md"},
    {"title": "01. Architecture Deep Dives", "filter": "modeling/kimball_vs_datavault.md"},
    {"title": "01. Architecture Deep Dives", "filter": "spark/streaming_checkpoints.md"},
    {"title": "02. Python Core & Internals", "filter": "python/"},
    {"title": "03. PySpark Optimization", "filter": "pyspark/"},
    {"title": "04. Lakehouse Storage", "filter": "storage/"},
    {"title": "05. Databricks Deep Compute", "filter": "databricks/"},
    {"title": "06. Dist System Theory", "filter": "dist/"},
    {"title": "07. Database Mechanics", "filter": "db/"},
    {"title": "08. Advanced SQL Mastery", "filter": "sql/"},
    {"title": "09. Modeling Architectures", "filter": "modeling/"},
    {"title": "10. dbt & Integration", "filter": "dbt/"},
    {"title": "11. Orchestration & Event", "filter": "airflow/"},
    {"title": "12. Azure Security VNet", "filter": "azure/"},
    {"title": "13. Identity & Web APIs", "filter": "sec/"},
    {"title": "14. Protocol Defaults", "filter": "net/"},
    {"title": "15. CI/CD & Testing", "filter": "cicd/"},
    {"title": "16. SRE & Observability", "filter": "ops/"},
    {"title": "17. System Design", "filter": "arch/"},
    {"title": "18. Certs", "filter": "certifications/"}, 
    {"title": "19. Misc Specs", "filter": "misc/"},
    {"title": "20. Capstone", "filter": "projects/"}
]

md_files = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True)
md_files = [f.replace(os.sep, "/") for f in md_files]

axes = []
contents_dict = {}

featured_paths = [
    "docs/databricks/roi_photon_deep.md",
    "docs/modeling/kimball_vs_datavault.md",
    "docs/spark/streaming_checkpoints.md"
]
base_md_files = [f for f in md_files if f.replace("/", os.sep) not in [p.replace("/", os.sep) for p in featured_paths]]

def process_file_list(sub_files, ax_idx, axis_title):
    mod_idx = 1
    axis_obj = {"title": axis_title, "modules": []}
    for f in sub_files:
        rel_path = f.replace(base_dir.replace(os.sep, "/") + "/", "")
        mod_id = f"MOD_{ax_idx}.{mod_idx}"
        
        with open(f, "r", encoding="utf-8") as file:
            content = neutralize_text(file.read())
            
        with open(f, "w", encoding="utf-8") as file: # Resave scrubbed
            file.write(content)
            
        title = "Untitled"
        first_line = content.split('\n')[0].strip()
        if first_line.startswith("# "):
            title = first_line[2:]
            
        contents_dict[mod_id] = content
        
        axis_obj["modules"].append({
            "id": mod_id,
            "title": title,
            "path": rel_path
        })
        mod_idx += 1
    return axis_obj

# Featured Axis
featured_axis = {"title": "00. EXPERT SPECIALS", "modules": []}
m_idx = 1
for f_path in featured_paths:
    full_p = os.path.join(base_dir, f_path)
    if os.path.exists(full_p):
        with open(full_p, "r", encoding="utf-8") as file:
            content = neutralize_text(file.read())
        title = content.split('\n')[0].strip()[2:]
        contents_dict[f"VIP.0.{m_idx}"] = content
        featured_axis["modules"].append({
            "id": f"VIP.0.{m_idx}",
            "title": title,
            "path": f_path
        })
        m_idx += 1
axes.append(featured_axis)

for ax_idx, axis_def in enumerate(axes_structure[3:], 1):
    sub_files = [f for f in base_md_files if f.endswith(".md") and (axis_def["filter"] in f)]
    sub_files.sort()
    axis_obj = process_file_list(sub_files, ax_idx, axis_def["title"])
    if axis_obj["modules"]:
        axes.append(axis_obj)

js_content = "const studyData = {\n"
js_content += '    title: "DATA ENGINEERING MASTERY",\n'
js_content += '    subtitle: "Advanced Architectural Deep Dives",\n'
js_content += '    localStorageKey: "study17_advanced_progress",\n'
js_content += '    themeColor: "#14b8a6",\n' 
js_content += '    secondaryColor: "#0ea5e9",\n' 
js_content += '    axes: ' + json.dumps(axes, ensure_ascii=False, indent=4) + '\n};\n\n'
js_content += 'window.moduleContents = ' + json.dumps(contents_dict, ensure_ascii=False, indent=2) + ';\n'

js_path = os.path.join(base_dir, "dashboard_data.js")
with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Batch generation and recompilation complete! {len(axes)} axes wrapped.")

# Update index.html Cache Buster to v=6
html_path = os.path.join(base_dir, "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

import re
html = re.sub(r'src=\"dashboard_data\.js\?v=\d+\"', f'src=\"dashboard_data.js?v={int(time.time())}\"', html)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
