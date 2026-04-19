# Service Endpoint vs Private Endpoint
### 1. 【エンジニアの定義】Professional Definition
**Service Endpoint**: Azure VNetからPaaS（Storage等）への経路を「最短のMicrosoftバックボーン経由」にする機能。しかし、Storage自体は依然としてパブリックなエンドポイントを持つ。
**Private Endpoint**: VNet内の「プライベートIPアドレス」をPaaSに割り当て、インターネットからのアクセスを100%物理的に遮断する（外から見えなくなる）最強の閉域網機能。
### 2. 【0ベース・深掘り解説】Gap Filling
セキュリティ審査で「ADLSをセキュアにしろ」と言われたとき、Service Endpointで済ませると金融機関の審査に落ちます。Private Endpoint と Private DNS ZoneをポチポチまたはTerraformで構成し、「10.0.x.x」のIPでDatabricksとADLSを通信させることが、プロフェッショナルDEの必須スキルのひとつです。
