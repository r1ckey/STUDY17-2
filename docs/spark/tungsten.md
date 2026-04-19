# Project Tungsten & Memory Management
### 1. 【エンジニアの定義】Professional Definition
**Tungsten**: Spark 1.5から導入された、JVMオブジェクトのオーバーヘッドをバイパスし、メモリ上にバイナリ形式（Unsafe Row）で直接データを配置・計算する内部最適化エンジン。
### 2. 【0ベース・深掘り解説】Gap Filling
JVM（Java仮想マシン）のガベージコレクションはビッグデータの天敵です。数千万のオブジェクトを作るとGCパニックで処理が止まります。
Tungstenは「JVMを通さず、C言語のようにメモリを直接確保・操作（Off-Heap）」し、さらに「Whole-stage Code Generation」でSQLから最適なJavaバイトコードを動的に生成します。これによりSparkは物理的なハードウェア限界に近い速度で動作します。
