# Window Functions (The Real Power of SQL)
### 1. 【エンジニアの定義】Professional Definition
**Window関数**: 行を集約（GROUP BY）して行数を減らすのではなく、元の行数を保ったまま、指定した「窓（Window）」の範囲内で集計や順位付けを行う高度なSQL関数。
### 2. 【0ベース・深掘り解説】Gap Filling
「顧客別の初回購入日からの経過日数を出したい」「直近3回分の移動平均を出したい」。これらをJOINやSubQueryで書くとクエリが地獄になりますが、`OVER (PARTITION BY user_id ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` と書くことで、RDBMSやSparkはソート1回だけで爆速で計算してくれます。
