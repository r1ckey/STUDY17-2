# ELT vs ETL Paradigm Shift

### 1. 【エンジニアの定義】Professional Definition
> **ETL (Extract, Transform, Load)**:
> データを抽出し、中間の専用サーバーで変換し、綺麗にしてからウェアハウスにロードする旧来の手法。
> **ELT (Extract, Load, Transform)**:
> 生データをとにかく全部ウェアハウス(DWH)にロードしてから、DWHの強力な計算エンジン（SQL）を使って変換する現代の手法。

### 2. 【0ベース・深掘り解説】Gap Filling
#### 🦖 中間サーバーの悲劇 (ETL)
昔のデータベースは計算能力が貧弱で高価でした。だからDB内で複雑な文字列変換等を行うとシステムが死ぬため、間に専用の「ETLサーバー（InformaticaやTalend等）」を挟んでいました。しかし、このサーバーがボトルネックとなり、スケールしない・学習コストが高いという問題がありました。

#### 🚀 SnowflakeとDatabricksがもたらしたELT革命
現在はDWHやLakehouse側の計算パワーが無限大（クラウドスケール）になりました。
間に不要なサーバーを挟まず、Fivetran等のツールで**とにかく全データをDWHにコピー（Load）**します。
そしてDWHの中で、SQLを使ってデータを整形（Transform）します。このDWH内部での「T」を司るのが **dbt** です。

### 3. 【アーキテクチャの視覚化】Visual Guide
```mermaid
graph TD
    subgraph "ETL (Old Generation)"
        E1[Systems] -->|"Extract"| T1[ETL Server]
        T1 -->|"ボトルネック！"| T1
        T1 -->|"Load"| L1[(DWH)]
    end

    subgraph "ELT (Modern Data Stack)"
        E2[Systems] -->|"抽出・即ロード(Fivetran)"| L2[(DWH / Lakehouse)]
        L2 -->|"DWH内部で変形(dbt)"| L2
        Note right of L2: 計算パワーが無限なので<br/>全部DBの中でやる！
    end
```

### 💡 この用語のまとめ (Key Takeaways)
* **ELT**: とにかく先に保存する。加工は無限のパワーを持つデータベース内で。
* **モダンデータスタック**: Fivetran(EL) + Snowflake/Databricks + dbt(T) の鉄板構成。
