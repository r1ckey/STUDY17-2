import os

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17\docs"

content_dict = {
    "certifications/azure_de.md": r"""# Azure Data Engineer Associate (DP-203)

### 1. 【エンジニアの定義】Professional Definition

> **Azure Data Engineer Associate (DP-203)**:
> Microsoft Azure上で、リレーショナル・非リレーショナルデータを統合、変換、統合するデータソリューションの設計および実装能力を証明する資格。Azure Synapse Analytics、Azure Data Factory (ADF)、Azure Databricks、Azure Data Lake Storage (ADLS) などのコアリソースを網羅的に理解していることが求められる。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 🏭 AzureにおけるETLの主役: Azure Data Factory (ADF)
オンプレミスからクラウドへデータを引っ張り上げる時、まず間違いなく使われるのが**Azure Data Factory**です。
SSIS（SQL Server Integration Services）の系譜を継ぐこのツールは、GUI上でアイコンを繋ぐだけで「毎晩DBサーバーからデータを抜いてADLSに保存する」処理（Copy Data activity）が作れます。
試験では、「オーケストレーションはADF」「重いデータ変換はDatabricksかSynapse」という役割分担が必ず問われます。

#### 🌊 Synapse Analytics vs Databricks
Azureには強力な分析環境が2つあります。どう使い分けるべきか？
*   **Azure Synapse Analytics**: Microsoft純正の全部入りモダンDWH。SQLをこよなく愛するチーム向け。専用SQLプール（旧SQL DW）と、サーバーレスSQLプールが強力。
*   **Azure Databricks**: Apache Sparkベースのオープンな分析基盤。PythonやScalaなどコードベースでゴリゴリ機械学習や複雑なETLをこなすデータサイエンス・エンジニア向け。

試験では「Sparkを細かくチューニングしたい」「Pythonの機械学習ライブラリを多用する」という要件があればDatabricksを選ぶのが正解となります。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

Azure公式が提示するモダンデータウェアハウスの典型的なアーキテクチャ像。

```mermaid
graph TD
    subgraph "1. Ingest (抽出・ロード)"
        Source[("オンプレDB / SaaS")]
        ADF["Azure Data Factory<br>(Copy Activity)"]
        Source -->|"スケジュール実行"| ADF
    end

    subgraph "2. Store (データレイク)"
        ADF --> ADLS[("Azure Data Lake<br>Storage Gen2")]
    end

    subgraph "3. Prep & Train (変換)"
        ADLS -->|"PySpark"| ADB["Azure Databricks"]
        ADB -->|"整形・正規化"| ADLS
    end

    subgraph "4. Model & Serve (DWH / 提供)"
        ADLS -->|"PolyBase"| Synapse[("Azure Synapse<br>Analytics")]
        ADB -.->|"直接連携も可"| Synapse
    end

    subgraph "5. Consume (可視化)"
        Synapse --> PowerBI["Power BI"]
    end
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **DP-203の핵**: ADF(運ぶ) → ADLS(貯める) → Databricks(磨く) → Synapse(提供する) の黄金リレー。
*   **セキュリティと監視**: Azure Key Vaultを使ったシークレット管理や、Log Analyticsでの監視も頻出。
*   **Lambdaアーキテクチャ**: バッチ処理(ADF)とストリーム処理(Event Hubs + Stream Analytics)のハイブリッド設計に慣れること。
""",

    "python/index.md": r"""# Python Data Engineering Essentials

### 1. 【エンジニアの定義】Professional Definition

> **Python (データ基盤における)**:
> 機械学習からデータエンジニアリングまで、データ領域における事実上の共通言語。単なるスクリプト言語ではなく、PySpark、pandas、Airflow、dbt（内部Jinja）など、モダンデータスタックのツール群を接着する「グルー（接着剤）」として機能する。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 📦 なぜデータ基盤はPython一強なのか？
かつて企業のETL処理はJavaやScalaで書かれていました。高速だからです。
しかし現在、データパイプラインは「いかに早くビジネス要件に合わせてSQLを組み立てるか」にシフトしました。Pythonは遅いと言われますが、それは**誤解**です。Pythonが遅いのは「for文で1行ずつ処理した時」だけであり、PySparkやPolarsを介して「C言語やRustで書かれた計算エンジンに命令を出す」分には、Javaと同じ速度が出ます。
手軽に書けて、内部は超高速。これがPython一強の理由です。

#### 🐍 Pandas から PySpark(分散) への意識改革
データエンジニアとしてPythonを書く際、単なるウェブエンジニアと最も異なるのが「**分散処理への理解**」です。
Pandasは1台のPCのメモリ内で動きますが、データが1TBを超えると `MemoryError` で落ちます。そこでPySparkを使います。Pythonで書いたコードは通信（RPC）を通じてクラスター上の数千のWorkerノードに翻訳され実行されます。「今自分が書いているコードは、マスターとワーカーのどちらで動くのか？」を意識しないと、平気でクラスターを破壊するコードを書いてしまいます（例：巨大なイテレータをワーカーからCollectしてしまう等）。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

Pythonがモダンデータスタックの様々な領域をいかに繋いでいるか。

```mermaid
graph TD
    Python["Python (The Glue)"]
    
    subgraph "Orchestration"
        Python -->|"DAG定義"| Airflow["Apache Airflow"]
        Python -->|"パイプライン自動化"| Prefect["Prefect / Dagster"]
    end

    subgraph "Data Transformation"
        Python -->|"分散処理API"| Spark["PySpark / Databricks"]
        Python -->|"巨大な単一ノード処理"| Polars["Polars / Pandas"]
        Python -->|"DWH内マクロ"| dbt["dbt (Jinja2)"]
    end
    
    subgraph "Data Quality & ML"
        Python -->|"型検証"| GreatEx["Great Expectations"]
        Python -->|"機械学習"| Scikit["Scikit-Learn / PyTorch"]
    end
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **Pythonの役割**: 計算そのものを行うのではなく、CやRustで書かれた高速エンジンに「命令を出す」指揮官。
*   **関数型へのシフト**: データ処理コードは状態を持たない（副作用のない関数）純粋関数型に近い書き方が求められる。
*   **メモリの境界に敏感になる**: ローカルの16GBメモリと、クラウドの数TBの分散メモリの違いを常に意識してAPIを使い分ける。
""",

    "projects/keiba.md": r"""# Project: 競馬データ分析基盤

### 1. 【エンジニアの定義】Professional Definition

> **競馬データエンジニアリング計画**:
> Webからのデータスクレイピング（Extract）、Databricksによる分散データクレンジング・特徴量エンジニアリング（Transform）、およびクラウドDWHへの保存（Load）という、モダンデータスタックの基本を網羅した実践的フルスクラッチ・ポートフォリオ。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 🏇 なぜ競馬データはETLの最高の練習台なのか？
競馬データは「ただの数字の羅列」ではありません。
*   **多様なデータ構造**: 過去数十年のレース結果（表データ）、出走馬の血統（ツリー構造）、オッズの変動（時系列データ）。これらバラバラのデータをキーで繋ぎ合わせるRDB設計の知見が身につきます。
*   **ダーティデータの宝庫**: クレイピングしたデータは「取消」「中止」「同着」といったイレギュラーなノイズが大量に含まれています。これらを安全に弾いたり補完したりするPySparkの `fillna()` や `when().otherwise()` の実戦経験が積めます。
*   **特徴量生成（Feature Engineering）**: 「前走からの日数」「過去3戦の平均タイム」など、Window関数の高度な使い方（`partitionBy().orderBy().rowsBetween()`）を嫌というほど学べます。

#### 🏗️ 設計方針：メダリオンアーキテクチャの適用
このプロジェクトではDatabricks認定で学ぶ「メダリオン」を忠実に再現します。
1.  Python（BeautifulSoup等）で取きた生のHTML/JSONをそのままADLS（Bronze層）に投下。
2.  Databricks Autoloaderを利用して自動的に差分を読み込み、不要な列を削ってParquetでSilver層へ。
3.  dbtを使ってSilver層のテーブル同士を繋ぎ、機械学習モデルがそのまま食える行列データ（Gold層）を生成。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

完全自動化された競馬データ収集・処理パイプライン。

```mermaid
graph TD
    subgraph "Scraping & Ingestion (Python/GCP/Azure)"
        Target["競馬情報サイト(netkeiba等)"]
        Scraper["Cloud Functions / Azure Functions<br>(Python スクレパ)"]
        Target -.->|"HTML解析"| Scraper
    end

    subgraph "Databricks Lakehouse (Medallion)"
        Bronze[("Bronze Delta Table<br>(Raw HTML/JSON)")]
        Silver[("Silver Delta Table<br>(正規化・型変換)")]
        Gold[("Gold Delta Table<br>(ML特徴量マトリクス)")]
        
        Scraper -->|"JSON投下"| Bronze
        Bronze -->|"PySpark クレンジング"| Silver
        Silver -->|"dbt / Window関数集計"| Gold
    end

    subgraph "Consumption (ML/BI)"
        MLFlow["MLflow (モデル管理)"]
        AutoML["Databricks AutoML<br>(予測モデリング)"]
        Gold --> AutoML
        AutoML --> MLFlow
    end
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **実践的ETLの登竜門**: 競馬データは「データの汚さ」「結合の複雑さ」「時系列」の全要素が詰まった最高の教材。
*   **Window関数の極意**: 「過去◯戦の成績」を出すためにSQL/PySparkの高度な分析関数を習得できる。
*   **最終ゴール**: 自作のデータパイプラインからMLflowまでを繋ぎ、「データ基盤構築からAI予測まで1人で完結できる」証明とする。
"""
}

# Ensure directories exist and write files
for filepath, content in content_dict.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Brushed up the final {len(content_dict)} mkdocs pages successfully!")
