# MVCC (Multi-Version Concurrency Control)
### 1. 【エンジニアの定義】Professional Definition
**MVCC (多版同時実行制御)**: データベースにおいて「書き込み処理」と「読み込み処理」が互いにブロック（ロック待ち）しないようにする仕組み。書き込み中に別人が読み込んでも、書き込み直前の「古いバージョンのスナップショット」が見える。
### 2. 【0ベース・深掘り解説】Gap Filling
PostgreSQLやOracle、そしてDatabricksのDelta Lakeでも採用されています。Aさんが1億行のUPDATEをかけている最中に、Bさんが同じ表をSELECTしてもエラーにならず、UPDATE前のデータが綺麗に返ってきます。DWHにおいて「夜間バッチを動かしながら、昼間のBIダッシュボードを見せる」ための最強の裏技です。
