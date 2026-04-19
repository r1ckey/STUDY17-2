import os

base_dir = r"C:\Users\jorda\Documents\ANTIGRAVITY\study17"
docs_dir = os.path.join(base_dir, "docs")

deep_content = {
    "python/asyncio.md": r"""# Python AsyncIO & Networking I/O
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「通信待ち時間」という無駄な空白**
データエンジニアリングで頻繁に発生するのが、「外部のWeb APIからデータを収集してDWHに保存する」処理です。例えば、1000個の異なるエンドポイントにリクエストを投げる処理を、標準の `requests.get()` の `for` ループで書いたとします。
1回のAPIの応答に「1秒」かかる場合、1000件のデータを取るのに**1000秒（約16分）**かかります。
これに対し、「1つ目のリクエストを投げて、APIのサーバーが処理を行って返事をくれるまでの1秒の待ち時間に、2つ目、3つ目のリクエストを別の回線で投げてしまえばいい」という発想が非同期処理 (Asynchronous I/O) です。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
**Event Loop と シングルスレッド非同期**
マルチスレッドと非同期（AsyncIO）はどう違うのでしょうか？
マルチスレッドは「OSが複数のスレッド（労働者）を用意し、別々の仕事をさせる」ことですが、Pythonでは前述のGIL（グローバルインタプリタロック）のせいで上手く動作しないことが多々あります。
Pythonの `asyncio` モジュールでは、スレッドはたった1つ（1人の労働者）しかいません。その代わり、**イベントループ (Event Loop)** という超高速なタスク管理システムが中央に座ります。
労働者はAPIにリクエストを投げると、`await` (待機) 状態に入ります。イベントループは「あ、こいつ今ヒマ（待ち状態）になったな」と検知し、瞬時に別のタスク（次のリクエストを投げる処理）を労働者に割り当てます。
この高速な切り替え（コンテキストスイッチ）により、1つのスレッドで1000個のAPIリクエストをほぼ同時に投げることができ、1000秒かかっていた処理が **2〜3秒で完了** します。

```mermaid
sequenceDiagram
    participant EventLoop as Event Loop
    participant Thread as Single Thread
    participant API1 as External API 1
    participant API2 as External API 2

    EventLoop->>Thread: タスク1開始
    Thread->>API1: GET リクエスト送信 (await)
    Note over Thread, API1: --- 通信待ち状態へ移行 ---
    Thread-->>EventLoop: 「暇になった」と通知
    EventLoop->>Thread: 即座にタスク2開始
    Thread->>API2: GET リクエスト送信 (await)
    
    API1-->>EventLoop: 応答完了のアラート
    EventLoop->>Thread: タスク1を再開しデータを保存
```

### 3. 【実務への応用】Practical Application
* **aiohttp の活用**:
  標準の `requests` ライブラリは同期型なので、`asyncio` の中では使えません（スレッド全体をブロックしてしまうため）。外部APIを非同期で叩く場合は、`aiohttp` や `httpx` といった非同期特化のライブラリを使用するのが実務の必須要件です。
* **Semaphore（セマフォ）による並行数制御**:
  1000回一気にリクエストを投げると、大概のAPIサーバーは「DoS攻撃を受けた」と判定して `429 Too Many Requests` のエラーを返してブロックしてきます。
  実務では必ず `asyncio.Semaphore(10)` などを使って、「同時に投げるリクエストは最大10個まで」といったスロットル制御（Throttling）を組み込むことが不可欠です。
""",

    "python/metaclasses.md": r"""# Metaclasses (Advanced Object Creation)
### 1. 【課題解決のメカニズム】Mechanism of Problems
**「クラスそのもの」を作る黒魔術**
オブジェクト指向において、通常「クラス」は「インスタンス（具体的なモノ）」を作るための設計図です。では、「クラスという設計図自体」を作るものは何でしょうか？それが「メタクラス（Metaclass）」です。
データモデリングやORM（SQLAlchemy, Django ORMなど）を作る場合、「ユーザーが普通にクラスを定義しただけで、裏側で勝手にバリデーションを追加し、DBのテーブルスキーマと紐付ける」といったフレームワーク側の魔法が必要になります。メタクラスは、この魔法を実現する究極のツールです。

### 2. 【アーキテクチャの真髄】Architectural Deep Dive
Pythonにおいてクラスはそれ自体が「オブジェクト（`type`クラスのインスタンス）」です。
通常のクラスが `__init__` でインスタンスを初期化するように、メタクラスは `__new__` や `__init__` メソッドを持ち、そこで「新しく定義されようとしているクラスのメソッドや属性」をインターセプト（横取り）して書き換えることができます。

```mermaid
graph TD
    Type((type <br/>The build-in Metaclass)) -->|Instances are Classes| Metaclass[Custom Metaclass]
    Metaclass -->|Instances are Classes| Class[Your Base Class]
    Class -->|Instances are Objects| Object[Actual Data Object]
```

### 3. 【実務への応用】Practical Application
* **実務での制限事項**: 「メタクラスは99%のユーザーにとって不要である」(Tim Peters) という名言の通り、自前でデータフレームワークやORMをフルスクラッチ（開発）するのでない限り、データチームのアプリケーションコード内にメタクラスを実装するのは、保守性の観点から強力なアンチパターンとなります。しかし、「dbtなどの内部実装がどのようにSQLをパース・マッピングしているか」を理解するための教養として非常に価値が高いです。
"""
}

# Write files directly
for filepath, content in deep_content.items():
    full_path = os.path.join(docs_dir, filepath)
    if os.path.exists(full_path):
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
print("Generated Deep Dive Content for Python Expansion!")
