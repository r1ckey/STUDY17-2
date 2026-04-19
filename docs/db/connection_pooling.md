# Connection Pooling
### 1. 【エンジニアの定義】Professional Definition
**コネクションプーリング**: データベースへの接続（TCPハンドシェイク+認証）は非常にコストが高いため、あらかじめ複数の接続を確立して「使いまわす」ための仕組み（PgBouncerなど）。
### 2. 【0ベース・深掘り解説】Gap Filling
PythonスクリプトからAzure SQLに1行挿入するたびに `connect()` を呼んでいると、その通信のオーバーヘッドのせいで処理能力が1/1000になります。さらに、DB側も「同時接続数上限（Max Connections）」に達してシステム全体がダウンします。
