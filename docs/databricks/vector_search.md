# Vector DB & MosaicML (RAG Architecture)
### 1. 【エンジニアの定義】Professional Definition
**Vector Database**: 文章や画像を高次元のベクトル（Embedding）に変換し、類似度計算（コサイン類似度など）を超高速で行うための専用データベース。LLMと組み合わせたRAG（Retrieval-Augmented Generation）のコアコンポーネント。
### 2. 【0ベース・深掘り解説】Gap Filling
現代のデータエンジニアには、単なるデータパイプラインだけでなく「社内ドキュメントを読み込ませて賢く回答するAI（RAG）」の構築も求められます。
社内のPDFをSparkでパース・チャンク分割し、Embeddingモデルを通してVector DB（Databricks Vector Search）にロードし、ユーザーの検索クエリに応答する「AIのインフラ」を組むのが今後のメインの仕事になります。
