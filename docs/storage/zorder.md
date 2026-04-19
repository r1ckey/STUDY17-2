# Z-Ordering & Data Skipping
### 1. 【課題解決のメカニズム】Mechanism of Problems
**フルスキャンの悪夢とパーティションの限界**
Date（日付）による物理フォルダ分割（Partitioning）は優秀ですが、「特定のProductID」や「特定のCustomerID」で検索をかけた場合、パーティションが切られていない軸での検索となるため、結局全ファイルを走査（フルスキャン）することになります。
かといって「ProductID」でパーティションを切ると、IDの種類が多すぎて「1ファイルのサイズが異常に小さく、フォルダが数千万個できるオーバーパーティション問題」を引き起こしクラスタが死にます。
このトレードオフを次元を超えて解決する数学的アルゴリズムが **Z-Ordering**（多次元クラスタリング）です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Z-Order Curve（Z階数曲線）と Data Skipping**
Databricks（Delta Lake）は裏側で各Parquetファイルごとに「このファイルにはID 100〜500のデータが入っている」という統計情報（Min-Maxステータス）を持っています。
これを利用し、クエリエンジンは「探しているIDが 999 の場合、このファイルはMin=100, Max=500の範囲だから絶対に存在しない」と判断し、**ファイルをS3から読むことすらスキップ**します（Data Skipping）。

しかし、データが完全にバラバラに散らばっていると、全ファイルのMin-Maxが重複してしまいスキップできません。
`OPTIMIZE table ZORDER BY (category, price)` を実行すると、エンジンは2つの次元（カテゴリと価格）の値をビット単位で交差（インターリーブ）させた「Z値」を計算し、多次元空間において近いデータ同士を同じParquetファイル内に物理的に固めて再配置します。
これにより、特定のカテゴリで検索しても、特定の価格帯で検索しても、圧倒的な精度でファイルをスキップできるようになります。

```mermaid
graph LR
    classDef box fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef skip fill:#334155,stroke:#475569,stroke-width:2px,stroke-dasharray: 5 5;
    
    Query(Query: WHERE ID = 800) --> Filter{Min-Max Check}
    Filter -->|File 1: Min=100, Max=500| F1[File Parquet 1]:::skip
    Filter -->|File 2: Min=600, Max=900| F2[File Parquet 2]:::box
    Filter -->|File 3: Min=1000, Max=1500| F3[File Parquet 3]:::skip
    
    note default
    Only File 2 is physically read from Object Storage.
    Incredible IO savings.
    end note
```

### 3. 【実務への応用】Practical Application
* **何をZ-Orderの対象にするか？**:
  カーディナリティ（値の種類）が中規模〜大規模で、よくダッシュボードやクエリの `WHERE` 句のフィルター条件や `JOIN` キーとして使われるカラムに対してZ-Orderをかけます。
* **アンチパターン**:
  すでにPartitioningしているカラム（例: `date`）に対してZ-Orderをかけるのは無意味です。また、Z-Orderに4つも5つもカラムを指定すると効力が激減し、ただのソート処理にCPU/DBUコストを浪費するだけになります（最大で2〜3個のカラムに絞るのが定石）。
