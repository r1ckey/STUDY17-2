# Distributed Computing & DataFrames

### 1. 【エンジニアの定義】Professional Definition
> **PySpark DataFrame**:
> 一見するとPandasの表に見えるが、実は「複数台のサーバー（Worker）に分割（Partition）して保持されているデータのかたまり」を抽象化したもの。
> **Partition (パーティション)**:
> 分散処理の並列度の基本単位。100個のパーティションがあれば、理論上100個のCPUコアで同時に計算ができる。

### 2. 【0ベース・深掘り解説】Gap Filling
#### 🍰 パーティションという「ケーキの切り分け」
100GBのデータを1人で食べる（1台のサーバーで計算する）には何日もかかります。
Sparkはこれを例えば1000個のショートケーキ（Partition）に分割し、10人で一気に食べ進めます。
もし「1個のケーキだけ50GBあり、残り999個は1MB」という切り分け方をしたら？（これを**データスキュー / Data Skew** と呼ぶ）。1人だけ徹夜で食べ続けることになり、システム全体が遅延します。
データエンジニアの腕の見せ所は、この「ケーキの切り分け方（パーティション）を均等・最適に保つ」ことです。

### 3. 【アーキテクチャの視覚化】Visual Guide
```mermaid
graph TD
    subgraph "Driver Node (司令塔)"
        Code[df.count()]
    end
    
    subgraph "Worker Nodes (実行部隊)"
        W1[Core 1: Partition 1]
        W2[Core 2: Partition 2]
        W3[Core 3: Partition 3]
    end
    
    Code -->|"タスク分配"| W1
    Code -->|"タスク分配"| W2
    Code -->|"タスク分配"| W3
```

### 💡 この用語のまとめ (Key Takeaways)
* **Sparkの本質**: 1台でできないことを、複数台に「切り分けて（Partition）」任せる。
* **Data Skew**: 分散処理最大の敵。データが一部のノードに偏る現象。
