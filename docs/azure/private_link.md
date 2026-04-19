# Azure Private Link & VNet Injection
### 1. 【エンジニアの定義】Professional Definition
**Private Link**: AzureのPaaS（ストレージ等）へのアクセスを、パブリックインターネットを経由せず、自社のVNet内のプライベートIPアドレス経由で安全に行う通信技術。
### 2. 【0ベース・深掘り解説】Gap Filling
金融やエンタープライズの現場では「DBの中身が万が一インターネットを通るのはNG」というコンプライアンス要件があります。
通常、DatabricksからADLS（データレイク）を読むと、通信はデータセンター内のインターネットルーターをかすめます。これを遮断するため、Storage Accountに対してPrivate Endpointを設定し、VNet内（10.0.0.x等）のローカルIPで完全閉域網通信を実現します。
また、Databricks自体（Data Plane）をお客様が管理する既存のセキュアなVNetにデプロイする「VNet Injection」も、エンタープライズDEの必須設計知識です。
