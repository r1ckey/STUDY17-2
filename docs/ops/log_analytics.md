# Databricks Monitoring with Log Analytics
### 1. 【エンジニアの定義】Professional Definition
**Azure Log Analytics / Monitor**: DatabricksやADFから排出される膨大な診断ログ（監査ログ、ジョブの実行ログ、クラスターのメトリクス）をKusto Query Language (KQL) で一元的に検索・分析・アラート設定する基盤。
### 2. 【0ベース・深掘り解説】Gap Filling
「昨日突然ジョブが失敗した。原因は？」と聞かれたとき、DatabricksのUIの奥底からログを拾うのは三流です。
熟練のDEは、クラスターの設定（init scriptなど）で診断ログをLog Analyticsに流すように構成しており、KQLを用いて「昨日OOMエラーで死んだプロセス一覧」を1秒で特定し、アラート連携（PagerDutyやTeams）させます。
