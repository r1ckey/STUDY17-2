import os
import json

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")
os.makedirs(docs_dir, exist_ok=True)

# Define the structure and content for the Massive Encyclopedia
modules = {
    # == AXIS 1: Python Deep Internals ==
    "python/gil.md": r"""# Python GIL & Multiprocessing Internals
### 1. 【エンジニアの定義】Professional Definition
**GIL (Global Interpreter Lock)**: CPythonにおいて、一度に1つのスレッドしかPythonバイトコードを実行できないようにする排他ロック機構。データ処理において、単一プロセス内のマルチスレッド化ではCPUバウンドなタスク（計算処理）がスケールしない根本原因。
### 2. 【0ベース・深掘り解説】Gap Filling
DEが陥る罠：データ変換を速くしようと `concurrent.futures.ThreadPoolExecutor` を導入したが、全く速くならない。これはGILが原因。
解決策：`ProcessPoolExecutor`でマルチプロセス化するか（メモリ消費大）、Pandas/Polarsのように裏側でC/Rustレイヤー等を利用しGILを解放するライブラリを叩くこと。
```mermaid
graph TD
    A[Python Thread 1] -->|Wait| GIL((GIL))
    B[Python Thread 2] -->|Acquire| GIL
    GIL -->|Execute| C[CPU Core 1]
    D[Rust/C Extension] -->|GIL Bypassed| E[CPU Core 2,3,4]
```
""",
    
    "python/memory.md": r"""# Object Memory Layout & Garbage Collection
### 1. 【エンジニアの定義】Professional Definition
Pythonは全てがオブジェクト（PyObject構造体）。整数ひとつでも参照カウント（ob_refcnt）、型情報（ob_type）、値を持つため、C言語の純粋なint(4バイト)に対し、Pythonのintは28バイトを消費する。
### 2. 【0ベース・深掘り解説】Gap Filling
「1億行の数値をリストに入れるとRAMが枯渇する」理由がこれ。Pandas/Numpyが速く省メモリなのは、内部的にPythonオブジェクトではなくC言語の連続したメモリ領域（配列）としてデータを保持しているから。
ガベージコレクション（GC）：主に「参照カウント」でメモリを解放するが、循環参照対策の「世代別GC」が走ると処理が一瞬停止（Stop-The-World）する。バッチ処理の謎のスパイク遅延の犯人。
""",

    # == AXIS 2: Advanced Distributed Systems ==
    "dist/cap.md": r"""# CAP/PACELC Theorem in Modern Data
### 1. 【エンジニアの定義】Professional Definition
**CAP定理**: 分散システムはConsistency（一貫性）、Availability（可用性）、Partition tolerance（分断耐性）のうち2つしか満たせない。
**PACELC定理**: CAPの拡張。P（分断時）はAかCの二者択一だが、E（平常時）でもL（レイテンシ）とC（一貫性）のトレードオフが発生する。
### 2. 【0ベース・深掘り解説】Gap Filling
ADLS（Azure Data Lake）やS3は「最終結果整合性（Eventual Consistency）」を取るシステム。ファイルを上書きした直後に読み込むと、古いファイルが返ってくることがある。Sparkのバッチでこれが起きるとデータ欠損になるため、Delta LakeのようなACIDトランザクション層（Cを保証する層）が必要になる。
```mermaid
graph TD
    A[NoSQL/Obejct Storage] -->|Focus| B[Availability & Partition Tolerance]
    B -->|Trade-off| C[Eventual Consistency]
    D[Delta Lake / RDBMS] -->|Focus| E[Consistency & Partition Tolerance]
    E -->|Trade-off| F[Latency impact]
```
""",

    # == AXIS 3: Spark Deep Dive ==
    "spark/tungsten.md": r"""# Project Tungsten & Memory Management
### 1. 【エンジニアの定義】Professional Definition
**Tungsten**: Spark 1.5から導入された、JVMオブジェクトのオーバーヘッドをバイパスし、メモリ上にバイナリ形式（Unsafe Row）で直接データを配置・計算する内部最適化エンジン。
### 2. 【0ベース・深掘り解説】Gap Filling
JVM（Java仮想マシン）のガベージコレクションはビッグデータの天敵です。数千万のオブジェクトを作るとGCパニックで処理が止まります。
Tungstenは「JVMを通さず、C言語のようにメモリを直接確保・操作（Off-Heap）」し、さらに「Whole-stage Code Generation」でSQLから最適なJavaバイトコードを動的に生成します。これによりSparkは物理的なハードウェア限界に近い速度で動作します。
""",

    "spark/aqe.md": r"""# Adaptive Query Execution (AQE)
### 1. 【エンジニアの定義】Professional Definition
**AQE (適応型クエリ実行)**: Spark 3.0以降の目玉機能。クエリの実行「中」に、完了したステージの実際の統計情報（データ量など）を見て、以降の実行計画を動的に最適化する仕組み。
### 2. 【0ベース・深掘り解説】Gap Filling
「事前計画」の限界：統計情報（CBO）があっても、複雑なフィルタ（例：`like '%hoge%'`）の後のデータ量はSparkには予測不能。結果、大きすぎるパーティションで処理が詰まる（Data Skew）。
AQEは「一度フィルタ結果を見てから、次のJOINの作戦を変える」ことができます。
* **動的結合変更**: Sort-Merge Joinの予定だったが、結果が小さかったので即座にBroadcast Joinに切り替える。
* **動的パーティション結合**: 細かすぎる数千のパーティションを「丁度いいサイズのまとまり」に結合し直す。
* **Skew Join最適化**: 特定の巨大パーティションを分割し、ボトルネックを解消する。
""",

    # == AXIS 4: Advanced Delta & Storage ==
    "storage/parquet.md": r"""# Parquet Internals (Row Group & Bloom Filter)
### 1. 【エンジニアの定義】Professional Definition
**Parquet**: 列指向（Columnar）のファイルフォーマット。データをRow Group単位で分割し、列ごとに圧縮をかけることでスキャン性能を極限まで高める。
### 2. 【0ベース・深掘り解説】Gap Filling
なぜParquetは速いのか？クエリで `select age from users` としたとき、CSVなら全データを読みますが、Parquetなら「age列」のブロックだけをディスクから取得します（**Column Projection**）。
さらに「1〜10万行目のageの最小値は20、最大値は50」という統計情報を持っているため、`age = 60` を探す場合、そのブロックを一切読まずにスキップします（**Predicate Pushdown**）。
ここにブルームフィルタ（Bloom Filter: 確率的データ構造）を組み合わせることで、不要なディスクI/Oを99%削減できます。
""",

    "storage/zorder.md": r"""# Z-Ordering & OPTIMIZE
### 1. 【エンジニアの定義】Professional Definition
**Z-Ordering**: 多次元データを1次元空間にマッピングするアルゴリズム（Z階数曲線）を用いて、指定した複数カラムで一緒に問い合わせされるデータが、物理的に同じファイル内へ配置されるようソートする技術。
### 2. 【0ベース・深掘り解説】Gap Filling
「パーティショニング（フォルダ分割）」は強力ですが、年月日（year=2026/month=04...）などのカーディナリティ（種類）が適度なものにしか使えません。「ユーザーID」でパーティション分割するとフォルダが数億個でき、システムが崩壊します。
しかし「ユーザーID」でよく検索する。どうするか？
`OPTIMIZE table ZORDER BY (user_id)` を実行すると、Delta Lakeは裏側の数千のParquetファイルを読み直し、「近いユーザーID」が同じファイルにまとまるように詰め替えます。結果、前述のPredicate Pushdownが極限まで効くようになり、1時間のクエリが1秒で終わります。
""",

    # == AXIS 5: Databricks Operations ==
    "databricks/photon.md": r"""# Photon Engine
### 1. 【エンジニアの定義】Professional Definition
**Photon**: JVM上のSparkの限界を突破するため、DatabricksがC++でフルスクラッチ開発したネイティブベクトル化（Vectorized）クエリエンジン。
### 2. 【0ベース・深掘り解説】Gap Filling
CPUは「SIMD（Single Instruction, Multiple Data）」という、1回の命令で複数の配列データを一気に処理する機能を持っていますが、JVMからはこれがうまく使えません。
PhotonはSparkの「実行計画」をそのまま受け取り、実行処理（JOIN, AGGなど）だけをC++側でSIMDを駆使して爆速処理します。設定のチェックボックスをオンにするだけで、既存のPySpark/SQLコードを書き換えることなく2〜5倍高速化します。
""",

    "databricks/unity_catalog.md": r"""# Unity Catalog & Data Governance
### 1. 【エンジニアの定義】Professional Definition
**Unity Catalog (UC)**: ワークスペースを跨いだ統合ガバナンスソリューション。テーブル、ファイル、MLモデルに対するアクセス権限（ACL）を一元管理し、血統（Lineage）を自動追跡する。
### 2. 【0ベース・深掘り解説】Gap Filling
旧来のHive Metastore時代は「ワークスペースAとBでテーブル権限がバラバラ」「誰がこのテーブル作ったのか分からない」地獄でした。
UCはすべてを階層化します（`catalog.schema.table`）。
最も偉大な機能は「カラムレベルの血統（Lineage）」。`users`テーブルの`email`カラムが、どのETLジョブを経て、どのPower BIのグラフに使われているか、UI上で網の目のようなグラフで完全にトラッキングできます。個人情報削除（GDPR）対応の必須機能です。
""",

    # == AXIS 6: Data Modeling Architecture ==
    "modeling/kimball.md": r"""# Kimball Dimensional Modeling
### 1. 【エンジニアの定義】Professional Definition
**ディメンショナル・モデリング**: 業務プロセスを「測定可能な数値（Fact）」と「その文脈・属性（Dimension）」に分けてモデリングする、DWH設計の事実上の標準。スタースキーマを形成する。
### 2. 【0ベース・深掘り解説】Gap Filling
RDBMSの第3正規化（重複を無くす設計）をデータ分析に持ち込むと、JOINが10個以上発生しクエリが死にます。
分析用DWHでは「誰が(DimUser)、いつ(DimDate)、どこで(DimStore)、何を(DimProduct)買って、金額はいくらだったか(FactSales)」という星型（Star Schema）に設計します。
これにより、BIツール（PowerBI等）が直感的にフィルターをかけやすくなり、エンジニア以外のビジネスユーザーでもSQLライクな分析が可能になります。
""",

    "modeling/scd.md": r"""# Slowly Changing Dimensions (SCD)
### 1. 【エンジニアの定義】Professional Definition
**SCD (ゆっくり変化する次元)**: 顧客の「住所」や商品の「カテゴリ」など、時間が経つと変化するマスタデータをDWHでどう履歴管理するかの設計パターン。Type 1〜6が存在する。
### 2. 【0ベース・深掘り解説】Gap Filling
* **Type 1 (上書き)**: 古い住所を消して新しい住所で上書きする。過去の「東京店での売上」が、引越し後スナップショットを見ると「大阪店での売上」に化けてしまうリスクあり。履歴を追わない場合に使う。
* **Type 2 (行の追加)**: 「レコード有効開始日」と「有効終了日」（+最新フラグ）カラムを持たせ、変化があったら古い行の終了日を〆て、新しい行を追加する。最も標準的な履歴管理。DWHの絶対の基本。
* **Type 3 (列の追加)**: `current_address` と `previous_address` カラムを持たせる。変更は1世代前までしか追えないが、現在の値と過去の値を並べて集計したい時に便利。
""",

    # == AXIS 7: dbt Advanced Mechanics ==
    "dbt/macro_jinja.md": r"""# dbt Macros & Jinja Mastery
### 1. 【エンジニアの定義】Professional Definition
**Jinja**: Pythonのテンプレートエンジン。dbtは単なるSQLではなく、Jinjaを使うことでSQL内に制御構文(for, if)や関数(Macro)を埋め込み、SQLを「プログラミング言語化」する。
### 2. 【0ベース・深掘り解説】Gap Filling
「12ヶ月分の月別カラムをPIVOTで作りたい」。素のSQLなら手書きで12行書きますし、来年になったらバグります。
dbtなら `{% for month in range(1, 13) %}` でSQL文自体をループで自動生成（コンパイル）します。
「複数のテーブルに同じマスキング処理を適用したい」。これをMacroとして定義し `{{ mask_personal_data('email') }}` と呼び出すだけで、変更時はMacroの定義1箇所を直すだけで全テーブルに適用されます。DRY（Don't Repeat Yourself）原則の達成です。
""",

    "dbt/materialization.md": r"""# Custom Materializations & Incremental
### 1. 【エンジニアの定義】Professional Definition
**Materialization**: dbtが書かれた `select` 文をデータベース上で「何として」具現化するか（View, Table, Incremental, Ephemeral等）の戦略。
### 2. 【0ベース・深掘り解説】Gap Filling
毎日100億行のテーブルを `table` （全件洗い替え）で処理していてはコストが破産します。
そこで `incremental` を使います。
`{% if is_incremental() %} where date >= (select max(date) from {{ this }}) {% endif %}`。
この数行を書くだけで、初回の実行時は全件CREATE TABLEし、次回からは「前回以降の差分だけ」をマージ（MERGE INTO等）する賢い処理に勝手に化けます。各DBMSの厄介なMERGE構文の差異を、dbtが吸収してくれるのが非常に強力です。
""",

    # == AXIS 8: Orchestration Deep Dive ==
    "airflow/executors.md": r"""# Airflow Executors (Celery vs Kubernetes)
### 1. 【エンジニアの定義】Professional Definition
**Executor**: Airflowが解釈したDAG内の各タスクを、「どのマシンのどのプロセスで実行するか」を決定する実行エンジン。
### 2. 【0ベース・深掘り解説】Gap Filling
* **LocalExecutor**: Airflowサーバー内でマルチプロセスで動かす。安価だが負荷が高いと死ぬ。
* **CeleryExecutor**: 複数のワーカーノード（別のVM）を用意し、Redis等をキューにしてタスクを投げるタスク分散の王道。ワーカーの維持にお金がかかる。
* **KubernetesExecutor**: タスク1つにつき、K8s上に新しく1つのPodを立ち上げて実行し、終わったらPodを捨てる。実行ごとの環境分離（ライブラリ衝突回避）と、完全なオートスケールが可能。モダンデータスタックにおける究極のオーケストレーション。
""",
    
    # == AXIS 9: Azure Security & Network architecture ==
    "azure/private_link.md": r"""# Azure Private Link & VNet Injection
### 1. 【エンジニアの定義】Professional Definition
**Private Link**: AzureのPaaS（ストレージ等）へのアクセスを、パブリックインターネットを経由せず、自社のVNet内のプライベートIPアドレス経由で安全に行う通信技術。
### 2. 【0ベース・深掘り解説】Gap Filling
金融やエンタープライズの現場では「DBの中身が万が一インターネットを通るのはNG」というコンプライアンス要件があります。
通常、DatabricksからADLS（データレイク）を読むと、通信はデータセンター内のインターネットルーターをかすめます。これを遮断するため、Storage Accountに対してPrivate Endpointを設定し、VNet内（10.0.0.x等）のローカルIPで完全閉域網通信を実現します。
また、Databricks自体（Data Plane）をお客様が管理する既存のセキュアなVNetにデプロイする「VNet Injection」も、エンタープライズDEの必須設計知識です。
""",
    
    # == AXIS 10: Infrastructure as Code & DataOps ==
    "ops/terraform.md": r"""# Terraform for Databricks
### 1. 【エンジニアの定義】Professional Definition
**Infrastructure as Code (IaC)**: インフラ構築をUI上のクリックではなく、HCL形式のコードで自動化・バージョン管理する手法。
### 2. 【0ベース・深掘り解説】Gap Filling
手作業でDatabricksのクラスターを作り、権限を手動で付与していると、別の開発環境や本番環境を作るときに手順ミス（ヒューマンエラー）が確実に発生します。
Terraformを使えば、`databricks_cluster` や `databricks_secret` リソースをコード化し、`terraform apply` を叩くだけで全く同じ環境が数分で再現されます。
クラスタのノードタイプ変更や、特定ユーザーの退職に伴う権限削除なども、GitHub上のコードレビュー（PR）を通じて安全かつ監査可能な形で実行できます。
"""
}

# Add more dummy placeholders for 2000 pages scope
advanced_topics = [
    # Axis 1
    ("python/cython.md", "Cython & C Extensions", "PythonコードをC言語に変換・コンパイルし、GILを回避して極限まで高速化する技術。"),
    ("python/asyncio.md", "AsyncIO in DE", "ネットワークI/O待ち（API呼び出し等）をシングルスレッド上で非同期処理し、同時実行性を高める。"),
    # Axis 2
    ("dist/vector_clocks.md", "Vector Clocks & Consensus", "分散DBにおいて「どのイベントが先だったか」を論理シグネチャで追跡・解決する分散アルゴリズムの基礎。"),
    ("dist/paxos_raft.md", "Paxos & Raft Consensus", "HadoopのZooKeeperなどで使われる、ネットワーク分断時にも「誰がリーダーか」を多数決で決める合意形成アルゴリズム。"),
    # Axis 3
    ("spark/rdd_lineage.md", "RDD Lineage & Fault Tolerance", "Sparkがなぜ安全なのか。ノードが死んだとき、元の操作履歴（Lineage）からデータを失わず部分的に再計算する耐障害メカニズム。"),
    ("spark/cbo.md", "Cost Based Optimizer (CBO)", "SQL最適化において、テーブルごとの「行数」「値の分散」の統計情報（Cost）から、最も軽いJOIN順を導き出す知能。"),
    # Axis 4
    ("storage/iceberg.md", "Apache Iceberg vs Delta vs Hudi", "モダンTable Formatの3大巨頭。メタデータ管理をファイルではなくディレクトリ構造とマニフェストファイルで抽象化する設計思想比較。"),
    # Axis 5
    ("databricks/dlt.md", "Delta Live Tables (DLT)", "データパイプラインを「宣言的（これを作れ）」に定義すれば、Sparkストリーミングの再試行や依存関係を勝手に解決するマネージド基盤。"),
    ("databricks/cluster_sizing.md", "Cluster Sizing Strategy", "計算リソースの最適化。Driverサイズ、Worker数、Photon適用の見極め、Spotインスタンス活用のコスト削減マトリクス。"),
    # Axis 6
    ("modeling/data_vault.md", "Data Vault 2.0", "Hub(ハブ), Link(リンク), Satellite(サテライト)の3構造で、超大規模かつ複数システム由来の「変化し続けるシステム」を柔軟に統合する最新モデリング。"),
    ("modeling/obt.md", "One Big Table (OBT)", "JOINを避けるため、クエリ前に全てのDimensionを結合済みの超巨大「1枚の平べったい表」を作る現代DWHの力技最適化。"),
    # Axis 7
    ("dbt/ci_cd.md", "dbt CI/CD Implementation", "GitHub Actions等で「PR時にプレビュー環境DBでdbt runを試走させ、テストが通ってはじめてマージできる」ようにするDevOps運用。"),
    # Axis 8
    ("airflow/kafka.md", "Apache Kafka Architecture", "非同期イベントストリーミング。Topic, Partition, Offset, Consumer Groupによる圧倒的な再送可能メッセージング基盤。"),
    # Axis 9
    ("azure/managed_identities.md", "Managed Identities & Service Principals", "キーローテーションの悪夢を防ぐ。パスワードを持たせず、Azureリソース（VMやADF）自体にEntra ID（AAD）でのアイデンティティを持たせ、認証をパスする。"),
    # Axis 10
    ("ops/data_observability.md", "Data Observability (Monte Carlo)", "「何かおかしい」を検知する。データパイプラインの鮮度、ボリューム、スキーマ変更、異常値などを機械学習で自動監視し、ダッシュボードが壊れる前にアラートを出す運用。")
]

for filepath, title, desc in advanced_topics:
    modules[filepath] = f"""# {title}
### 1. 【エンジニアの定義】Professional Definition
> **{title}**: 高度なデータエンジニアリング及び分散システム設計において、システムのスケール、信頼性、モデラビリティを担保するためのコア概念。
### 2. 【0ベース・深掘り解説】Gap Filling
{desc}
*(※ 2000ページ級の完全な内容構築に向け、当モジュールの詳細コンテンツを後続の学習で書き込みます。)*
"""

for filepath, content in modules.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated {len(modules)} massive scope modules.")

# Now recreate the js manifest dynamically combining OLD and NEW axes
import glob

axes_structure = [
    {"title": "01. Python Core & Process Internals", "filter": "python/"},
    {"title": "02. PySpark Master Class", "filter": "pyspark/"},
    {"title": "03. Spark Internal Engines", "filter": "spark/"},
    {"title": "04. Lakehouse & Advanced Storage", "filter": "storage/"},
    {"title": "05. Databricks Deep Compute", "filter": "databricks/"},
    {"title": "06. Distributed Systems Theory", "filter": "dist/"},
    {"title": "07. Data Modeling Architecture", "filter": "modeling/"},
    {"title": "08. dbt & ELT Paradigm", "filter": "dbt/"},
    {"title": "09. Orchestration & Event Streaming", "filter": "airflow/"},
    {"title": "10. Azure Security & Network", "filter": "azure/"},
    {"title": "11. DataOps & IaC", "filter": "ops/"},
    {"title": "12. Certifications", "filter": "certifications/"},
    {"title": "13. Projects", "filter": "projects/"}
]

js_path = os.path.join(base_dir, "dashboard_data.js")
axes = []

md_files = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True)
md_files = [f.replace(os.sep, "/") for f in md_files]

id_counter = 1
contents_dict = {}

for ax_idx, axis_def in enumerate(axes_structure, 1):
    axis_obj = {"title": axis_def["title"], "modules": []}
    
    # find files that match the filter directory
    sub_files = [f for f in md_files if f.endswith(".md") and (axis_def["filter"] in f)]
    sub_files.sort()
    
    mod_idx = 1
    for f in sub_files:
        rel_path = f.replace(base_dir.replace(os.sep, "/") + "/", "")
        mod_id = f"V_{ax_idx}.{mod_idx}"
        
        # Read title from first line
        title = "Untitled"
        with open(f, "r", encoding="utf-8") as file:
            first_line = file.readline().strip()
            if first_line.startswith("# "):
                title = first_line[2:]
            file.seek(0)
            contents_dict[mod_id] = file.read()
            
        axis_obj["modules"].append({
            "id": mod_id,
            "title": title,
            "path": rel_path
        })
        mod_idx += 1
        
    if axis_obj["modules"]:
        axes.append(axis_obj)


js_content = "const studyData = {\n"
js_content += '    title: "DATA ENGINEERING",\n'
js_content += '    subtitle: "2000-page Encyclopedia (As-Is to To-Be)",\n'
js_content += '    localStorageKey: "study17_encyclopedia_progress",\n'
js_content += '    themeColor: "#9333ea",\n' # Purple for ultimate
js_content += '    secondaryColor: "#eab308",\n' # Yellow
js_content += '    axes: ' + json.dumps(axes, ensure_ascii=False, indent=4) + '\n};\n\n'
js_content += 'window.moduleContents = ' + json.dumps(contents_dict, ensure_ascii=False, indent=2) + ';\n'

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Bake complete. Packed into Encyclopedia. Axes: {len(axes)}.")
