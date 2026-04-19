# Databricks Mastery

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
