import os
import glob
import time

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")

deep_content = {
    # ==========================
    # Axis 15: CI/CD & Testing
    # ==========================
    "cicd/data_testing.md": r"""# Data Testing with Great Expectations
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「コードはバグらないが、データがバグる」**
ソフトウェア工学のテスト（Unit Test）は、ロジックが正しいかを保証します。しかしデータエンジニアリングでは、「ロジックは完璧だが、システムに入力されたデータが腐っていたため、結果のダッシュボードが崩壊する」という「Silent Data Corruption（サイレントデータ破損）」が最大の敵です。
例えば、「売上金額が突然マイナスになっている」「必須のユーザーIDがNULLになっている」ことに誰より早く（できればパイプラインの途中で）気づき、不正データを隔離（Quarantine）し、エラーを飛ばす。これを宣言的に防ぐのが **Great Expectations (GX)** によるデータテストの仕組みです。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Expectations（期待値）の定義と検証**
Great Expectationsは、データに対する「契約（Data Contract）」をJSON形式で定義します。
* `expect_column_values_to_not_be_null(column="user_id")`
* `expect_column_values_to_be_between(column="age", min_value=0, max_value=120)`

コード内に直接 `if value < 0:` を書くのではなく、検証ルールを外部に切り出すことで、以下のアーキテクチャが実現します。
1. **Profiler**: 最初は過去のデータから自動的にルールを推論させる。
2. **Validator**: パイプライン（Airflow等）の中で Databricks / Spark と結合してデータを取り込む「直前・直後」に検証セットを起動する。
3. **Data Docs**: 検証結果がいかに素晴らしいかを人間に見せるための静的HTMLドキュメント（Data Quality Dashboard）が自動生成される。

### 3. 【実務への応用】Practical Application
* **Circuit Breaker パターン**:
  パイプラインの途中でデータ品質のテストがコケた場合、そのまま後段（Gold層やBI）に流すのではなく、AirflowなどでAirflowExceptionを発火させパイプラインを「強制停止」させる（Circuit Breaker）ことが重要です。狂ったデータをユーザーに見せて信頼を失うくらいなら、ダッシュボードが「昨日のデータから更新されていません」と表示される方が何倍もマシです。
""",

    # ==========================
    # Axis 16: SRE & Observability
    # ==========================
    "ops/dora_metrics.md": r"""# DORA Metrics & Data Reliability Engineering
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「何となく遅い」「何となく不安」を撲滅する**
データ基盤の保守において、経営層から「システムの信頼性はどうなっているか？」と聞かれた時、「頑張って監視しています」と答えるのはプロフェッショナルではありません。
Google（DORA）が提唱した「4つのキー・メトリクス」をデータチームに落とし込み、システムのパフォーマンスとチームの開発生産性を定量化して追跡するフレームワークが **Data Reliability Engineering (DRE)** です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Four Key Metrics for Data Teams**
1. **Deployment Frequency (デプロイ頻度)**: 「データパイプライン（dbt, Airflow等）の変更を月に何回本番環境に出しているか」。多ければ多いほど、チームが無駄な官僚的プロセスを持たず、CI/CDでアジャイルに動けている証拠です。
2. **Lead Time for Changes (変更のリードタイム)**: 「ユーザーから『このカラムを追加して』と言われてから、本番に反映されるまでの時間」。
3. **Change Failure Rate (変更障害率)**: 「デプロイした結果、本番のジョブが落ちて手戻りになった割合」。低いほどテスト（CI）が充実している証拠です。
4. **Time to Restore Service (平均復旧時間 - MTTR)**: 「障害を検知してから直るまでの時間」。

これを支えるのが、SLO（Service Level Objective）です。「我々のデータパイプラインは、毎朝9時までに最新データを99.9%の確率で提供する」という宣言（Data SLA）を行い、それに違反した時間（Error Budget）が尽きた場合、全メンバーが新機能開発を停止してインフラ改善に専念するという規律が求められます。

### 3. 【実務への応用】Practical Application
* **Data Lineage (データ・リネージ) によるMTTR削減**:
  ダッシュボードの表示がおかしいとクレームが来た際、「どのテーブルが元凶か」を探るのに半日かかっていてはMTTR（復旧時間）は改善しません。Databricks Unity Catalogなどの機能を用い、どのカラムがどの元テーブルから流れてきたかの「血統（Lineage）」を自動でグラフ化しておくことで、原因特定時間を瞬時に圧縮することがDREの要となります。
"""
}

# 写し出し
for filepath, content in deep_content.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated {len(deep_content)} deep modules for Batch 5 (CI/CD & Observability).")
