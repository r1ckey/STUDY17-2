import os

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")
os.makedirs(docs_dir, exist_ok=True)

content_dict = {
# --- Axis 1: Python Data Foundation ---
"python/core.md": r"""# Python in Data Engineering (Core)

### 1. 【エンジニアの定義】Professional Definition
> **Python Core for DE**:
> データ基盤開発において、スクリプトの保守性とリソース効率を最大化するPythonの基礎知識。単純なfor文だけでなく、ジェネレータ（`yield`）による省メモリ処理や、辞書内包表記を用いた高速な変換、型ヒント（Type Hinting）を用いたエラー防止が必須となる。

### 2. 【0ベース・深掘り解説】Gap Filling
#### 🐘 なぜジェネレータ(`yield`)が必須なのか？
100GBのログファイルを処理するとき、中級者までのPythonエンジニアは `readlines()` を使ってファイルを一括でリストに読み込みます。結果、サーバーは数秒でOOM（Out Of Memory）を起こして死にます。
データエンジニアは `yield` を使って「1行読んで処理し、捨てる」フローを作ります。これにより、メモリ消費量は常に「1行分(数バイト)」に抑えられ、100GBでもPBでも同じ16GBのPCで処理できるようになります。

### 3. 【アーキテクチャの視覚化】Visual Guide
```mermaid
graph TD
    subgraph "Bad (List Comprehension)"
        LCA[Read File] -->|"Load 10GB into RAM"| LCB[RAM Explodes]
        LCB --> LCC[Crash]
    end
    subgraph "Good (Generator)"
        GA[Read Line] -->|"Keep 1KB in RAM"| GB[Process]
        GB --> GC[Write/Yield]
        GC -.->|Loop| GA
    end
```

### 💡 この用語のまとめ (Key Takeaways)
* **ジェネレータ**: ビッグデータ時代において限られたメモリで巨大ファイルを裁くための必須文法。
* **型ヒント(Typing)**: データパイプラインの途中で「文字列が来るはずがINTが来た」等のバグを未然に防ぐ。
""",

"python/pandas.md": r"""# Pandas & Polars for Data Manipulation

### 1. 【エンジニアの定義】Professional Definition
> **Pandas**:
> メモリ上（シングルノード）で行うデータ分析のデファクトスタンダード。裏側はC/CythonとNumPyベース。
> **Polars**:
> Rustで書かれた、Pandasの次世代を担うマルチスレッド対応の超高速データフレームライブラリ。

### 2. 【0ベース・深掘り解説】Gap Filling
#### 🚦 Pandasの限界と `MemoryError`
Pandas最大の弱点は「手元のPCのRAMを超えるデータは扱えない」ことです。データ量が10GBあり、PCのメモリが16GBの場合、処理の中間マージ等でメモリ使用量は容易に3倍（30GB）に膨れ上がり、プログラムが落ちます。
ここでデータエンジニアは「クラウドに持っていきPySparkで分散処理する」か、「ローカルで爆速・省メモリのPolarsに載せ替える」かの設計判断（アーキテクト）を迫られます。

### 3. 【アーキテクチャの視覚化】Visual Guide
```mermaid
graph TD
    Data[Data Size 50GB]
    
    Data --> Pand[Pandas]
    Pand -->|"RAM枯渇"| Crash[OOM Crash]
    
    Data --> Polar[Polars LazyFrame]
    Polar -->|"クエリ最適化＆ストリーミング"| RAM[Low RAM Usage]
    
    Data --> Spark[PySpark]
    Spark -->|"10台のWorkerへ分散"| Dist[Success]
```

### 💡 この用語のまとめ (Key Takeaways)
* **Pandas**: 小〜中規模（数GB以下）のデータ探索用。
* **Polars**: ローカル最強の超高速＆遅延評価（Lazy）ライブラリ。
* **設計の要**: データのスケールに合わせて、ライブラリを適切に移行（マイグレーション）できるのがプロ。
""",

# --- Axis 2: PySpark Mastery ---
"pyspark/distributed.md": r"""# Distributed Computing & DataFrames

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
""",

"pyspark/lazy_eval.md": r"""# Action, Transformation & Lazy Evaluation

### 1. 【エンジニアの定義】Professional Definition
> **Transformation**:
> `filter()`, `select()`, `groupBy()` など、元データに対する「変形の指示」。実行しても計算はされない。
> **Action**:
> `show()`, `write()`, `count()` など、実際に結果を出力・保存する指示。ここで初めてSparkが動き出す。
> **Lazy Evaluation (遅延評価)**:
> Actionが呼ばれるまで計算を引き伸ばし、全体の処理フロー（DAG）を見てから最も効率の良い最短ルートで計算を実行する最適化の仕組み。

### 2. 【0ベース・深掘り解説】Gap Filling
#### 🔮 カタリスト(Catalyst Optimizer)の魔法
なぜこんな回りくどいことをするのでしょうか？
例えば「1億行のデータから、東京の人を絞り込んで（Filter）、その中で10件だけ抽出する（Limit）」というコードを書いたとします。
Pandasなら1億行すべて舐めてから10件出しますが、Spark（Lazy Evaluation）は「最終的に10件だけでいいのなら、最初からファイルの上から10人東京の人を見つけた瞬間にファイルを読むのをやめよう」と**計画を裏で書き換え**ます。
これが遅延評価による劇的なパフォーマンス向上の正体です。

### 3. 【アーキテクチャの視覚化】Visual Guide
```mermaid
sequenceDiagram
    participant Code as "Python Code"
    participant Engine as "Spark Engine (Catalyst)"
    
    Code->>Engine: df.filter(age > 20)
    Engine-->>Code: "了解。メモした" (Transformation)
    Code->>Engine: df.select(name)
    Engine-->>Code: "了解。メモした" (Transformation)
    Code->>Engine: df.show(5)
    Note over Engine: Action検知！<br/>メモを解析して最短ルートを編み出し、<br/>一気に実行。
    Engine-->>Code: [結果の5行]
```

### 💡 この用語のまとめ (Key Takeaways)
* **TransformationとAction**: スケジュールを立てるのが前、実行に移すのが後。
* **Catalyst Optimizer**: 勝手にコードを賢く書き換えてくれるSpark最強のコンパイラ。
""",

"pyspark/joins.md": r"""# Joins & Data Skew Optimization

### 1. 【エンジニアの定義】Professional Definition
> **Shuffle Join vs Broadcast Join**:
> Sparkでテーブル結合する際の2大戦略。巨大テーブル同士ならデータをノード間で行き交わせる（Shuffle）、巨大テーブルと極小テーブルなら極小の方を全ノードにコピーして配る（Broadcast）ことで高速化する。

### 2. 【0ベース・深掘り解説】Gap Filling
#### 🚧 シャッフル（通信）は悪である
Sparkは「各サーバーが独立して計算する」のが一番速いです。
JOIN（結合）を行うと、同じキーを持つデータを1箇所のサーバーに集めるため、ネットワーク上でテラバイト級のデータの移動（Shuffle）が発生します。ここでシステムが劇的に重くなります。

#### 📡 Broadcast Join の回避策
売上テーブル（1億行）と、都道府県マスタ（47行）をJOINする場合。
全ノード間でシャッフルするのは無駄の極みです。Sparkでは `broadcast(df_master)` と指定することで、47行の小さな表を**あらかじめ全てのWorkerのメモリにコピー（配布）**します。これによりワーカー間で通信することなくローカルだけでJOINが完了し、処理時間が1/10になります。

### 3. 【アーキテクチャの視覚化】Visual Guide
```mermaid
graph TD
    subgraph "Broadcast Join (爆速)"
        Master[都道府県マスタ 47行]
        Sales1[売上 (Node 1)]
        Sales2[売上 (Node 2)]
        
        Master -->|"コピーを配布 (ネットワーク通信極小)"| Sales1
        Master -->|"コピーを配布"| Sales2
        
        Sales1 -.->|"各ローカルでJoin"| Result1
        Sales2 -.->|"各ローカルでJoin"| Result2
    end
```

### 💡 この用語のまとめ (Key Takeaways)
* **Shuffle Join**: 巨大同士。通信が多くて重い。
* **Broadcast Join**: 巨大×極小。マスタデータを全台に配ることで通信を殺す最強テクニック。
* **Salting**: Skew（特定キーへの偏り）を乱数を足して人為的にバラす上級テクニック。
"""
}

# Ensure directories exist and write files
for filepath, content in content_dict.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated Phase 1 expansion modules: {len(content_dict)} files.")
