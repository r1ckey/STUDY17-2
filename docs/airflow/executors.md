# Airflow Executors (Celery vs Kubernetes)
### 1. 【エンジニアの定義】Professional Definition
**Executor**: Airflowが解釈したDAG内の各タスクを、「どのマシンのどのプロセスで実行するか」を決定する実行エンジン。
### 2. 【0ベース・深掘り解説】Gap Filling
* **LocalExecutor**: Airflowサーバー内でマルチプロセスで動かす。安価だが負荷が高いと死ぬ。
* **CeleryExecutor**: 複数のワーカーノード（別のVM）を用意し、Redis等をキューにしてタスクを投げるタスク分散の王道。ワーカーの維持にお金がかかる。
* **KubernetesExecutor**: タスク1つにつき、K8s上に新しく1つのPodを立ち上げて実行し、終わったらPodを捨てる。実行ごとの環境分離（ライブラリ衝突回避）と、完全なオートスケールが可能。モダンデータスタックにおける究極のオーケストレーション。
