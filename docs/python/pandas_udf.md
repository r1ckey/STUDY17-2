# Pandas UDF (Vectorized UDF)
### 1. 【エンジニアの定義】Professional Definition
**Pandas UDF**: PySpark上でPythonネイティブの関数を適用する際、1行ずつ評価する従来の激遅なUDFを捨て、内部的にApache Arrowを用いてJVMとPythonプロセス間のデータ転送をバッチ単位（列指向）で高速に行う機能。
### 2. 【0ベース・深掘り解説】Gap Filling
Sparkで「複雑な機械学習推論」を行う場合、SQLでは書けないためPythonのUDFを作ります。しかし従来のUDFは、1行ずつ「JVM → Python」へデータ変換・通信を行うため、数千万行の処理に数時間かかります。Pandas UDFを使うと、数千行のブロック単位で一気に処理が渡るため、10〜100倍の圧倒的な高速化が保証されます。
