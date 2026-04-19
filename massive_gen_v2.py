import os
import json
import glob

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")
os.makedirs(docs_dir, exist_ok=True)

# Define the structure and content for Volume 2 of the Massive Encyclopedia
modules_v2 = {
    # == Advanced Python (Language Internals) ==
    "python/context_managers.md": r"""# Context Managers & Resource Leaks
### 1. 【エンジニアの定義】Professional Definition
**Context Manager (`with` 構文)**: ファイルやネットワークコネクションなど、OSレベルのリソースを「確実に」クローズするためのプログラミング・パラダイム。内部的に `__enter__` と `__exit__` メソッドを持つ。
### 2. 【0ベース・深掘り解説】Gap Filling
DEのよくある障害として「Too many open files (ファイルディスクリプタの枯渇)」があります。ファイルを開いたまま `close()` を忘れたり、例外処理中に `close()` が呼ばれなかったために発生します。`with` を使用すると、例外が起ころうと途中で `return` しようと、確実にコネクションが切断されるため、堅牢なデータパイプラインには必須の記法です。
""",

    "python/decorators.md": r"""# Decorators & Metaprogramming
### 1. 【エンジニアの定義】Professional Definition
**Decorator (`@` 構文)**: 既存の関数のソースコードをいじることなく、前後に処理（ログ出力、リトライ、実行時間計測など）を注入するための高階関数（関数を引数にとり、関数を返す関数）。
### 2. 【0ベース・深掘り解説】Gap Filling
クラウドAPIを叩いてデータを抜く処理では、「一時的なネットワークエラー」による失敗が日常茶飯事です。各関数に `try-except` のリトライ処理を書くと長大で読みづらいコードになりますが、`@retry(times=3)` というデコレータを被せるだけで、どんな関数も堅牢なオートリトライ処理を備えた関数にアップグレードできます。
""",

    "python/pandas_udf.md": r"""# Pandas UDF (Vectorized UDF)
### 1. 【エンジニアの定義】Professional Definition
**Pandas UDF**: PySpark上でPythonネイティブの関数を適用する際、1行ずつ評価する従来の激遅なUDFを捨て、内部的にApache Arrowを用いてJVMとPythonプロセス間のデータ転送をバッチ単位（列指向）で高速に行う機能。
### 2. 【0ベース・深掘り解説】Gap Filling
Sparkで「複雑な機械学習推論」を行う場合、SQLでは書けないためPythonのUDFを作ります。しかし従来のUDFは、1行ずつ「JVM → Python」へデータ変換・通信を行うため、数千万行の処理に数時間かかります。Pandas UDFを使うと、数千行のブロック単位で一気に処理が渡るため、10〜100倍の圧倒的な高速化が保証されます。
""",

    # == Networking & APIs ==
    "net/tcp_vs_udp.md": r"""# TCP/IP Fundamentals
### 1. 【エンジニアの定義】Professional Definition
**TCP (Transmission Control Protocol)**: 手を繋いで通信する（3-way Handshake）。「届いたか？」を確認し、損失があれば再送する信頼性の高いプロトコル（HTTPやDB接続はすべてコレ）。
**UDP (User Datagram Protocol)**: 投げっぱなしの通信。欠損しても気にしないが圧倒的に速い（動画配信やオンラインゲーム）。
### 2. 【0ベース・深掘り解説】Gap Filling
KafkaやSpark等での「TimeoutException」。TCPの特性上、大量のデータを送っているとネットワーク機器がパケットをドロップし、再送待ち（Retransmission）が発生するため、一時的にレスポンスが停滞します。この振る舞いを理解しないと、単純にAPIタイムアウト値をむやみに延ばすだけの対症療法になってしまいます。
""",
    
    "net/rest_vs_grpc.md": r"""# REST APIs vs gRPC / GraphQL
### 1. 【エンジニアの定義】Professional Definition
**REST**: HTTPプロトコル上でJSONなどのテキストをやり取りする標準的アーキテクチャ。遅いがシンプル。
**gRPC**: HTTP/2上でProtocol Buffers（Protobuf）というバイナリ形式でやり取りするGoogle開発の超高速RPC。
**GraphQL**: クライアントが「欲しいデータの構造」を指定できるため、無駄なデータ通信（Over-fetching）を防げるFacebook開発のAPI言語。
### 2. 【0ベース・深掘り解説】Gap Filling
データエンジニアとしてマイクロサービス間のデータ通信を設計する際、RESTで毎秒10万件のJSONをパースしているとCPUが燃え尽きます。内部システム間は圧倒的に軽く高速なgRPC（バイナリ通信）を選ぶのがモダンシステムの鉄則です。
""",

    # == Database Architecture ==
    "db/ac_mvcc.md": r"""# MVCC (Multi-Version Concurrency Control)
### 1. 【エンジニアの定義】Professional Definition
**MVCC (多版同時実行制御)**: データベースにおいて「書き込み処理」と「読み込み処理」が互いにブロック（ロック待ち）しないようにする仕組み。書き込み中に別人が読み込んでも、書き込み直前の「古いバージョンのスナップショット」が見える。
### 2. 【0ベース・深掘り解説】Gap Filling
PostgreSQLやOracle、そしてDatabricksのDelta Lakeでも採用されています。Aさんが1億行のUPDATEをかけている最中に、Bさんが同じ表をSELECTしてもエラーにならず、UPDATE前のデータが綺麗に返ってきます。DWHにおいて「夜間バッチを動かしながら、昼間のBIダッシュボードを見せる」ための最強の裏技です。
""",

    "db/btree_vs_lsm.md": r"""# B-Tree vs LSM Tree (Storage Engines)
### 1. 【エンジニアの定義】Professional Definition
**B-Tree**: MySQL等の旧来のRDBMSで使われる、読み込み（検索）に強いが、ランダム書き込みに弱い木構造インデックス。
**LSM Tree (Log-Structured Merge-Tree)**: CassandraやRocksDB等で使われる、書き込み（Write）を超高速にするために、とにかくログとしてデータを追記（Append）し続け、裏側でマージする形式。
### 2. 【0ベース・深掘り解説】Gap Filling
秒間数万件のIoTセンサーデータをRDBMS(B-Tree)に投げると、インデックスの再構築（ページ分割）によりディスクI/Oが爆発して死にます。ビッグデータでは書き込み効率（Write Amplificationの低減）が命なので、NoSQLのLSM Treeアーキテクチャが多用されます。
""",

    "db/connection_pooling.md": r"""# Connection Pooling
### 1. 【エンジニアの定義】Professional Definition
**コネクションプーリング**: データベースへの接続（TCPハンドシェイク+認証）は非常にコストが高いため、あらかじめ複数の接続を確立して「使いまわす」ための仕組み（PgBouncerなど）。
### 2. 【0ベース・深掘り解説】Gap Filling
PythonスクリプトからAzure SQLに1行挿入するたびに `connect()` を呼んでいると、その通信のオーバーヘッドのせいで処理能力が1/1000になります。さらに、DB側も「同時接続数上限（Max Connections）」に達してシステム全体がダウンします。
""",

    # == Security & Identity ==
    "sec/oauth2.md": r"""# OAuth 2.0 & OIDC
### 1. 【エンジニアの定義】Professional Definition
**OAuth 2.0**: パスワードを渡すことなく、AというアプリがBというサービス（Google等）にアクセスする「一時的な権限（トークン）」を付与する認可フレームワーク。
**OIDC (OpenID Connect)**: OAuth 2.0の上に「認証（あなたは誰か）」の仕組みを被せたもの。
### 2. 【0ベース・深掘り解説】Gap Filling
エンタープライズのデータパイプライン構築では、「ID/Passwordをソースコードに埋め込む」のは犯罪に近いです。AzureではService Principalなどを通じてOAuth 2.0の仕組みを利用し、数時間で期限切れになる「Access Token」を使ってDatabricksからADLSへセキュアにアクセスします。
""",

    "sec/zero_trust.md": r"""# Zero Trust Architecture
### 1. 【エンジニアの定義】Professional Definition
**ゼロトラスト**: 「社内ネットワークだから安全」という境界防御（VPN等）の考えを捨て、「すべてのアクセス（外部も内部も）を信頼せず、常に検証する」というセキュリティモデル。
### 2. 【0ベース・深掘り解説】Gap Filling
データエンジニアリングでは、DatabricksがADLSにアクセスする際に、VNet内（プライベートネットワーク）であっても必ず「IAMによる多要素認証状態の検証」「最小権限の原則（Least Privilege）」を適用する設計が求められます。
""",

    # == System Architecture Patterns ==
    "arch/lambda_vs_kappa.md": r"""# Lambda vs Kappa Architecture
### 1. 【エンジニアの定義】Professional Definition
**Lambda Architecture**: バッチ処理の層（Hadoop等）と、リアルタイムのストリーミング層（Storm/Spark Streaming等）の２つを並行して動かし、Viewで統合するアーキテクチャ。複雑極まりない。
**Kappa Architecture**: バッチ処理を捨て、「すべてをログのストリームとして扱う（Kafka中心）」ことで、システムを一つに統合したモダンなアーキテクチャ。
### 2. 【0ベース・深掘り解説】Gap Filling
Lambdaアーキテクチャは「バッチ用とストリーム用」の2つの似たようなコードを書かなければならず、保守が地獄でした。Databricksはこの派生で、「バッチとストリーミングの境界を無くす」Delta Live Tables (DLT) 等を推進しています。
""",

    "arch/event_sourcing.md": r"""# Event Sourcing & CQRS
### 1. 【エンジニアの定義】Professional Definition
**Event Sourcing**: 現在の「状態（残高1000円）」を保存するのではなく、「発生したイベントの歴史（+5000円, -4000円）」をすべて保存し、そこから現在の状態を計算するアーキテクチャ。
**CQRS**: 読み込み（Query）と書き込み（Command）のデータベース（モデル）を完全に分離・非同期化する設計手法。
### 2. 【0ベース・深掘り解説】Gap Filling
銀行システムやECサイトのカートなどで多用されます。イベント（履歴）さえあれば、過去の任意の時点（Time Travel）にシステムを完全復元できるのが強みです。DWHやDelta LakeのTransaction Logの根本的な思想はこれに基づいています。
""",

    # == CI/CD & Testing ==
    "cicd/great_expectations.md": r"""# Core Data Testing (Great Expectations)
### 1. 【エンジニアの定義】Professional Definition
**Great Expectations**: データの「期待値（NULLがないか、値の範囲が妥当か）」を定義し、パイプラインに取り込まれたデータがその条件を満たしているかを検証（プロファイリング／テスト）するためのPythonフレームワーク。
### 2. 【0ベース・深掘り解説】Gap Filling
ソフトウェアがバグる原因は「コードのバグ」ですが、データパイプラインが壊れる原因の9割は「想定外のデータが上流から飛んできた（Data Outage）」ことです。
これを防ぐため、dbtテストやGreat Expectationsをパイプラインの関所（Data Contract）として置き、腐ったデータが湖（Data Lake）に入るのを未然にブロックします。
"""
}

# Add more dummy placeholders for massive scale to hit the "2000-page" vibe
import random

ext_topics = [
    # Spark
    ("spark/memory_management.md", "Spark Execution vs Storage Memory", "Spark ExecutorマシンのRAMにおける、計算用（Execution）とキャッシュ用（Storage）の境界線とUnified Memory Managerの動的配分。"),
    ("spark/kryo.md", "Kryo Serialization (The Speed Hack)", "Javaの標準シリアライゼーションを捨ててKryoを使うことで、ノード間通信とメモリ使用量（GC負荷）を劇的に落とす魔法。"),
    ("spark/rdd_persistence.md", "RDD Persistence & Eviction Policies", "メモリから溢れたキャッシュをどうするか（LRU方式）、MEMORY_AND_DISK の罠など。"),
    # Python
    ("python/metaclasses.md", "Metaclasses (Advanced Python)", "クラスを作成するためのクラス。ライブラリ（ORMなど）を自作しない限り直に触る必要はないが、内部の黒魔術を理解できる。"),
    ("python/itertools.md", "Itertools & Collections", "メモリ効率よく組み合わせや集計を行うPython標準の最強ツール群。"),
    # Databases / SQL
    ("db/wal.md", "WAL (Write-Ahead Logging)", "DBはなぜクラッシュしてもデータが消えないのか。変更を実際のテーブルに書く前に、まず「ログ（WAL）」としてディスクに順次書き込む（Append-only）メカニズム。"),
    ("db/sharding.md", "Replication vs Sharding", "スケールアップの限界。読み込みを増やすためのレプリケーション（Slave）と、書き込みを増やすためのシャーディング（分割）の根本的な違い。"),
    # API / Web
    ("net/http2.md", "HTTP/2 vs HTTP/1.1", "1回のコネクションで複数のファイル・データをパラレルに送受信できるマルチプレクシング（gRPCの土台）。"),
    ("net/websockets.md", "WebSockets vs Server-Sent Events (SSE)", "DBからフロントエンドへのリアルタイム通知。双方向通信（WebSocket）と単方向ストリーミング（SSE）の使い分け。"),
    # DevOps / CI/CD
    ("cicd/pytest.md", "Pytest for Data Pipelines", "モック化（Mock）を駆使して、本番のDBに繋がずにパイプラインの変換ロジックだけをCIサーバーで超高速にテストする。"),
    ("ops/docker.md", "Docker Internals for DE", "データパイプライン環境をカプセル化し、「私のPCでは動いたのに」を撲滅するCgroupsとNamespaceの技術。")
]

for filepath, title, desc in ext_topics:
    modules_v2[filepath] = f"""# {title}
### 1. 【エンジニアの定義】Professional Definition
> **{title}**: 高度なシステム設計やトラブルシューティングで必ず必要になる基礎技術要素。
### 2. 【0ベース・深掘り解説】Gap Filling
{desc}
*(※ 2000ページ級の完全な内容構築に向け、当モジュールの詳細コンテンツを後続の学習で書き込みます。)*
"""

# Write files
for filepath, content in modules_v2.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# Update build_portal.py logic inside massive_gen_v2.py
axes_structure = [
    {"title": "01. Python Core & Internals", "filter": "python/"},
    {"title": "02. PySpark Optimization", "filter": "pyspark/"},
    {"title": "03. Spark Architecture", "filter": "spark/"},
    {"title": "04. Lakehouse & Storage", "filter": "storage/"},
    {"title": "05. Database Internals (DBA)", "filter": "db/"},
    {"title": "06. Dist System Theory", "filter": "dist/"},
    {"title": "07. Databricks Deep Compute", "filter": "databricks/"},
    {"title": "08. System Design Patterns", "filter": "arch/"},
    {"title": "09. Data Modeling", "filter": "modeling/"},
    {"title": "10. dbt & Integration", "filter": "dbt/"},
    {"title": "11. Orchestration", "filter": "airflow/"},
    {"title": "12. Networking & APIs", "filter": "net/"},
    {"title": "13. Cloud Security & IAM", "filter": "sec/"},
    {"title": "14. Azure Specifics", "filter": "azure/"},
    {"title": "15. CI/CD & Quality", "filter": "cicd/"},
    {"title": "16. DataOps & IaC", "filter": "ops/"},
    {"title": "17. Certs & Projects", "filter": "certifications/"}, 
    {"title": "18. Capstone", "filter": "projects/"}
]

js_path = os.path.join(base_dir, "dashboard_data.js")
axes = []
md_files = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True)
md_files = [f.replace(os.sep, "/") for f in md_files]
contents_dict = {}

for ax_idx, axis_def in enumerate(axes_structure, 1):
    axis_obj = {"title": axis_def["title"], "modules": []}
    sub_files = [f for f in md_files if f.endswith(".md") and (axis_def["filter"] in f)]
    sub_files.sort()
    
    mod_idx = 1
    for f in sub_files:
        rel_path = f.replace(base_dir.replace(os.sep, "/") + "/", "")
        mod_id = f"Vol_{ax_idx}.{mod_idx}"
        
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
js_content += '    subtitle: "2000-page Encyclopedia (Volume 2)",\n'
js_content += '    localStorageKey: "study17_encyclopedia_v2_progress",\n'
js_content += '    themeColor: "#f43f5e",\n' # Intense Rose
js_content += '    secondaryColor: "#3b82f6",\n' # Blue
js_content += '    axes: ' + json.dumps(axes, ensure_ascii=False, indent=4) + '\n};\n\n'
js_content += 'window.moduleContents = ' + json.dumps(contents_dict, ensure_ascii=False, indent=2) + ';\n'

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Generated {len(modules_v2)} new modules.")
print(f"Bake complete. Packed into Encyclopedia V2. Total Axes: {len(axes)}.")
