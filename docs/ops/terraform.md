# Terraform for Databricks
### 1. 【エンジニアの定義】Professional Definition
**Infrastructure as Code (IaC)**: インフラ構築をUI上のクリックではなく、HCL形式のコードで自動化・バージョン管理する手法。
### 2. 【0ベース・深掘り解説】Gap Filling
手作業でDatabricksのクラスターを作り、権限を手動で付与していると、別の開発環境や本番環境を作るときに手順ミス（ヒューマンエラー）が確実に発生します。
Terraformを使えば、`databricks_cluster` や `databricks_secret` リソースをコード化し、`terraform apply` を叩くだけで全く同じ環境が数分で再現されます。
クラスタのノードタイプ変更や、特定ユーザーの退職に伴う権限削除なども、GitHub上のコードレビュー（PR）を通じて安全かつ監査可能な形で実行できます。
