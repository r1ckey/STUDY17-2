# Core Data Testing (Great Expectations)
### 1. 【エンジニアの定義】Professional Definition
**Great Expectations**: データの「期待値（NULLがないか、値の範囲が妥当か）」を定義し、パイプラインに取り込まれたデータがその条件を満たしているかを検証（プロファイリング／テスト）するためのPythonフレームワーク。
### 2. 【0ベース・深掘り解説】Gap Filling
ソフトウェアがバグる原因は「コードのバグ」ですが、データパイプラインが壊れる原因の9割は「想定外のデータが上流から飛んできた（Data Outage）」ことです。
これを防ぐため、dbtテストやGreat Expectationsをパイプラインの関所（Data Contract）として置き、腐ったデータが湖（Data Lake）に入るのを未然にブロックします。
