# Zero Trust Architecture
### 1. 【エンジニアの定義】Professional Definition
**ゼロトラスト**: 「社内ネットワークだから安全」という境界防御（VPN等）の考えを捨て、「すべてのアクセス（外部も内部も）を信頼せず、常に検証する」というセキュリティモデル。
### 2. 【0ベース・深掘り解説】Gap Filling
データエンジニアリングでは、DatabricksがADLSにアクセスする際に、VNet内（プライベートネットワーク）であっても必ず「IAMによる多要素認証状態の検証」「最小権限の原則（Least Privilege）」を適用する設計が求められます。
