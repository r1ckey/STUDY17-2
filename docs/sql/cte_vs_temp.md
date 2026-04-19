# CTEs vs Temporary Tables
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「可読性を重んじるあまり発生する超絶パフォーマンス劣化」**
データ分析界隈では「サブクエリのネストを避けるため、WITH句（CTE）を使おう」としばしば教わります。これによりコードは上から下へ流れるように美しくなります。
しかし、複雑なシステムにおいて **「同じCTEを後段のクエリで何度も使い回す」** 場合、エンジンによっては「CTE＝単なる文字列のマクロ置換」として解釈され、**参照されるたびに重い計算（スキャンとJOIN）が最初から再実行される** という致命的なパフォーマンス劣化を引き起こします。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Materialization（実体化）の境界線**
CTE（Common Table Expression）の裏側の挙動はDBエンジンによって大きく異なります。
* **PostgreSQL / MySQL**: 古いバージョンではCTEは必ず実体化（実行結果をメモリに持つ）されていましたが、近年は最適化により「インライン展開（毎回再計算）」されるケースが増えました。
* **Spark SQL / Databricks**: Spark Catalyst オプティマイザは、CTEが複数回呼ばれた場合、それが再計算すべきか、内部的にキャッシュすべきかを判断しようとしますが、複雑なJOINが絡むとしばしば「フルスキャン連発」という爆弾を抱えます。

この問題に対処する絶対的なアーキテクチャが **ローカル・マテリアライゼーション (Temporary Table)** です。
メモリまたは高速なディスク（SSD/Delta Cache）へ「1度だけ計算した結果」を物理的に書き出し、それに専用のインデックスや統計情報を付すことで、後段で10回参照されようが爆速でクエリが返るようになります。

```mermaid
graph TD
    classDef main fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef sub fill:#312e81,stroke:#8b5cf6,stroke-width:2px;
    classDef warn fill:#7f1d1d,stroke:#f87171,stroke-width:2px;
    
    subgraph "CTE Nightmare (Inline Expansion)"
        T[Huge Base Table]:::main
        C{CTE Definition}:::warn
        Q1[Query A using CTE]:::sub
        Q2[Query B using CTE]:::sub
        
        Q1 --> C --> T
        Q2 --> C --> T
        note right of T: Full scan happens TWICE
    end
```

### 3. 【実務への応用】Practical Application
* **CTEを使うべき時**: 単純なフィルタリングや、複雑なロジックを段階的に読ませるための「論理的分割」であり、なおかつ「1回しか参照されない」場合。
* **Temporary Tableを使うべき時**: 重いウィンドウ関数、数億行のハッシュ集計、複数のファクトテーブルの結合を含んでおり、かつその結果を後続で **「2回以上異なる角度で集計（再利用）する」** 場合。
