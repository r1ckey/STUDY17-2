# Photon Engine
### 1. 【エンジニアの定義】Professional Definition
**Photon**: JVM上のSparkの限界を突破するため、DatabricksがC++でフルスクラッチ開発したネイティブベクトル化（Vectorized）クエリエンジン。
### 2. 【0ベース・深掘り解説】Gap Filling
CPUは「SIMD（Single Instruction, Multiple Data）」という、1回の命令で複数の配列データを一気に処理する機能を持っていますが、JVMからはこれがうまく使えません。
PhotonはSparkの「実行計画」をそのまま受け取り、実行処理（JOIN, AGGなど）だけをC++側でSIMDを駆使して爆速処理します。設定のチェックボックスをオンにするだけで、既存のPySpark/SQLコードを書き換えることなく2〜5倍高速化します。
