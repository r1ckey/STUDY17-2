import os
import glob
import time

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")

deep_content = {
    # ==========================
    # Axis 12: Azure Security VNet
    # ==========================
    "azure/private_link.md": r"""# Azure Private Link & VNet Architecture
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「パブリッククラウド」という本質的なリスク**
AWSのS3やAzureのADLS、DatabricksといったPaaSリソースは、デフォルトでインターネット上のグローバルなパブリックIPアドレスを持ちます。ファイアウォール（IP制限）で「社内のIPしか通さない」と設定していても、データ自体はインターネットという公道を通るため、経路での傍受リスクや、設定ミスによる全世界からのデータ漏洩（S3バケットの公開事故など）という致命的なインシデントに直結します。
エンタープライズや金融機関の審査において、「公道を通るな、専用の地下トンネルを掘れ」という要件を完璧に満たす技術が **Azure Private Link (Private Endpoint)** です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Private Endpoint と DNSのオーバーライド**
Private Endpointを設定すると、PaaS（例えばADLS）に対して、あなたのVNet（プライベートネットワーク）内の「ローカルなIPアドレス（10.0.1.5等）」が物理的に刺さります。
しかし、コード内で `https://myatalake.blob.core.windows.net` にアクセスした際、PCは通常「グローバルIP」を解決してそちらへ向かおうとします。そこで必須になるのが **Private DNS Zone** の連携です。
VNetの内部からアクセスした時だけ、DNSサーバーが「そのURLの行き先はグローバルの 52.x.x.x ではなく、手元の 10.0.1.5 だよ」と嘘のルーティング（DNS上書き）を行います。これにより、Microsoftの超高速なバックボーン網を通る完全に閉ざされたプライペート通信が完成します。

```mermaid
graph TD
    classDef vnet fill:#1e293b,stroke:#3b82f6,stroke-width:2px;
    classDef dns fill:#312e81,stroke:#8b5cf6,stroke-width:2px;
    classDef paas fill:#7f1d1d,stroke:#f87171,stroke-width:2px;
    
    subgraph "Your Secure Azure VNet"
        VM[Databricks Worker <br/> IP: 10.0.2.10]:::vnet
        PE[Private Endpoint <br/> IP: 10.0.2.20]:::vnet
        DNS((Private DNS Zone <br/> Resolves to 10.0.2.20)):::dns
    end
    
    VM -->|Query URL| DNS
    VM -->|Data Flow Bypass Public Internet| PE
    PE -->|Microsoft Backbone| Storage[Azure Data Lake Gen2]:::paas
    
    Internet((Public Internet)) -.->|Access Blocked| Storage
```

### 3. 【実務への応用】Practical Application
* **Databricks NPIP (No Public IP) ワークスペース**:
  高度なセキュリティ要件では、Databricksのワーカーノード（VM）自体にパブリックIPを付与しない運用（NPIP）が基本です。しかしNPIPにすると、VMがインターネット上の「Databricksのコントロールプレーン」にアクセスできなくなり、ジョブが起動しません。これを解決するため、Databricksの「Control Plane API」と「Web Auth」に対してもPrivate Endpointを個別に構成し、完全にVNetの中だけで閉じたクラスタ通信網（Secure Cluster Connectivity）を構築する設計力が求められます。
""",

    # ==========================
    # Axis 13: Identity & Web APIs
    # ==========================
    "sec/oauth2_oidc.md": r"""# OAuth 2.0 & OpenID Connect (OIDC)
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「パスワードを渡すリスク」からの脱却**
外部の業務アプリケーションA（例: 経費精算アプリ）が、あなたの会社のカレンダーデータにアクセスして出張予定を取得したいとします。大昔は「AにカレンダーのIDとパスワードを登録させ、Aがあなたの代わりにログインする（Basic認証）」という恐ろしいことが行われていました。Aがハッキングされたら、あなたのすべての権限が奪われます。
「パスワードは絶対に渡さない。代わりに、カレンダーを見る権限だけを制限付きで作った『入場券（Token）』を渡す」という認可の仕組みが **OAuth 2.0** であり、その上に「あなたは誰か」という認証の仕組みを乗せたのが **OpenID Connect (OIDC)** です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**JWT (JSON Web Token) の検証メカニズム**
現代のAPIアクセスにおいて、データのやり取りはJWTという規格でパッケージ化された文字列で行われます。
JWTは「ヘッダー.ペイロード.シグネチャ」の3つのドット区切りで構成されています。ペイロード（中身）には `{"role": "data_engineer", "exp": 1700000000}` といった権限がBase64で書かれているだけなので、**誰でもデコードして中身を読めます（暗号化とは違います）**。
ではなぜ安全なのか？それは最後の「シグネチャ（署名）」にあります。
認証サーバー（Azure Entra ID 等）の非公開の「秘密鍵」でペイロードのハッシュを暗号化しているため、途中で誰かがペイロードの権限を `"role": "admin"` に書き換えたとしても、APIサーバー側が提供されている「公開鍵」を使ってハッシュを検証した瞬間に「署名が合わない＝改ざんされている」と見抜き、一瞬で弾き返すことができるからです。

### 3. 【実務への応用】Practical Application
* **M2M (Machine to Machine) と Client Credentials Flow**:
  ユーザーがブラウザでログインボタンを押すのではなく、「Airflowがdbt CloudのAPIを叩く」「Databricksが外部のREST APIからデータを夜間に収集する」といったサーバー間のバッチ処理において、人間の介入は不可能です。ここでは `Client ID` と `Client Secret`（または証明書）を用いてバックグラウンドで一瞬でトークンを発行するフロー（Client Credentials Flow）を設計します。決してユーザー用のパスワードをバッチスクリプト内に埋め込むようなアンチパターン（Resource Owner Password Credentials）を行ってはなりません。
"""
}

# 写し出し
for filepath, content in deep_content.items():
    full_path = os.path.join(docs_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
        
print(f"Generated {len(deep_content)} extremely deep modules for Batch 4.")
