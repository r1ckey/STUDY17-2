# TCP/IP Fundamentals
### 1. 【エンジニアの定義】Professional Definition
**TCP (Transmission Control Protocol)**: 手を繋いで通信する（3-way Handshake）。「届いたか？」を確認し、損失があれば再送する信頼性の高いプロトコル（HTTPやDB接続はすべてコレ）。
**UDP (User Datagram Protocol)**: 投げっぱなしの通信。欠損しても気にしないが圧倒的に速い（動画配信やオンラインゲーム）。
### 2. 【0ベース・深掘り解説】Gap Filling
KafkaやSpark等での「TimeoutException」。TCPの特性上、大量のデータを送っているとネットワーク機器がパケットをドロップし、再送待ち（Retransmission）が発生するため、一時的にレスポンスが停滞します。この振る舞いを理解しないと、単純にAPIタイムアウト値をむやみに延ばすだけの対症療法になってしまいます。
