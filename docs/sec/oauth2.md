# OAuth 2.0 & OIDC
### 1. 【エンジニアの定義】Professional Definition
**OAuth 2.0**: パスワードを渡すことなく、AというアプリがBというサービス（Google等）にアクセスする「一時的な権限（トークン）」を付与する認可フレームワーク。
**OIDC (OpenID Connect)**: OAuth 2.0の上に「認証（あなたは誰か）」の仕組みを被せたもの。
### 2. 【0ベース・深掘り解説】Gap Filling
エンタープライズのデータパイプライン構築では、「ID/Passwordをソースコードに埋め込む」のは犯罪に近いです。AzureではService Principalなどを通じてOAuth 2.0の仕組みを利用し、数時間で期限切れになる「Access Token」を使ってDatabricksからADLSへセキュアにアクセスします。
