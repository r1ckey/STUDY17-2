# Joins & Data Skew Optimization

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
