# Advanced MLflow & MLOps Pipelines
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「あの時のモデル、どうやって作ったっけ？」**
データサイエンスの現場で最大の技術的負債となるのが「モデルの再現性の欠如」です。ローカルのJupyter Notebookでハイパーパラメータを手打ちして作成したモデルは、半年後に精度が劣化して再学習しようとしたとき、正確なパラメータや前処理コードが見つからず、最悪ゼロから作り直しになります。
MLflow は、この「実験の記録（Tracking）」「コードと環境のパッケージ化（Projects）」「モデルの管理手段（Models）」「レジストリ（Model Registry）」の4本柱で、誰がいつ作ってもモデルを確実に再現し、シームレスに本番へデプロイ可能にする MLOps の世界標準フレームワークです。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Autologging と Model Signatures**
Databricks上で動作する `mlflow.autolog()` がどのように裏側で動いているのか。
実は、Scikit-learn や XGBoost 等のライブラリ側の `fit()` や `predict()` メソッドが実行された瞬間に、MLflow はそれらの呼び出しをフック（インターセプト）し、使用されたハイパーパラメータ、学習時間、精度メトリクスなどを裏のストレージに自動保存します。

注目すべきは `Model Signature`（モデルの入力と出力のスキーマ定義）です。モデルを保存する際、入力データのデータ型（推論時には Int ではなく Float で来る、など）を厳格にJSONスキーマとして焼き込みます。これにより、本番のREST APIで予期せぬデータ型のJSONがPOSTされた瞬間に、モデル本体を走らせることなくMLflowレイヤーでエラーとして弾く（フェイルファースト機能）が実現されます。

### 3. 【実務への応用】Practical Application
* **Feature Storeとの統合**:
  MLflow単体では「学習時のデータ（Feature）」の値は管理しません。Databricksでは Feature Store と MLflow を連携（`FeatureStoreClient.log_model`）させます。これにより、モデルと一緒に「この特徴量は Feature Store のどのテーブルから引っ張ってくるか」というマッピング情報がパッケージ化されるため、リアルタイム推論時のAPI内部ロジックを100行以上削減できます。
* **アンチパターン**:
  実務において「ただのファイル（Pickle）」としてモデルをADLSに保存するのは絶対にNGです。Pythonのバージョンや依存ライブラリの微小な差異で、本番環境でUnpickleに失敗したり予測値が狂ったりするため、MLflowが生成する `conda.yaml` や `requirements.txt` と一緒に完全にサンドボックス化して保存する運用が必須です。
