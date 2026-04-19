# Custom Materializations & Incremental
### 1. 【エンジニアの定義】Professional Definition
**Materialization**: dbtが書かれた `select` 文をデータベース上で「何として」具現化するか（View, Table, Incremental, Ephemeral等）の戦略。
### 2. 【0ベース・深掘り解説】Gap Filling
毎日100億行のテーブルを `table` （全件洗い替え）で処理していてはコストが破産します。
そこで `incremental` を使います。
`{% if is_incremental() %} where date >= (select max(date) from {{ this }}) {% endif %}`。
この数行を書くだけで、初回の実行時は全件CREATE TABLEし、次回からは「前回以降の差分だけ」をマージ（MERGE INTO等）する賢い処理に勝手に化けます。各DBMSの厄介なMERGE構文の差異を、dbtが吸収してくれるのが非常に強力です。
