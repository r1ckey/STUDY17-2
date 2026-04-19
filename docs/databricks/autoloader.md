# Auto Loader (Streaming Ingestion)

### 1. 【エンジニアの定義】Professional Definition
> **Auto Loader API (`cloudFiles`)**:
> Databricksが提供する、クラウドストレージ（S3, ADLS等）に新しく到着したファイルのみを、追加の設定や管理なしで自動的かつ増分的に読み込むStreaming機構。内部的にRocksDBを用いて「どのファイルまで読んだか」の状態を管理する。

### 2. 【0ベース・深掘り解説】Gap Filling
#### 🔄 毎日数万ファイル来るバッチ処理の限界
ADLSの特定のフォルダに、業務システムから毎日「5分おき」にCSVファイルが飛んでくるとします。
過去のSparkエンジニアはどうやって「新しく来たファイルだけ」を読んでいたでしょうか？
`1. フォルダ内のファイル一覧を取得する`
`2. DBに書き込んだログと突き合わせて、未処理のファイル名だけを抽出する`
`3. それをSparkで読み込む...`
このコードを書くのは地獄であり、ファイルが100万件を超えると「ファイル一覧(ls)を取得する時間」だけで数十分かかります。
**Auto Loader**を使うと、`spark.readStream.format("cloudFiles")` と書くだけで、Databricksがバックグラウンドで「イベントグリッド」等と連携し、新着ファイルを超高速かつ確実に処理してくれます。

### 3. 【アーキテクチャの視覚化】Visual Guide
```mermaid
graph LR
    subgraph "SaaS / On-Prem"
        App[Business App] -->|"5分おきにCSV出力"| ADLS[ADLS (Data Lake)]
    end

    subgraph "Databricks Auto Loader"
        ADLS -.->|"File Event Notification"| State[RocksDB Checkpoint]
        State -->|"未読ファイルだけを抽出"| Spark[Spark Engine]
        Spark --> Delta[(Bronze Delta Table)]
    end
```

### 💡 この用語のまとめ (Key Takeaways)
* **Auto Loader**: ファイル増分取り込みの絶対的スタンダード。コードが数行で済む。
* **スキーマ推論**: 翌日急にCSVの列が増えても、Auto Loaderが自動で検知して処理を落とさず（あるいは安全に止めて）修復を促す。
