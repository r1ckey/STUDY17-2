# Lambda vs Kappa Architecture
### 1. 【エンジニアの定義】Professional Definition
**Lambda Architecture**: バッチ処理の層（Hadoop等）と、リアルタイムのストリーミング層（Storm/Spark Streaming等）の２つを並行して動かし、Viewで統合するアーキテクチャ。複雑極まりない。
**Kappa Architecture**: バッチ処理を捨て、「すべてをログのストリームとして扱う（Kafka中心）」ことで、システムを一つに統合したモダンなアーキテクチャ。
### 2. 【0ベース・深掘り解説】Gap Filling
Lambdaアーキテクチャは「バッチ用とストリーム用」の2つの似たようなコードを書かなければならず、保守が地獄でした。Databricksはこの派生で、「バッチとストリーミングの境界を無くす」Delta Live Tables (DLT) 等を推進しています。
