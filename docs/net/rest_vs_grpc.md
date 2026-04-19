# REST APIs vs gRPC / GraphQL
### 1. 【エンジニアの定義】Professional Definition
**REST**: HTTPプロトコル上でJSONなどのテキストをやり取りする標準的アーキテクチャ。遅いがシンプル。
**gRPC**: HTTP/2上でProtocol Buffers（Protobuf）というバイナリ形式でやり取りするGoogle開発の超高速RPC。
**GraphQL**: クライアントが「欲しいデータの構造」を指定できるため、無駄なデータ通信（Over-fetching）を防げるFacebook開発のAPI言語。
### 2. 【0ベース・深掘り解説】Gap Filling
データエンジニアとしてマイクロサービス間のデータ通信を設計する際、RESTで毎秒10万件のJSONをパースしているとCPUが燃え尽きます。内部システム間は圧倒的に軽く高速なgRPC（バイナリ通信）を選ぶのがモダンシステムの鉄則です。
