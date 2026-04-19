# Data Fabric
### 1. 【エンジニアの定義】Professional Definition
**Data Fabric**: 物理的に分散しているデータ（AWS, Azure, オンプレミス）を、まるで1つの巨大な仮想データ空間に存在するかのようにアクセス・管理可能にするテクノロジー主導のアーキテクチャ。
### 2. 【0ベース・深掘り解説】Gap Filling
Microsoft Fabricがまさにこれです。Azure上のデータも、AWS S3上のデータも、物理的に1箇所にコピー（ETL）することなく、OneLakeという仮想レイヤーを通じて「ショートカット」として接続し、シームレスにJOINできます。データの移動コストをなくす究極のアプローチです。
