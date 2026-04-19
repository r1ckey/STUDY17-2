# B-Tree vs LSM Tree (Storage Engines)
### 1. 【エンジニアの定義】Professional Definition
**B-Tree**: MySQL等の旧来のRDBMSで使われる、読み込み（検索）に強いが、ランダム書き込みに弱い木構造インデックス。
**LSM Tree (Log-Structured Merge-Tree)**: CassandraやRocksDB等で使われる、書き込み（Write）を超高速にするために、とにかくログとしてデータを追記（Append）し続け、裏側でマージする形式。
### 2. 【0ベース・深掘り解説】Gap Filling
秒間数万件のIoTセンサーデータをRDBMS(B-Tree)に投げると、インデックスの再構築（ページ分割）によりディスクI/Oが爆発して死にます。ビッグデータでは書き込み効率（Write Amplificationの低減）が命なので、NoSQLのLSM Treeアーキテクチャが多用されます。
