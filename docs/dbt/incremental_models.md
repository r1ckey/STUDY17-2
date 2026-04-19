# dbt Incremental Models & Merge Strategies
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
