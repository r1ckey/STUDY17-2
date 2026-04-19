import os
import json
import glob
import re

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")
os.makedirs(docs_dir, exist_ok=True)

# --------------------------------------------------------------------------
# Step 1-5: Brainstorming -> Research -> Prose -> Mermaid -> Architect Review
# Applying "Kazaneya Style" (Mechanism of Problems -> Practical Application)
# --------------------------------------------------------------------------

content_v4 = {
    # 1. ROI Optimization / Photon
    "databricks/roi_photon_deep.md": r"""# Databricks ROI Optimization & Photon Internals
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「とりあえずWorker数を増やせば速くなる」という幻想**
データエンジニア初心者が陥りがちなのが、Sparkジョブが遅いときに「クラスタのノード数を倍にする」という力技です。しかし、これがOOM（メモリ不足エラー）やData Skew（データの偏り）に起因する場合、ノードをいくら増やしても解決せず、クラウドの請求額（DBUコスト）だけが指数関数的に増大します。
真のROI最適化は、「どこでCPU/メモリ時間を浪費しているか」を読み解き、適切なインスタンスタイプの選択やPhotonエンジンの有効化を行うことです。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**JVMのオーバーヘッドとPhotonのC++ベクタ化**
SparkはJava仮想マシン(JVM)の上で動作します。JVMは、数十億行のデータを1行ずつ処理することには向いていません（オブジェクト生成のオーバーヘッドとGC停止が多発するため）。
Photonエンジンを有効化すると、Sparkの物理実行計画がフックされ、JVMをバイパスしてネイティブなC++レイヤーでSIMD（Single Instruction, Multiple Data）命令を用いて数百行を「一括（ベクトル）」で処理します。

```mermaid
graph TD
    classDef spark fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef photon fill:#312e81,stroke:#8b5cf6,stroke-width:2px;
    
    subgraph "Legacy JVM Spark"
        A[Read Row 1]:::spark --> B[Process Row 1]:::spark
        A2[Read Row 2]:::spark --> B2[Process Row 2]:::spark
        B --> C[Garbage Collection <br/> Stop The World]:::spark
    end
    
    subgraph "Photon Engine (C++ SIMD)"
        D[Read Array: Row 1 to 1024]:::photon --> E[Vectorized Process x86/ARM]:::photon
        E --> F[Zero GC Overhead]:::photon
    end
```

### 3. 【実務への応用】Practical Application (Kazaneya Style)
* **いつPhotonを使うべきか？**: JOIN、集計（AGG）、および複雑な文字列変換（Regex）が多発するバッチ。これらがボトルネックなら、PhotonをONにするだけで計算リソース(DBU)を50%削減しつつ、速度が2倍になるケースがあります。
* **アンチパターン**: I/Oバウンドなワークロード（単に巨大ファイルを読んでどこかに保存するだけの処理）でPhotonを有効にすると、CPUではなくディスクがボトルネックのままなので、割高なPhoton DBUコストだけを支払うことになります。
""",

    # 2. Data Modeling Strategy
    "modeling/kimball_vs_datavault.md": r"""# Lakehouse Data Modeling: Kimball vs Data Vault 2.0
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「システムが変化するとDWHが壊れる」という宿命**
従来のKimball（スタースキーマ）はBIツールで読み込むのには最高ですが、ソースシステムが追加されたり、業務ロジックが変わると、中核となるFactテーブルとDimensionテーブルの両方に手を入れる必要があり、莫大な保守工数が発生します。
エンタープライズのLakehouse基盤において、この「変化に対する脆さ」を解決するのがData Vault 2.0です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Hashベースの疎結合構造 (Hub, Link, Satellite)**
Data Vaultは、ビジネスエンティティ（例: 顧客）を不変のキーとして **Hub** に記録し、複数のエンティティ間の関係（例: 顧客が商品を買う）を **Link** に記録し、変化する全属性（例: 顧客の住所、商品の価格）を **Satellite** に記録します。
新しいシステムのデータソースが増えた場合、「既存のテーブルにカラムを追加する」のではなく、「新しいSatelliteを追加でぶら下げるだけ」で済みます。既存のデータパイプラインは一切テストをやり直す必要がありません（Additive Change）。

```mermaid
erDiagram
    HUB_CUSTOMER ||--o{ LINK_TRANSACTION : "Participates"
    HUB_PRODUCT ||--o{ LINK_TRANSACTION : "Involves"
    
    HUB_CUSTOMER ||--o{ SAT_CUST_CRM : "Has Attributes (System A)"
    HUB_CUSTOMER ||--o{ SAT_CUST_WEB : "Has Attributes (System B)"
    
    LINK_TRANSACTION ||--o{ SAT_TRANS_DETAIL : "Has Details"
    
    %% Architectural elegance: New source systems just add new Satellites without altering Hubs.
```

### 3. 【実務への応用】Practical Application (Kazaneya Style)
* **適用境界**: すべてをData Vaultにするのはアンチパターンです。JOINの回数が激増して分析クエリが遅くなるためです。
* **Kazaneyaの実務解**: 生データを格納するBronzeからSilver（統合層）への変換でData Vault 2.0を用い「変更への耐性（オフェンス）」を高め、最終的にGold層（提供層）へデータを渡す際に、BIツールが読みやすいKimballのStar Schemaに「ビューとして変換（ディフェンス）」する2段構えのアーキテクチャが最強です。
""",

    # 3. Micro-batch fault tolerance
    "spark/streaming_checkpoints.md": r"""# Structured Streaming & Fault Tolerance Mechanics
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「途中で死んだら、どこから再開すればいいのか？」**
Kafkaから毎秒数万件のログを取り込み、ADLSに書き込むストリーミング処理。ノードがクラッシュした際、Sparkはどうやって「重複して書き込まない」「データを取りこぼさない（Exactly-Once）」を保証しているのでしょうか。これを支えるのが `Write-Ahead Logs (WAL)` とディレクトリベースの `Checkpointing` です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
SparkのStructured Streamingは、処理対象のデータ（Kafkaのオフセット番号など）を処理開始『前』に、必ずクラウドストレージ（ADLS等）上のチェックポイントフォルダにJSON形式で記録（WAL）します。
その後処理を行い、Sink（出力先）へ書き込みます。Sink側（Delta Lakeなど）が冪等性（同じ処理を何度やっても結果が同じになる性質）を持つ場合、クラッシュからの復旧時に「保存されたオフセット」を読み直し、安全にリトライを行います。

```mermaid
sequenceDiagram
    participant Kafka as Source (Kafka)
    participant Spark as Spark Engine
    participant CP as Checkpoint (ADLS)
    participant Delta as Sink (Delta Lake)

    Spark->>Kafka: 新しいオフセットを取得 (100〜200)
    Spark->>CP: "100〜200を処理するよ" と記録 (WAL)
    Note over Spark: 処理中にワーカーがクラッシュ！
    Note over Spark: --- ジョブ再起動 ---
    Spark->>CP: 最後にどこまで約束したか確認
    CP-->>Spark: "100〜200が未完了だったよ"
    Spark->>Kafka: 100〜200を再取得
    Spark->>Delta: 安全に書き込み (Idempotent)
```

### 3. 【実務への応用】Practical Application (Kazaneya Style)
* **障害設計**: チェックポイントディレクトリは、データ本体とは完全に独立したパスに保存すること。また、ジョブのロジックを大きく変更（groupByのキーを変える等）した場合、以前のチェックポイントと互換性がなくなり例外で落ちます。この場合はチェックポイントパスを新規で作る（やり直す）必要があります。
"""
}

for filepath, content in content_v4.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

# --------------------------------------------------------------------------
# Step 6: UI Page & UX Enhancement
# Modifying HTML template for reading times, tags, and dynamic typography
# --------------------------------------------------------------------------

def update_ui():
    html_path = os.path.join(base_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Apply Style improvements
    # 1. Update overall fonts and headers
    html = html.replace("font-family: 'Outfit', 'Noto Sans JP', sans-serif;", 
                        "font-family: 'Inter', '-apple-system', 'Segoe UI', 'Roboto', 'Noto Sans JP', sans-serif;")
    
    # 2. Add Read Time UI structure inside viewer meta header
    if '<span id="read-time" class="read-time"></span>' not in html:
        old_meta = '<span id="current-id" class="module-id" style="font-size: 1.2rem;"></span>'
        new_meta = """<div style="display: flex; flex-direction: column; gap: 0.2rem;">
                        <span id="current-id" class="module-id" style="font-size: 1.2rem;"></span>
                        <span id="read-time" style="font-size: 0.8rem; color: var(--text-secondary); display: flex; align-items: center; gap: 0.5rem;">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                            <span id="read-time-text">3 min read</span>
                        </span>
                      </div>"""
        html = html.replace(old_meta, new_meta)

    # 3. Add JS to calculate read time in `loadModule`
    js_inject = """
                const words = text.replace(/<[^>]*>?/gm, '').split(/\s+/).length;
                const readMins = Math.max(1, Math.ceil(words / 400));
                document.getElementById('read-time-text').textContent = `約 ${readMins} 分で読めます`;
    """
    if 'document.getElementById(\'read-time-text\')' not in html:
        # inject dynamically
        html = html.replace("mdContent.innerHTML = marked.parse(text);", "mdContent.innerHTML = marked.parse(text);" + js_inject)

    # 4. Highlight blockquotes with Kazaneya / Architect styles
    css_inject = """
        .markdown-body h1 { background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; border-bottom: none; border-left: 6px solid var(--accent-primary); padding-left: 1rem; margin-bottom: 2rem; }
        .markdown-body blockquote { border-left: 4px solid var(--accent-primary); background: rgba(59, 130, 246, 0.05); padding: 1.5rem; margin: 1.5rem 0; border-radius: 0 12px 12px 0; box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06); }
        .markdown-body blockquote strong { color: var(--accent-primary); }
    """
    if "linear-gradient(135deg" not in html[html.find(".markdown-body h1"):html.find(".markdown-body h1")+200]:
        html = html.replace(".markdown-body blockquote { border-left: 4px solid var(--accent-secondary); background: rgba(16, 185, 129, 0.1); padding: 1rem; margin: 1.5rem 0; font-style: italic; }", css_inject)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

update_ui()

# --------------------------------------------------------------------------
# Bake into JSON (Re-running the package logic)
# --------------------------------------------------------------------------

axes_structure = [
    {"title": "01. Architecture Deep Dives (Kazaneya)", "filter": "databricks/roi_photon_deep.md"},
    {"title": "01. Architecture Deep Dives (Kazaneya)", "filter": "modeling/kimball_vs_datavault.md"},
    {"title": "01. Architecture Deep Dives (Kazaneya)", "filter": "spark/streaming_checkpoints.md"},
    # We will just append the new deeply written V4 files as a featured top track
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
md_files = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True)
md_files = [f.replace(os.sep, "/") for f in md_files]

axes = []
contents_dict = {}

# to avoid duplication of the featured top articles, we pop them from the general filter
featured_paths = [
    "docs/databricks/roi_photon_deep.md",
    "docs/modeling/kimball_vs_datavault.md",
    "docs/spark/streaming_checkpoints.md"
]
md_files = [f for f in md_files if f.replace("/", os.sep) not in [p.replace("/", os.sep) for p in featured_paths]]

def process_file_list(sub_files, ax_idx, axis_title):
    mod_idx = 1
    axis_obj = {"title": axis_title, "modules": []}
    for f in sub_files:
        rel_path = f.replace(base_dir.replace(os.sep, "/") + "/", "")
        mod_id = f"KAZ_{ax_idx}.{mod_idx}"
        
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

# First manual axis out of featured paths
featured_axis = {"title": "00. KAZANEYA SPECIALS", "modules": []}
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

for ax_idx, axis_def in enumerate(axes_structure[3:], 1):  # Skip top 3 because we made a custom VIP axis
    sub_files = [f for f in md_files if f.endswith(".md") and (axis_def["filter"] in f)]
    sub_files.sort()
    axis_obj = process_file_list(sub_files, ax_idx, axis_def["title"])
    if axis_obj["modules"]:
        axes.append(axis_obj)

js_content = "const studyData = {\n"
js_content += '    title: "KAZANEYA DE",\n'
js_content += '    subtitle: "Advanced Architectural Deep Dives",\n'
js_content += '    localStorageKey: "study17_kazaneya_progress",\n'
js_content += '    themeColor: "#14b8a6",\n' # Teal
js_content += '    secondaryColor: "#0ea5e9",\n' # Sky
js_content += '    axes: ' + json.dumps(axes, ensure_ascii=False, indent=4) + '\n};\n\n'
js_content += 'window.moduleContents = ' + json.dumps(contents_dict, ensure_ascii=False, indent=2) + ';\n'

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Workflow Executed. Generated VIP Deep Dive files and injected UI enhancements.")
