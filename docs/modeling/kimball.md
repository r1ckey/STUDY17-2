# Kimball Dimensional Modeling
### 1. 【エンジニアの定義】Professional Definition
**ディメンショナル・モデリング**: 業務プロセスを「測定可能な数値（Fact）」と「その文脈・属性（Dimension）」に分けてモデリングする、DWH設計の事実上の標準。スタースキーマを形成する。
### 2. 【0ベース・深掘り解説】Gap Filling
RDBMSの第3正規化（重複を無くす設計）をデータ分析に持ち込むと、JOINが10個以上発生しクエリが死にます。
分析用DWHでは「誰が(DimUser)、いつ(DimDate)、どこで(DimStore)、何を(DimProduct)買って、金額はいくらだったか(FactSales)」という星型（Star Schema）に設計します。
これにより、BIツール（PowerBI等）が直感的にフィルターをかけやすくなり、エンジニア以外のビジネスユーザーでもSQLライクな分析が可能になります。
