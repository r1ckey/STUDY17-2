# Advanced Window Functions & Analytical SQL
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
