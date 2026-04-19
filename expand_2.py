import os

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")
os.makedirs(docs_dir, exist_ok=True)

content_dict = {
# --- Axis 3: Databricks Core Extensions ---
"databricks/autoloader.md": r"""# Auto Loader (Streaming Ingestion)

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
""",

# --- Axis 4: Modern Data Stack ---
"dbt/elt.md": r"""# ELT vs ETL Paradigm Shift

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
""",

"dbt/testing.md": r"""# dbt Testing & Documentation

### 1. 【エンジニアの定義】Professional Definition
> **dbt Testing**:
> データ変換パイプラインにおいて、データの品質（一意性、非NULL、制約など）を担保するために、SQLベースで自動実行されるテスト群。
> **dbt Docs**:
> データパイプラインからテーブルのスキーマ、説明、依存関係グラフ（DAG）までを自動生成するドキュメント機能。

### 2. 【0ベース・深掘り解説】Gap Filling
#### 🐛 「ゴミを入れたらゴミが出る」を防ぐ
データ分析の世界で最悪なのは、「データパイプラインが正常終了したのに、結果の売上が実態と合っていない」ことです。
dbtを使うと、`schema.yml` に数行書くだけで「売上カラムは負の値にならないか」「ユーザーIDは一意か」を毎回の処理時にテストできます。
エラーがあれば処理を止め、後続のダッシュボードを汚染しません。ソフトウェア開発の「CI/CDテスト」の文化をデータ領域に持ち込んだ革命です。

### 💡 この用語のまとめ (Key Takeaways)
* **4大標準テスト**: `unique`, `not_null`, `accepted_values`, `relationships`。
* **データカタログ**: `dbt docs generate` だけで、開発者が欲しかったテーブル定義書と関係図がウェブとして出力される。
"""
}

# Ensure directories exist and write files
for filepath, content in content_dict.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated Phase 2 expansion modules: {len(content_dict)} files.")
