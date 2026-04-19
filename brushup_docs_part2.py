import os

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17\docs"

content_dict = {
    "databricks/index.md": r"""# Databricks Mastery

### 1. 【エンジニアの定義】Professional Definition

> **Databricks**:
> Apache Sparkのオリジナル開発者たちが創設した、データエンジニアリング、データサイエンス、機械学習、および分析を単一のプラットフォームで提供するUnified Data Analytics Platform（統合データ分析基盤）。
> 
> **Lakehouse Architecture**:
> データレイクの「柔軟性・低コスト（非構造化データの保存）」と、データウェアハウスの「信頼性・パフォーマンス（ACIDトランザクションと高速スキーマクエリ）」を融合させた独自のアーキテクチャ。Databricksはその提唱者でありリーディングカンパニー。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 🔄 なぜ「レイク」と「ウェアハウス」を合体させたのか？
昔のデータ基盤は「二度手間」でした。
まずAWS S3に生データ（ログや画像）を全部突っ込む（Data Lake）。しかしそこからBIで分析するには遅すぎる・SQLが使えないため、綺麗に整形した一部のデータをSnowflakeやRedshiftに**コピーして移す（Data Warehouse）**必要がありました。
これをやると「コピー時のバグ」「データ同期の遅延」「二重のストレージコスト」という地獄が発生します。
Databricksは「**Delta Lake**」技術を使って、S3やADLSにある「生データ」に対して直接、DWH並みの高速SQL処理とトランザクション保護をかけられるようにしました。これにより、**データのコピー移動を不要**にしたのがLakehouse革命です。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

データ基盤の進化とLakehouseの立ち位置。

```mermaid
graph TD
    subgraph "1. 過去: Data Warehouse"
        DB1[(RDBMS)] --> ETL1[ETL] --> DWH1[(DWH)]
        Note over DB1,DWH1: 構造化データしか入らない<br/>高コスト
    end

    subgraph "2. 過渡期: Two-Tier (Data Lake + DWH)"
        Raw2[ログ/画像等] --> DL2[(Data Lake / S3)]
        DL2 -->|"複雑なETLでコピー"| DWH2[(DWH)]
        Note over Raw2,DWH2: データの二重管理・同期エラー
    end

    subgraph "3. 現在: Lakehouse (Databricks)"
        Raw3[あらゆるデータ] --> DL3[(Delta Lake / ADLS)]
        DL3 -->|"直接SQLクエリ<br>(Databricks SQL)"| BI3[BI Tools / AI]
        Note over Raw3,BI3: コピー不要。単一の信頼できる情報源
    end
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **Databricks**: Sparkのお膝元。データエンジニア最強の武器。
*   **Lakehouse**: データレイクの上にDWHの信頼性と速度を乗せるパラダイム。データの二重管理を粉砕する。
""",

    "certifications/databricks_associate.md": r"""# Databricks Certified Data Engineer Associate

### 1. 【エンジニアの定義】Professional Definition

> **Databricks Certified Data Engineer Associate**:
> Databricksプラットフォームを使用して、データ処理の基本タスク（ETL）を実行する能力を証明するエントリーレベル資格。Delta Lakeの基礎、Databricks SQL、Sparkの基本概念、ジョブのスケジューリング、およびUnity Catalogの基礎権限管理などが問われる。

---

### 2. 【0ベース・深掘り解説】Gap Filling

#### 🏗️ 「メダリオンアーキテクチャ」が試験の心臓部
この試験を突破するために最も重要な概念は**Medallion Architecture（ブロンズ・シルバー・ゴールド）**のデータパイプライン設計です。
*   **Bronze層 (Raw)**: APIやファイルから持ってきた生のJSONなどを「そのままの形」で保存するゴミ箱兼履歴層。
*   **Silver層 (Enriched)**: Bronzeのデータを読み、日付フォーマットを揃えたり、NULLを除去したり、テーブル同士を結合したりして「綺麗に整形した」クレンジング層。
*   **Gold層 (Curated)**:  Silverを参照して「部門別売上サマリ」「マーケティング用KPI」など、BIツールが即座に読める状態に集計済みのビジネス層。

試験では「Bronze層の目的として正しいものはどれか？」「データウェアハウスの代わりになる集計層はどれか？」といった役割の理解が深く問われます。

---

### 3. 【アーキテクチャの視覚化】Visual Guide

Databricks公式が推奨するメダリオンアーキテクチャの流れ。

```mermaid
graph LR
    subgraph "Auto Loader / Kafka"
        Ingest["Raw Data Streams"]
    end

    subgraph "Delta Lake (Medallion Architecture)"
        Bronze[("Bronze<br/>(生データ/変更履歴)")]
        Silver[("Silver<br/>(フィルタ・結合・正規化)")]
        Gold[("Gold<br/>(ビジネスレベル集計)")]
        
        Ingest -->|"そのまま保存"| Bronze
        Bronze -->|"クレンジング"| Silver
        Silver -->|"集計 (Group By)"| Gold
    end

    subgraph "Consumers"
        BI["BI Dashboards"]
        ML["Machine Learning"]
        
        Gold --> BI
        Silver --> ML
    end
```

---

### 💡 この用語のまとめ (Key Takeaways)
*   **Medallion Architecture**: Bronze(生の保存) → Silver(綺麗な明細) → Gold(集計・BI用)の3層構造。
*   **Auto Loader**: クラウドストレージに新しく到着したファイルだけを差分で読み込む超便利機能。試験頻出。
*   **Delta Live Tables (DLT)**: SQLやPythonで「データの流れ」を定義するだけで処理が動く、Databricksのパイプライン自動化機能。
"""
}

# Ensure directories exist and write files
for filepath, content in content_dict.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Brushed up 2 more core mkdocs pages successfully!")
