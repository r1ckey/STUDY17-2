import os
import glob
import json
import time

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")

deep_content = {
    # ==========================
    # Axis 05: Databricks Deep Compute
    # ==========================
    "databricks/mlflow_deep.md": r"""# Advanced MLflow & MLOps Pipelines
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
""",

    "databricks/photon_execution.md": r"""# Photon Execution Engine (Vectorized C++)
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「JVMの壁」と次世代データ処理**
Apache Sparkは長らくビッグデータ処理の覇者でしたが、データ量がペタバイト級に跳ね上がり、かつ複雑な計算（Hash JoinやRegex Extract）が頻発する現代において、「Java仮想マシン (JVM)」上で動作することが巨大な足かせとなりました。
Row（行）単位での処理によるCPUのキャッシュミス、オブジェクトのシリアライズ/デシリアライズの負荷、そして大量のメモリを消費して定期的に処理を止めるGC（Garbage Collection）。これらJVM固有の遅延要因を完全に根絶するため、Databricksが底辺からC++でゼロスクラッチした処理エンジンが Photon です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Volcano Model から Vectorized Execution へ**
従来のSpark（や古いRDBMS）は Volcano Model と呼ばれ、1行ずつ評価していました（`next_row()`）。
Photon は、1行ではなく数千行（バッチ）をメモリ上の連続したアレイ（Array）領域に展開し、現代のCPU（Intel/AMD/ARM）に備わっている SIMD (単一命令・複数データ) を使って、一回のCPUサイクルで配列全体の演算を終わらせます。

```mermaid
graph TD
    classDef spark fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef photon fill:#312e81,stroke:#8b5cf6,stroke-width:2px;
    
    subgraph "Legacy Spark (JVM)"
        A[Driver Plan]:::spark --> B[JVM Executors]:::spark
        B --> C[Row-by-Row Iterator]:::spark
        C --> D[Add 1 + 2]:::spark
    end
    
    subgraph "Photon Engine (Native C++)"
        A2[Driver Plan]:::photon --> B2[Detect Photon Compatibility]:::photon
        B2 --> C2[C++ Layer (Off-Heap)]:::photon
        C2 --> D2[Vectorized SIMD Add [1,5...] + [2,10...]]:::photon
    end
```

### 3. 【実務への応用】Practical Application
* **Photonの適材適所**:
  Photonは「すべての処理をC++でやる」わけではなく、Sparkプランの中で、Photonが対応しているノード（HashJoin, AGG 等）だけを部分的にC++に任せ、非対応の機能（一部のカスタムUDF等）はJVMのSparkに戻す（Fallback）、というハイブリッドで動きます。UDFを多用すると、C++とJVMの間でデータ変換が多発し、かえって遅くなるため、極力Sparkの組み込み関数を使う（Pyspark.sql.functions）ことが、Photonの恩恵を最大化する秘訣です。
""",

    # ==========================
    # Axis 06: Dist System Theory
    # ==========================
    "dist/cap_theorem.md": r"""# CAP Theorem & PACELC 
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「絶対に壊れず、常に最新で、絶対に応答するシステム」は存在しない**
NoSQLやNewSQLなど様々なデータベースが登場し、データストアの選定がシステム設計の要となっています。しかし「要件は全部」と言って完璧なDBを探求するのは素人です。
分散システム（データを複数のサーバーに分けて置くこと）において、物理法則の如く立ちはだかるのが CAP 定理です。
一貫性（**C**onsistency：全員が同じ最新データを見る）、可用性（**A**vailability：常にシステムが応答する）、分断耐性（**P**artition Tolerance：ネットワークが切断されてもシステムが動き続ける）の3つのうち、原理的に同時に満たせるのは2つ（実質的にはPを前提として、CかAを選ぶ）しかないという残酷な事実です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**PACELC理論による完全なモデル化**
CAP定理はさらに進化し、PACELC定理として現代の基盤設計を支配しています。
`If Partition (P), how does the system trade off Availability and Consistency (A and C); Else (E), when the system is running normally, how does it trade off Latency and Consistency (L and C)?`
ネットワークが切れていない平時 (Else) であっても、データを遠くのノードへ完璧に複製（Consistency）しようとすれば、応答速度が遅くなる（Latency。LCトレードオフ）。

```mermaid
graph LR
    classDef C fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef A fill:#312e81,stroke:#8b5cf6,stroke-width:2px;
    
    subgraph "Partition Detected (Network Failure)"
        P{Choose:} -->|CP| CP[Wait for Sync: Timeout Error]:::C
        P -->|AP| AP[Return Old Data: No Error]:::A
    end
    
    subgraph "Normal Operation (Else)"
        E{Choose:} -->|EC| EC[Sync All Replicas: High Latency]:::C
        E -->|EL| EL[Async Replica: Low Latency]:::A
    end
```

### 3. 【実務への応用】Practical Application
* **データベース選定の意思決定**:
  * **RDBMS (PostgreSQL, MySQL等)**: 典型的な **CA / CP** 志向。障害が発生すると書き込みをロックしエラーを返しますが、金銭データなど「古すぎるデータや壊れたデータが見えると一発アウト」なシステムで採用します。
  * **Cassandra / DynamoDB (デフォルト)**: 典型的な **AP / EL** 志向。障害が起きてもとりあえず応答し（場合によっては数分前の古いデータ）、裏で非同期に同期します。秒間数万のアクセス（閲覧履歴やIoTログ）をさばくにはこれしかなく、最終的にデータが揃えばOK（Eventual Consistency）というドメインで採用します。
""",

    # ==========================
    # Axis 07: Database Mechanics
    # ==========================
    "db/mvcc_internals.md": r"""# MVCC (Multi-Version Concurrency Control)
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「誰かが読んでいる時に書き込むとロックされる」からの解放**
古いRDBMSでは、User A が巨大なテーブルを `SELECT` して読み取っている最中に、User B がそのテーブルの一部を `UPDATE` しようとすると、ロック（Table Lock / Row Lock）に引っかかって待たされる（またはその逆）のが常識でした。
データ分析においては、数時間かかる巨大なSELECTが頻繁に走ります。これが業務（UPDATE）を止めてしまう問題を、ロックを一切使わずに解決したのがMVCC（多版同時実行制御）です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**トランザクションIDと「世代」の管理**
PostgreSQLやDatabricksのDelta LakeなどのMVCCアーキテクチャでは、データを `UPDATE` または `DELETE` しても、**元のデータの実体は決して消しません（物理削除しない）**。
代わりに、新しく書き変わった「新バージョン（新行）」を追記し、各行に「このデータを作ったトランザクションID（Xmin）」と「このデータを消したトランザクションID（Xmax）」を不可視カラムとして持たせます。
User AがSELECTを叩いた瞬間、システムはUser A専用の「スナップショット（その瞬間の世界の写真）」を提供します。User Bが裏で最新バージョンをバンバン追記しようと、User Aには「自分がSELECTを打った瞬間に有効だった古いバージョン」だけが見え続けます。「読み取りは書き込みをブロックせず、書き込みも読み取りをブロックしない」究極の並行処理の完成です。

### 3. 【実務への応用】Practical Application
* **VACUUM戦略（消えない亡霊データの掃除）**:
  MVCCはロック問題を完璧に解決しましたが、最大の代償として「誰からも見られなくなった古いバージョン（ゴミ）」が永遠にディスク上に残存し、ストレージを食いつぶしクエリを徐々に遅くする（Bloat: 肥大化）という呪いをもたらしました。
  データエンジニアの急務は、PostgreSQLに対する適切な `autovacuum` チューニング、あるいは Delta Lake に対する `OPTIMIZE` および `VACUUM RETAIN 168 HOURS` のスケジュール実行化であり、これを見落とすと数ヶ月後にシステムがシステム領域不足で完全にダウンします。
"""
}

for filepath, content in deep_content.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
        
print(f"Generated {len(deep_content)} extremely deep modules for Batch 2.")

# Rebundle via neutralize_text
import re

html_path = os.path.join(base_dir, "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'src=\"dashboard_data\.js\?v=\d+\"', f'src=\"dashboard_data.js?v={int(time.time())}\"', html)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
