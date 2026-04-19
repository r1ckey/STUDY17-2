# Apache Airflow: DAG Mechanics & Idempotency
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「Cronシェルスクリプトの限界と依存性の罠」**
データパイプラインを「毎朝4時に実行する」という要件に対し、未だにレガシーな現場ではLinuxの `cron` とシェルスクリプトを使っています。
しかし、Aの処理が終わらないとBを実行できない（依存関係）、Aが途中でコケたらBから再開させたい（リトライ）、過去30日分のデータを手動で再計算したい（バックフィル）。こうなった瞬間、`cron` ではカオス（夜中にエンジニアが手動でスクリプトを叩き続ける地獄）に陥ります。
これを解決するため、すべてのタスク群を数学的な **DAG (有向非巡回グラフ)** として表現し、ステートマシンのように完全管理するのが Apache Airflow です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Execution Date の真実と冪等性 (Idempotency)**
Airflowの最も根源的であり、初心者が100%つまずく罠が `Execution Date (logical_date)` の概念です。
「2026年4月20日 00:00」にスケジュールされた `Daily` のジョブは、**「2026年4月20日 00:00」には実行されません。** 実際にはその24時間後の「2026年4月21日 00:00」になって初めて予約が発火します。
なぜなら、データエンジニアリングにおける「4/20の実行枠」とは「4/20の00:00 〜 23:59 までの全データが出揃ったことを確認してから、それを対象領域（マクロ変数 `{{ ds }}` 等）として処理を行う」という思想に基づいているからです。

```mermaid
graph TD
    classDef success fill:#1e293b,stroke:#10b981,stroke-width:2px;
    classDef fail fill:#7f1d1d,stroke:#ef4444,stroke-width:2px;
    classDef pending fill:#312e81,stroke:#6366f1,stroke-width:2px,stroke-dasharray: 4 4;
    
    A[Extract API Data]:::success --> B(Transform dbt Silver):::fail
    B --> C(Load Data Mart Gold):::pending
    
    note default
    Task B failed. 
    Airflow will safely retry B, and completely block C from starting.
    Idempotent design ensures retrying B won't corrupt data.
    end note
```

### 3. 【実務への応用】Practical Application
* **冪等性 (何度やっても結果が同じ) の強制限界**:
  Airflowのタスクは例外で死ぬことが日常です。タスクの中で `INSERT INTO table` と書いていると、リトライした際にデータが二重に増殖します。Airflowのタスクを設計する絶対ルールとして、タスク内のすべての処理は `DELETE FROM table WHERE date = '{{ ds }}'; INSERT INTO ...` のように、「開始前に必ずその日の出力領域を綺麗に吹き飛ばす（UPSERT/OVERWRITE）」か、そもそも追記のみで影響がない構造になっていなければなりません。これができなければ、オーケストレーションは破綻します。
