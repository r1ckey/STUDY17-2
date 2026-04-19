# Context Managers & Resource Leaks
### 1. 【エンジニアの定義】Professional Definition
**Context Manager (`with` 構文)**: ファイルやネットワークコネクションなど、OSレベルのリソースを「確実に」クローズするためのプログラミング・パラダイム。内部的に `__enter__` と `__exit__` メソッドを持つ。
### 2. 【0ベース・深掘り解説】Gap Filling
DEのよくある障害として「Too many open files (ファイルディスクリプタの枯渇)」があります。ファイルを開いたまま `close()` を忘れたり、例外処理中に `close()` が呼ばれなかったために発生します。`with` を使用すると、例外が起ころうと途中で `return` しようと、確実にコネクションが切断されるため、堅牢なデータパイプラインには必須の記法です。
