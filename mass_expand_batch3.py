import os
import glob
import time

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")

deep_content = {
    # ==========================
    # Axis 08: Advanced SQL Mastery
    # ==========================
    "sql/cte_vs_temp.md": r"""# CTEs vs Temporary Tables
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
""",

    "sql/window_functions_advanced.md": r"""# Advanced Window Functions & Analytical SQL
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「自己結合 (Self-Join) は死を招く」**
「過去3日間の移動平均を出したい」「各ユーザーについて、前回購入日との差分を出したい」。
このようなレコード間の比較を行う要件に対し、同じテーブルを日付をズラして `JOIN`（自己結合）するクエリは、直積（レコード数 × レコード数）に近い爆発を起こし、1万件のデータでも数分かかる事態を引き起こします。これを「ソート（並び替え）1回」だけでO(N log N) の速度で解決するのが、SQLが到達した最高峰の関数群である**Window関数**です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Partition, Order, Frame (窓の定義)**
Window関数の真の力は、`OVER()` 句の中にあります。これは3つのフェーズでレコードを切り出します。
1. **PARTITION BY**: 全データから、計算対象のグループ（例：ユーザー単位）の壁を作ります（グループ間の影響を遮断）。
2. **ORDER BY**: 壁の中で時系列等に並び替えます。
3. **ROWS BETWEEN**: ここが最重要です。「現在の行（CURRENT ROW）」を起点に、物理的に「何行前（PRECEDING）から何行後（FOLLOWING）まで」を計算に含めるかの「窓（フレーム）」をスライドさせます。

自己結合を用いずに、前回の購入日（`LAG`）、初回からの累計売上（`SUM() OVER (ROWS UNBOUNDED PRECEDING)`）、3日移動平均などを、たった1回のフルスキャンでメモリ上で実行します。

### 3. 【実務への応用】Practical Application
* **セッション解析 (Gaps and Islands)**:
  「ユーザーが30分以上アクションしなかったら、別のWebセッションと見なす」という複雑な分析も、Window関数 (`LAG`等) で時間差分を出し、その差分が30分を超えたらフラグ（1）を立て、そのフラグを累積和 (`SUM() OVER`) することで、独自ルールの「セッションID」をSQL一発で生成できます。
* **Qualify句の活用**:
  「各ユーザーの最新のログ『だけ』を抽出したい」場合。従来のSQLでは、サブクエリで `ROW_NUMBER()` を振り、一番外側で `WHERE rn = 1` で絞る必要がありました。Databricks等では `QUALIFY ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY time DESC) = 1` と書くことで、ネスト不要で直接絞り込むことができます。
""",

    # ==========================
    # Axis 09: Modeling Architectures
    # ==========================
    "modeling/scd_types.md": r"""# Slowly Changing Dimensions (SCD Types 1, 2, 3)
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「顧客が引っ越した時、過去の売上はどう扱うか？」**
分析の世界において、事実（いつ・何が・いくら売れたか）は不変（Immutable）ですが、それに紐づくマスターデータ（ユーザーの住所、部署名、担当者）は時間が経つと変化します。東京の顧客が大阪へ引っ越ししたとします。マスターテーブル上の住所を「大阪」にUPDATE（上書き）してしまうと、「去年、東京でどれくらい商品が売れたのか？」という地域別売上分析を行った際、過去の売上まで「大阪」として集計されてしまうという致命的な分析エラーが発生します。
この「ゆっくりと変化するマスター（SCD）」をどのようにデータウェアハウスに保存するかが、モデリングの永遠のテーマです。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**履歴管理の3大アプローチ**
データモデリングでは、ビジネス要件に合わせて以下のパターンを使い分けます。
* **SCD Type 1 (上書き)**:
  単なるUPDATEです。古い住所は消滅します。（適用例: 名前の誤字訂正など、履歴を追うことにビジネス的価値がないもの）
* **SCD Type 2 (履歴の完全保存 - 最も重要)**:
  住所が変わった際、古いレコードは残したまま「有効終了日（Valid_To）」を昨日で締め、新しいレコードを「有効開始日（Valid_From）=今日」からとしてINSERT（追記）します。
  これにより、昨年の売上データは「古いバージョンの顧客レコード」へJOINされ、今年の売上は「新しい顧客レコード」にJOINされるため、時系列を完璧に再現できます。
* **SCD Type 3 (代替列の追加)**:
  1行の中に「現在の住所」と「過去の住所」という列を両方持ちます。履歴は1世代前までしか追えませんが、構造がシンプルです。（適用例: 「昨年の所属部署」と「今年の所属部署」など）

### 3. 【実務への応用】Practical Application
* **Surrogate Key (代替キー) の必須化**:
  SCD Type 2を実装する場合、ビジネスキー（例: Email）は「同一人物」を表しますが、一意（Unique）ではなくなります（東京時代と大阪時代で2レコード存在するため）。そのため、必ず `Customer_SK (Surrogate Key: 無意味な連番やUUID)` を主キーとして付与し、Factテーブル（売上など）からはこのSKに向けて結合を行う設計が絶対条件となります。
""",

    # ==========================
    # Axis 10: dbt & Integration
    # ==========================
    "dbt/incremental_models.md": r"""# dbt Incremental Models & Merge Strategies
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「毎回数テラバイトを全再構築することの崩壊」**
1日1億件のログが増え続けるシステムを想像してください。dbt の強みは「SELECT文を書くだけで、あとは勝手にテーブル化 (Table Materialization) してくれる」ことですが、テーブルとして定義した場合、毎朝パイプラインが動くたびに「1年分の数十億件のデータを読み込み、全消去（DROP）し、再計算して挿入する」という狂気の沙汰（Full Refresh）が行われます。
コンピュートコストの爆発と処理時間の長時間化を防ぐため、「昨日増分した1億件だけをすくい出し、既存のテーブルに賢く合併させる」のが Incremental Model の至上命題です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Is_Incremental マクロとマージ戦略**
dbtでは、`materialized='incremental'` 設定を行うと、裏側で極めて高度な動きをします。

```sql
{{ config(materialized='incremental', unique_key='log_id') }}

SELECT * FROM {{ ref('raw_logs') }}
{% if is_incremental() %}
  -- このクエリは「既にテーブルが存在し、差分更新モードの時」だけ挿入される
  WHERE event_time > (SELECT MAX(event_time) FROM {{ this }})
{% endif %}
```

このコードに対し、DWH側（DatabricksやSnowflake）で採用される戦略（Strategy）には2つの極北があります。
1. **Append-Only（追記のみ）**: 重複チェックをせず、ただ `INSERT` する。最速ですが、ログが二重で送られてきた場合に重複が残ります。
2. **Merge（完全な統合）**: `unique_key` に基づいて、裏側で `MERGE INTO` 構文を生成します。既存のIDがあればUPDATE、無ければINSERT（UPSERT処理）を行います。一意性を保証しますが、テーブル全体のインデックスを舐めるためI/Oコストが高くなります。

### 3. 【実務への応用】Practical Application
* **Partitioned Merge (挿入範囲の限定)**:
  数百億件のDeltaテーブルへ `MERGE` をかけると、たとえ数十件の差分更新であっても裏側で極端に遅くなる場合があります。実務では `incremental_strategy='merge'` に加え、`partition_by='date'` のようなパーテション情報を提供することで、dbtに「過去3日分のパーティションだけしか探索しない」限定的マージを生成（Dynamic Partition Overwrite）させ、コストを1/100に圧縮することがアーキテクトの仕事です。
""",

    # ==========================
    # Axis 11: Orchestration & Event
    # ==========================
    "airflow/dag_mechanics.md": r"""# Apache Airflow: DAG Mechanics & Idempotency
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
"""
}

# 1. 書き込み
for filepath, content in deep_content.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
        
print(f"Generated {len(deep_content)} extremely deep modules for Batch 3.")
