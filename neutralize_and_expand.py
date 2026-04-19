import os
import json
import glob
import re

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")
os.makedirs(docs_dir, exist_ok=True)

# --------------------------------------------------------------------------
# 重厚な粒度かつ特定の社名を完全に排除した中立なプロフェッショナル解説
# --------------------------------------------------------------------------

content_v5 = {
    "databricks/roi_photon_deep.md": r"""# Databricks ROI Optimization & Photon Internals
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「スケールアウト」への過信とコストの罠**
データ基盤におけるパフォーマンス問題に対し、安易にノード数（Worker）を増やすアプローチは、クラウド破産の典型的なアンチパターンです。
Sparkの分散処理において、特定のノードにデータが集中する（Data Skew）、あるいはシャッフル時のネットワーク帯域がボトルネックとなっている場合、CPUコアをいくら増やしても処理時間はスケーラビリティの限界（アムダールの法則）に直面し、DBUコストのみが指数関数的に増大します。
真のROI最適化とは、ワークロード特性（CPUバウンドかI/Oバウンドか）をSpark UIの実行計画（DAG）とメトリクスから定量的に特定し、「スケールアウト（台数増）」ではなく「スケールアップ（インスタンスタイプの最適化）」や「コンピュートエンジンの切り替え（Photon化）」を適材適所で判断することにあります。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**JVMのオーバーヘッドとベクトル化エンジン（Photon）のC++層**
従来のApache SparkはJava Virtual Machine (JVM) 上で動作します。データを行（Row）単位で処理するアーキテクチャであるため、1つの演算（例: a + b）ごとに仮想メソッドの呼び出し、条件分岐、そして大量の中間オブジェクトの生成とガベージコレクション（GC）の停止（Stop-the-World）が発生します。
これに対し、PhotonエンジンはSparkの物理実行計画をC++で記述されたネイティブエンジンにプッシュダウンします。ここでは「SIMD (Single Instruction, Multiple Data)」というCPUのハードウェア機能を直接叩く「ベクトル化処理」が行われます。

1. **カラム単位のバッチ処理**: 各カラムのデータを連続したメモリ領域（アレイ）に展開。
2. **命令キャッシュ（L1/L2 Cache）の最適化**: ループ処理においてCPUの分岐予測ミスを極限まで減らし、キャッシュヒット率を飛躍的に向上。
3. **ゼロ仮想関数オーバーヘッド**: 動的ディスパッチを排除し、静的にコンパイルされたパイプラインで一気に処理を貫通。

```mermaid
graph TD
    classDef spark fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef photon fill:#312e81,stroke:#8b5cf6,stroke-width:2px;
    
    subgraph "Legacy Row-at-a-time (JVM)"
        A[Read Row 1]:::spark --> B[Virtual Call: Add]:::spark
        B --> C[Generate Object / CPU Cache Miss]:::spark
        C --> D[Read Row 2...]:::spark
    end
    
    subgraph "Vectorized Execution (Photon C++)"
        E[Load Array of 1024 INTs to SIMD Register]:::photon --> F[Execute Single CPU Instruction (ADD)]:::photon
        F --> G[Write 1024 INTs Array without GC]:::photon
    end
```

### 3. 【実務への応用】Practical Application
* **Photonの有効化基準**:
  * **推奨**: JOINキーのハッシュ計算、大規模な `GROUP BY` に伴うハッシュ集計、複雑な正規表現（RegEx）パース、および浮動小数点演算を多用するCPUバウンドなジョブ。処理時間が半分になれば、PhotonのプレミアムDBUコストを払っても総コスト（ROI）は劇的に改善します。
  * **非推奨**: S3からの単純なデータダウンロードや、小規模なデータフィルタリングのみを行うI/Oバウンドなジョブ。CPUがストレージの応答を待っている間も高いDBUを消費し続けるため、コストだけが悪化します。
* **メモリ最適化**:
  * Photonはヒープ外メモリ（Off-Heap Memory）を多用します。Photonを有効にする場合は、メモリ最適化インスタンス（Azureの場合は `E` シリーズなど）を選択し、Sparkの `spark.memory.offHeap.size` などを自律的に管理させる設定が不可欠です。
""",

    "modeling/kimball_vs_datavault.md": r"""# Lakehouse Modeling: Kimball vs Data Vault 2.0
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「ビジネスの変更」がDWHを破壊する歴史的な問題**
従来のデータウェアハウス設計におけるデファクトスタンダードである「ディメンショナル・モデリング（Kimballスタースキーマ）」は、BIツールからの検索パフォーマンスに特化しています。
しかし、新しい取引先システムが追加されたり、業務プロセスが根底から変化した場合、既存のFact（事実）およびDimension（属性）のスキーマを直接ALTER（書き換え）し、過去データをマイグレーションする膨大な工数が発生します。この「変化に対する脆さ」と「ベンダーロックインされたレガシーETL」を脱却し、クラウドスケールのLakehouseにおける俊敏性（Agility）を獲得するために考案されたのが Data Vault 2.0 です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**ハッシュベースの疎結合アーキテクチャ (Hub, Link, Satellite)**
Data Vault 2.0では、データシステムを以下の3要素に完全に分離します。
1. **Hub (ハブ)**: ビジネスキー（例: eメール、UUID、口座番号）の不変リスト。格納されるのは Business Key と、それをMD5またはSHA-1でハッシュ化したハッシュキー（Hash Key）、およびデータ到着日時とソース元情報のみ。属性は一切持ちません。
2. **Link (リンク)**: 複数のHub間の関係性（トランザクションなど）を表します。各Hubのハッシュキーを持ち、関係そのものを不変の事実として記録します。
3. **Satellite (サテライト)**: HubまたはLinkに関する変化する「属性情報（名前、価格、住所など）」を履歴として保持します。データの更新（SCD Type 2）はすべてここで行われます。

これにより、新しいシステム（CRM Bなど）が追加導入された場合、既存のテーブル設計を一切変更することなく、「新しいSatellite」を元のHubにぶら下げる（Additive Change）だけで拡張が完了します。
分散処理（Sparkなど）においては、ビジネスキーをハッシュキー化しておくことで、ロード処理同士のロック待ち（依存関係）を排除し、全テーブルをパラレル（並行）で超高速ロードできるという極めて実践的なメリットがあります。

```mermaid
erDiagram
    HUB_CUSTOMER {
        char(32) HK_CUSTOMER PK "MD5 Hash of Business Key"
        varchar BUSINESS_KEY "e.g., Email or Ext ID"
        timestamp LOAD_DATE
    }
    SAT_CUST_CRM_A {
        char(32) HK_CUSTOMER FK
        timestamp LOAD_DATE PK
        varchar FULL_NAME
        varchar ADDRESS
    }
    SAT_CUST_BILLING_B {
         char(32) HK_CUSTOMER FK
         timestamp LOAD_DATE PK
         varchar CREDIT_SCORE
    }
    
    HUB_CUSTOMER ||--o{ SAT_CUST_CRM_A : "Has Context (Sys A)"
    HUB_CUSTOMER ||--o{ SAT_CUST_BILLING_B : "Has Context (Sys B)"
```

### 3. 【実務への応用】Practical Application
* **情報マート層（Data Mart Layer）への変換**:
  * Data Vaultは「柔軟な取り込みと履歴の保存」には最強ですが、結合（JOIN）の数が指数関数的に増えるため、分析ユーザーやBIツールが直接クエリを叩くのには向いていません（クエリパフォーマンスが悪化）。
  * したがって実務では、Raw Data（Bronze層）から Data Vault（Silver層）へ並列統合し、最後に集計パイプラインを回してBI向けに Kimball の Star Schema（Gold層）ビューを生成する「2段階アプローチ」が必須アーキテクチャとなります。
* **遅延到着データの処理**:
  * トランザクションシステムの障害で、順番が逆転して古い更新履歴が遅れてLakehouseに到着した場合でも、Satelliteは単なるInsert-Onlyな追記モデルであるため、ロードエラーを起こさず、後段の集計ロジックで安全に時系列順に再構築（PIT: Point-in-Time Table の活用）できます。
""",

    "spark/streaming_checkpoints.md": r"""# Structured Streaming & Fault Tolerance Mechanics
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「マイクロバッチの中断と再開」における一貫性の担保**
毎秒数万件のセンサーデータやアクセスログをKafkaやEvent Hubsからリアルタイムに取り込むデータエンジニアリングにおいて、「ノード障害（クラッシュ）」は例外的な事象ではなく、日常的な設計前提として組み込まれなければなりません。
クラッシュ時にストリーム処理を再起動した際、単に「どこまで読んだか」を記録するだけでは、「データを重複して処理してしまう（At-least-onceの罠）」または「途中のデータを読み飛ばしてしまう（At-most-onceの罠）」問題が発生します。
エンタープライズが要求する「確実に1回だけ処理される（Exactly-Once Semantics）」を実現するため、Spark Structured Streamingは「ソース側の確実なリプレイ機能」と「シンク側のトランザクション管理」をチェックポイント（Checkpointing）と先行書き込みログ（WAL）で結びつけています。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Checkpointing, WAL, and Exactly-Once Semantics**
SparkのExactly-once保証は、以下の精密な協調動作によって成り立ちます。

1. **オフセットログ (Offset Log)**:
   各マイクロバッチの処理を開始する「前」に、Spark Driverは対象となるメッセージ範囲（例: KafkaのトピックA、パーティション0、オフセット1000〜1500）をクラウドストレージのチェックポイントディレクトリにある `offsets` サブフォルダへ JSON として書き留めます。
2. **実行 (Execution) と 状態保存 (State Store)**:
   ストリーム集計（例えば過去1時間のウィンドウ集計）を行う場合、これまでの集計結果（中間状態）をメモリ上ではなく、HDFS互換ストレージ（Deltaなど）上の `state` フォルダに永続化させながら処理を進めます。
3. **コミットログ (Commit Log)**:
   Sink（例えばDelta Tableへの書き込み）が正常に完了した直後、Driverは `commits` サブフォルダに行き「バッチID 42 は完全に完了した」というログを書き込みます。

この厳格なシーケンスにより、もしジョブがクラッシュした場合、システムは以下のリカバリ判断を自律的に下します：
- `offsets` には手掛かりがあるが、`commits` に記録がない場合：処理中に死んだと判断し、保存された全く同じオフセット範囲をKafkaから再取得し、全く同じバッチ（再計算）を実行する。
- Target Sinkが冪等（Idempotent：何度同じデータを流しても結果が同じ）な設計であれば、書き込みが重複することなく完全な復旧を遂げます。

```mermaid
sequenceDiagram
    participant Source as Event Broker (e.g. Kafka)
    participant Driver as Spark Driver
    participant CP as Object Storage (Checkpoint)
    participant Sink as Destination (Delta Lake)

    Driver->>Source: Poll latest offsets (e.g., 500-1000)
    Driver->>CP: Write Offset Log (Batch 11: 500-1000)
    Note over Driver, CP: --- 障害発生ポイント 1 ---
    Driver->>Driver: Process Data (Transformations)
    Driver->>Sink: Attempt Write to Sink
    Note over Driver, Sink: --- 障害発生ポイント 2 ---
    Sink-->>Driver: Write Acknowledged
    Driver->>CP: Write Commit Log (Batch 11 COMPLETE)
```

### 3. 【実務への応用】Practical Application
* **チェックポイント・ディレクトリの物理分離**:
  チェックポイントの場所を、出力先のテーブルと同じ階層に置くのは運用上のアンチパターンです。ストレージが満杯になったり、意図せず削除された際のブラスト半径（被害範囲）を分けるため、専用のセキュアなADLSコンテナなどに分離すべきです。
* **スキーマ進化とトポロジ変更の罠**:
  コードを修正し、`groupBy()` の条件キーを増やしたり減らしたり（集計トポロジの変更）してデプロイすると、以前のチェックポイントの状態（State）と互換性がなくなり、起動時に復旧に失敗します。この場合、ストリーミングジョブのビジネス要件上「過去の状態を引き継ぐ必要がない」のであれば、チェックポイントディレクトリを新規作成し、Kafkaの最初または最新のオフセットからクリーンスタートする運用設計が必要です。
"""
}

# Overwrite VIP files with neutralized, massive depth content.
for filepath, content in content_v5.items():
    full_path = os.path.join(docs_dir, filepath)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# --------------------------------------------------------------------------
# SCRUB ANY EXISTING REFERENCES TO KAZANEYA
# --------------------------------------------------------------------------
bad_words = ["Kazaneya", "KAZANEYA", "Kanazeya", "KAZ", "KANAZEYA", "kanazeya", "kazaneya"]

def neutralize_text(text):
    for w in bad_words:
        # replace with neutral professional terms
        if w.isupper():
            text = text.replace(w, "EXPERT")
        elif w.istitle():
            text = text.replace(w, "Advanced")
        else:
            text = text.replace(w, "advanced")
    return text

# Scrub all MD files
md_files = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True)
for f in md_files:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
    
    n_content = neutralize_text(content)
    if n_content != content:
        with open(f, "w", encoding="utf-8") as file:
            file.write(n_content)

# Scrub HTML file just in case
html_path = os.path.join(base_dir, "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

n_html = neutralize_text(html_content)
if n_html != html_content:
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(n_html)

# --------------------------------------------------------------------------
# Bundle Everything into JS using Neutral Axis names
# --------------------------------------------------------------------------
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

js_path = os.path.join(base_dir, "dashboard_data.js")
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
    return axis_obj

# Featured Axis
featured_axis = {"title": "00. EXPERT SPECIALS", "modules": []}
m_idx = 1
for f_path in featured_paths:
    full_p = os.path.join(base_dir, f_path)
    if os.path.exists(full_p):
        with open(full_p, "r", encoding="utf-8") as file:
            title = file.readline().strip()[2:]
            file.seek(0)
            contents_dict[f"VIP.0.{m_idx}"] = file.read()
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

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Workflow Executed. Regenerated deep VIP files, scrubbed all proprietary labels, and rebuilt the dashboard data.")
