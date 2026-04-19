# dbt Macros & Jinja Mastery
### 1. 【エンジニアの定義】Professional Definition
**Jinja**: Pythonのテンプレートエンジン。dbtは単なるSQLではなく、Jinjaを使うことでSQL内に制御構文(for, if)や関数(Macro)を埋め込み、SQLを「プログラミング言語化」する。
### 2. 【0ベース・深掘り解説】Gap Filling
「12ヶ月分の月別カラムをPIVOTで作りたい」。素のSQLなら手書きで12行書きますし、来年になったらバグります。
dbtなら `{% for month in range(1, 13) %}` でSQL文自体をループで自動生成（コンパイル）します。
「複数のテーブルに同じマスキング処理を適用したい」。これをMacroとして定義し `{{ mask_personal_data('email') }}` と呼び出すだけで、変更時はMacroの定義1箇所を直すだけで全テーブルに適用されます。DRY（Don't Repeat Yourself）原則の達成です。
