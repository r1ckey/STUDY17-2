# Object Memory Layout & Garbage Collection
### 1. 【エンジニアの定義】Professional Definition
Pythonは全てがオブジェクト（PyObject構造体）。整数ひとつでも参照カウント（ob_refcnt）、型情報（ob_type）、値を持つため、C言語の純粋なint(4バイト)に対し、Pythonのintは28バイトを消費する。
### 2. 【0ベース・深掘り解説】Gap Filling
「1億行の数値をリストに入れるとRAMが枯渇する」理由がこれ。Pandas/Numpyが速く省メモリなのは、内部的にPythonオブジェクトではなくC言語の連続したメモリ領域（配列）としてデータを保持しているから。
ガベージコレクション（GC）：主に「参照カウント」でメモリを解放するが、循環参照対策の「世代別GC」が走ると処理が一瞬停止（Stop-The-World）する。バッチ処理の謎のスパイク遅延の犯人。
