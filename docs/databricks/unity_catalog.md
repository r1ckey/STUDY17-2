# Unity Catalog & Data Governance
### 1. 【エンジニアの定義】Professional Definition
**Unity Catalog (UC)**: ワークスペースを跨いだ統合ガバナンスソリューション。テーブル、ファイル、MLモデルに対するアクセス権限（ACL）を一元管理し、血統（Lineage）を自動追跡する。
### 2. 【0ベース・深掘り解説】Gap Filling
旧来のHive Metastore時代は「ワークスペースAとBでテーブル権限がバラバラ」「誰がこのテーブル作ったのか分からない」地獄でした。
UCはすべてを階層化します（`catalog.schema.table`）。
最も偉大な機能は「カラムレベルの血統（Lineage）」。`users`テーブルの`email`カラムが、どのETLジョブを経て、どのPower BIのグラフに使われているか、UI上で網の目のようなグラフで完全にトラッキングできます。個人情報削除（GDPR）対応の必須機能です。
