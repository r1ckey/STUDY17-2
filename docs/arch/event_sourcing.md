# Event Sourcing & CQRS
### 1. 【エンジニアの定義】Professional Definition
**Event Sourcing**: 現在の「状態（残高1000円）」を保存するのではなく、「発生したイベントの歴史（+5000円, -4000円）」をすべて保存し、そこから現在の状態を計算するアーキテクチャ。
**CQRS**: 読み込み（Query）と書き込み（Command）のデータベース（モデル）を完全に分離・非同期化する設計手法。
### 2. 【0ベース・深掘り解説】Gap Filling
銀行システムやECサイトのカートなどで多用されます。イベント（履歴）さえあれば、過去の任意の時点（Time Travel）にシステムを完全復元できるのが強みです。DWHやDelta LakeのTransaction Logの根本的な思想はこれに基づいています。
