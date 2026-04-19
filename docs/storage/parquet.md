# Parquet Internals (Row Group & Bloom Filter)
### 1. 【エンジニアの定義】Professional Definition
**Parquet**: 列指向（Columnar）のファイルフォーマット。データをRow Group単位で分割し、列ごとに圧縮をかけることでスキャン性能を極限まで高める。
### 2. 【0ベース・深掘り解説】Gap Filling
なぜParquetは速いのか？クエリで `select age from users` としたとき、CSVなら全データを読みますが、Parquetなら「age列」のブロックだけをディスクから取得します（**Column Projection**）。
さらに「1〜10万行目のageの最小値は20、最大値は50」という統計情報を持っているため、`age = 60` を探す場合、そのブロックを一切読まずにスキップします（**Predicate Pushdown**）。
ここにブルームフィルタ（Bloom Filter: 確率的データ構造）を組み合わせることで、不要なディスクI/Oを99%削減できます。
