# Photon Execution Engine (Vectorized C++)
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「JVMの壁」と次世代データ処理**
Apache Sparkは長らくビッグデータ処理の覇者でしたが、データ量がペタバイト級に跳ね上がり、かつ複雑な計算（Hash JoinやRegex Extract）が頻発する現代において、「Java仮想マシン (JVM)」上で動作することが巨大な足かせとなりました。
Row（行）単位での処理によるCPUのキャッシュミス、オブジェクトのシリアライズ/デシリアライズの負荷、そして大量のメモリを消費して定期的に処理を止めるGC（Garbage Collection）。これらJVM固有の遅延要因を完全に根絶するため、Databricksが底辺からC++でゼロスクラッチした処理エンジンが Photon です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Volcano Model から Vectorized Execution へ**
従来のSpark（や古いRDBMS）は Volcano Model と呼ばれ、1行ずつ評価していました（`next_row()`）。
Photon は、1行ではなく数千行（バッチ）をメモリ上の連続したアレイ（Array）領域に展開し、現代のCPU（Intel/AMD/ARM）に備わっている SIMD (単一命令・複数データ) を使って、一回のCPUサイクルで配列全体の演算を終わらせます。

```mermaid
graph TD
    classDef spark fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef photon fill:#312e81,stroke:#8b5cf6,stroke-width:2px;
    
    subgraph "Legacy Spark (JVM)"
        A[Driver Plan]:::spark --> B[JVM Executors]:::spark
        B --> C[Row-by-Row Iterator]:::spark
        C --> D[Add 1 + 2]:::spark
    end
    
    subgraph "Photon Engine (Native C++)"
        A2[Driver Plan]:::photon --> B2[Detect Photon Compatibility]:::photon
        B2 --> C2[C++ Layer (Off-Heap)]:::photon
        C2 --> D2[Vectorized SIMD Add [1,5...] + [2,10...]]:::photon
    end
```

### 3. 【実務への応用】Practical Application
* **Photonの適材適所**:
  Photonは「すべての処理をC++でやる」わけではなく、Sparkプランの中で、Photonが対応しているノード（HashJoin, AGG 等）だけを部分的にC++に任せ、非対応の機能（一部のカスタムUDF等）はJVMのSparkに戻す（Fallback）、というハイブリッドで動きます。UDFを多用すると、C++とJVMの間でデータ変換が多発し、かえって遅くなるため、極力Sparkの組み込み関数を使う（Pyspark.sql.functions）ことが、Photonの恩恵を最大化する秘訣です。
