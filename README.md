# Togura - 極めてシンプルな機関リポジトリ

Togura（とぐら、[鳥座](https://ja.wiktionary.org/wiki/%E9%B3%A5%E5%BA%A7)）は、極めてシンプルな機関リポジトリを構築するためのアプリケーションです。

![Togura](https://github.com/nabeta/togura/blob/main/templates/images/logo.svg?raw=true)

動作例は https://nabeta.github.io/togura/ にあります。

## 特長

Toguraは[JPCOARスキーマ](https://schema.irdb.nii.ac.jp/ja/schema) 2.0のメタデータの記述、ならびに[ResourceSync](https://www.openarchives.org/rs/toc)によるメタデータのハーベストに対応しており、[IRDB](https://irdb.nii.ac.jp/)を通して、[CiNii Research](https://cir.nii.ac.jp/)でのメタデータの検索や[JaLC](https://japanlinkcenter.org/top/)によるDOIの付与が行えるようになっています。

Toguraで構築する機関リポジトリでの論文や研究データの公開は、ローカル環境（手元のパソコン）でメタデータファイルやHTMLファイルを作成し、それらのファイルを論文や研究データのファイルといっしょにWebサーバにアップロードすることで行います。このため、以下のような特長を持っています。

- Toguraでは直接JPCOARスキーマのメタデータを記述するため、[JAIRO Cloud](https://jpcoar.repo.nii.ac.jp/page/42)などでのメタデータマッピングの設定が不要になります。
- Toguraはメタデータの簡易チェック機能を提供しており、JPCOARスキーマに適合しないメタデータを記述した場合でも容易に誤りに気づくことができます。
- 手元のパソコンだけで登録作業を行うため、インターネットに接続されていない環境でも作業を行うことができます（インターネット接続は公開作業のときのみ必要）。メンテナンスによって登録作業を行えなくなる期間も発生しません。
- メタデータファイルをはじめ、登録に使用するファイルがすべて手元のパソコンに残るため、手元のパソコンのバックアップを取ることで、機関リポジトリ全体のバックアップが行えます。データの復旧も、バックアップからファイルをコピーするだけで行えます。
- 複数台のパソコンから接続できる共有フォルダがあれば、複数人で登録作業を行うことができます。
- Toguraによって構築された機関リポジトリは静的ファイルだけで構成されるため、Webサーバでのセキュリティの問題が発生する可能性は極めて低くなります。

一方で、以下のような制限があります。

- メタデータの編集にWebブラウザではなくテキストエディタを使用することを前提としているため、編集に慣れるまで少し時間がかかるかもしれません。
- JPCOARスキーマ以外の独自のメタデータ項目を定義することはできません。
- ファイルを公開するためのWebサーバの用意が別途必要になります。なお、サーバはHTMLファイルなどの静的ファイル（内容が変化しないファイル）がアップロードできるものであればよく、月数百円程度のレンタルサーバで動作させることが可能です。PHPやPython, Rubyなどのプログラミング言語の実行環境は不要です。
- IRDBによるハーベストに対応させる場合、Togura専用のホスト名を用意する必要があります。
    - ハーベスト可: `https://togura.example.ac.jp/`
    - ハーベスト不可: `https://www.example.ac.jp/togura/`
- Toguraで扱うファイルは、一律で全体公開となります。ユーザ認証やアクセス元のIPアドレスによる限定公開機能はありません。
    - Toguraにはアクセス制御の機能はありませんが、Webサーバの設定（`.htaccess`など）によってパスワードやIPアドレスによるアクセス制御をかけることは可能です。
- Toguraの画面のデザインを変更するには、HTMLテンプレートファイルを直接編集する必要があります。

## 使い方

### 必要なソフトウェアのダウンロードとインストール

1. Pythonをインストールします。3.11以降のバージョンをインストールしてください。Windowsをお使いの場合、[Microsoft Store](https://apps.microsoft.com/search?query=python&hl=ja-JP&gl=JP)からインストールできます。
1. [Visual Studio Code](https://code.visualstudio.com/)(VSCode)をインストールします。Windowsをお使いの場合、こちらも[Microsoft Store](https://apps.microsoft.com/detail/xp9khm4bk9fz7q?hl=ja-JP&gl=JP)からインストールできます。
1. VSCodeを起動し、画面上部のメニューから「View」→「Extensions」を選択します。画面左側に拡張機能のウインドウが表示されるので、`Japanese Language Pack`と入力すると、検索結果に"[Japanese Language Pack for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=MS-CEINTL.vscode-language-pack-ja)"が表示されるので、"Install"ボタンを押します。
1. 画面右下に「Change Language and Restart」というボタンが表示されるので、ボタンを押してVSCodeを再起動します。

### Toguraの実行準備

1. Toguraのzipファイルを以下のリンクからダウンロードし、適当なフォルダに展開します。
    https://github.com/nabeta/togura/archive/refs/heads/main.zip
    - Gitをお使いの方は、以下の方法でダウンロードすることも可能です。
    ```sh
    git clone https://github.com/nabeta/togura.git
    ```
1. 展開したフォルダを、「ドキュメント」フォルダなどのわかりやすいフォルダに移動します。Windowsの圧縮フォルダ機能でzipファイルを展開した場合、`togura-main`フォルダの中にもうひとつ`togura-main`フォルダが作成されていますので、そのフォルダを移動してください。以降、この展開したフォルダを「Toguraのフォルダ」と記述します。
1. VSCodeのメニューから「ファイル」→「フォルダーを開く」を選び、Toguraのフォルダを選びます。フォルダの選択画面では、Toguraのフォルダを選択（シングルクリック）した状態で「開く」ボタンを押してください。
1. 「このフォルダ内のファイルの作成者を信頼しますか?」と尋ねられたら、「はい、作成者を信頼します」を選びます。
1. 画面上部のメニューから「表示」→「拡張機能」を選びます。画面左側のウインドウに拡張機能の一覧が表示されるので、以下の2つに対してそれぞれ「インストール」ボタンを押します。
    - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
    - [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

    画面右下に 「このリポジトリ 用のおすすめ拡張機能 をインストールしますか?」というメッセージが表示された場合、「インストール」を選んでください。ただし、この場合でも別途画面左側のウインドウでそれぞれの拡張機能に対して「インストール」ボタンを押す必要があります。
1. VSCodeのメニューで「ファイル」→「名前をつけてワークスペースを保存」を選び、そのまま「保存」を選びます。
1. VSCodeの画面上部のメニューから「ターミナル」→「新しいターミナル」を選びます。ターミナルのウインドウが画面下部に開くので、以下のコマンドを実行して、[uvコマンドをインストール](https://docs.astral.sh/uv/getting-started/installation/)します。
    - Windowsの場合:
        ```powershell
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```
    - macOSやLinuxの場合
        ```sh
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
1. **VSCodeをいったん終了して、もう一度起動します。この操作を実行しないと、これ以降の`uv`コマンドが動作しないので、必ず実行してください。**
1. 先ほどと同様にVSCodeのメニューから「ファイル」→「フォルダーを開く」を選び、toguraのフォルダを選びます。
1. ターミナルで以下のコマンドを実行して、必要なPythonのモジュールをインストールします。
    ```sh
    uv venv
    uv pip install -r requirements.txt
    ```

    以下のようなメッセージがターミナルに表示されていれば、インストールは完了しています。もしエラーになっている場合、後述の「[エラーへの対応](#エラーへの対応)」をごらんください。
    ```
    Audited 8 packages in 1.45s
    ```
1. ターミナルで以下のコマンドを実行して、Toguraの初期設定を行います。このコマンドでは、設定ファイル`config.yaml`と、テンプレートのファイル`templates/head_custom.html`が作成されます。
    ```sh
    uv run python -X utf8 togura.py setup
    ```
    以下の項目を質問されますので、入力してください。
    - 組織の名称: 大学名など、機関リポジトリを運用する組織の名称です。
    - 機関リポジトリの名称: 機関リポジトリの名称です。
    - 機関リポジトリのトップページのURL: 公開先のWebサーバのトップページのURLです。Webサーバによる公開を行わず、自分のパソコンだけで動作を試す場合には、入力不要です。

    名称などを変更したい場合は、再度同じコマンドを実行してください。

### 動作テスト

1. Windowsのエクスプローラーなどで、Toguraのフォルダを開きます。`samples`、`work`、`public`フォルダが存在することを確認します。
1. `samples`フォルダを開き、サンプルの資料のフォルダが保存されていることを確認します。サンプルの資料は、[JPCOARスキーマ2.0のサンプルファイル](https://github.com/JPCOAR/schema/tree/master/2.0/samples)をもとに作成しています。
1. `work`フォルダと`public`フォルダを開き、それぞれ中身が空であることを確認します。
    - お使いのパソコンで隠しファイルを表示する設定になっている場合、`.keep`ファイルや`.well-known`フォルダが表示されます。
1. `samples`フォルダの中にある`00_sample`などのフォルダをすべて選択して、`work`フォルダにコピーします。
1. VSCodeに戻ってターミナルを開き、以下のコマンドを実行します。
    ```sh
    uv run python -X utf8 ./togura.py generate
    ```
1. `public`フォルダの中に作成されている`index.html`ファイルを開き、サンプルの資料の情報が表示されていることを確認します。

### メタデータの書き方

1. WindowsのエクスプローラーなどでToguraのフォルダを開き、`work`フォルダの中に新しいフォルダを作成します。フォルダ名は以下の規則で作成する必要があります。
    - 1文字以上の半角数字で始まること
        - この数字がリポジトリの登録番号となり、公開する際のURLとして使用されます
        - 登録番号は重複していない番号を使用する必要がありますが、連番である必要はありません
    - 数字の後ろに`_`（半角のアンダースコア）を含めること
    - `_`の後ろの文字は任意の文字列を入力可能
        - 資料名など、わかりやすいものであればなんでもかまいません

    ここでは`work`フォルダの中に`1001_my_article`フォルダを作ったこととして、以降そのフォルダを`work/1001_my_article`フォルダと記述します。
1. `samples`フォルダの中にあるサンプルのメタデータファイルから、登録する資料の種類に適したものを選んで、`work/1001_my_article`フォルダにコピーします。ファイル名は`jpcoar20.yaml`のままとしてください。
1. `work/1001_my_article`フォルダに、登録したい論文ファイルや研究データファイルをコピーします。ファイル名はなんでもかまいませんが、データを公開するときのURLに使用されるため、英数小文字を使用することをおすすめします。ただし、`work/1001_my_article`フォルダの中にフォルダを作成すると、これ以降の処理が正常に動作しなくなりますので注意してください。
1. VSCodeのファイル一覧から`work/1001_my_article`フォルダを開き、メタデータファイル`jpcoar20.yaml`の編集と保存を行ってください。編集の際には、以下の2点に注意してください。
    - `jpcoar20.yaml`の文字コードはUTF-8としてください。VSCodeで編集する際には、特になにも設定する必要はありません。
    - `jpcoar20.yaml`の編集はVSCode以外のテキストエディタでも行うことができますが（[後述](#vscode以外での動作)）、VSCodeで編集する場合、以下の機能が利用できます。
        - 一部のメタデータ項目名の最初の数文字を入力すると、自動的に入力候補が表示されます。
        - JPCOARスキーマに適合しないメタデータを記述している場合、赤色の波線が表示されます。
    - ファイルの1行目にある以下の記述は削除しないでください。もし削除した場合、1行目に同じ記述を追加し直してください。
      ```yaml
      # yaml-language-server: $schema=../../schema/jpcoar.json
      ```

### リポジトリ用ファイルの出力

VSCodeのターミナルで`togura.py generate`コマンドを実行し、YAMLで作成したメタデータファイルをHTMLファイルとJPCOARスキーマのXMLファイルに変換します。
```sh
uv run python -X utf8 ./togura.py generate
```
スクリプトの実行が正常に完了すると、ターミナルに以下のメッセージが表示されます。もしこのメッセージが表示されず、エラーになっている場合は、後述の「[エラーへの対応](#エラーへの対応)」をごらんください。

```
Toguraによるリポジトリの構築処理が完了しました。
```

また、`public`フォルダの中に以下のファイルとフォルダが作成されます。エクスプローラーなどで`index.html`や`ro-crate-preview.html`ファイルを開き、登録した資料の情報が表示されることを確認してください。

- 登録一覧のHTMLファイル`index.html`
- 登録番号のついたフォルダ
    - 登録した論文ファイル・研究データファイル
    - `ro-crate-preview.html`: メタデータを表示するためのHTMLファイル。[RO-Crate](https://www.researchobject.org/ro-crate/)の規格に則ったファイル名になっています
    - `ro-crate-metadata.json`: RO-CrateのメタデータJSONファイル
    - `jpcoar20.xml`: JPCOARスキーマのXMLファイル

メタデータの編集は`work`フォルダの中のファイルのみを用いて行います。`public`フォルダの中に作成されたファイルは編集しないでください。編集しても、再度`togura.py generate`コマンドを実行することで上書きされます。

### リポジトリ用ファイルの公開

`public`フォルダに保存されたフォルダとファイルの一式を、Webサーバにアップロードします。アップロードの方法は、FTPクライアントやWeb管理画面など、お使いのWebサーバによって異なりますので、サーバの管理者（大学のIT担当部署・レンタルサーバの業者など）におたずねください。

### 他の機関リポジトリからの移行

JPCOARスキーマ1.0でのOAI-PMHの出力に対応している機関リポジトリから、登録されている資料をToguraに移行することができます。移行には`togura.py migrate`コマンドを使用します。

指定できる項目は以下のとおりです。

- `--base-url`（必須）: OAI-PMHのベースURLです。JAIRO Cloudの場合、各リポジトリのトップページのURLに`/oai`を追加したものになります。たとえばリポジトリのトップページのURLが`https://jpcoar.repo.nii.ac.jp`の場合、OAI-PMHのベースURLは`https://jpcoar.repo.nii.ac.jp/oai`になります。
- `--export-dir`（必須）: 取得した資料のメタデータと本文ファイルを保存するフォルダ（ディレクトリ）です。任意の名前のフォルダを指定できます。
- `--date-from`: 移行対象の開始日で、この日よりも後に登録・更新された資料を移行します。`yyyy-MM-dd`（年4桁・月2桁・日2桁の半角数字、半角ハイフン区切り）形式で指定します。指定しない場合、コマンド実行時の30日前の日付が指定されたものとして動作します。
- `--date-until`: 移行対象の終了日で、この日よりも前に登録・更新された資料を移行します。`yyyy-MM-dd`（年4桁・月2桁・日2桁の半角数字、半角ハイフン区切り）形式で指定します。指定しない場合、コマンド実行時の日付が指定されたものとして動作します。
- `--metadata-prefix`: 取得するメタデータの種類です。`jpcoar_1.0`か`jpcoar_2.0`を指定します。指定しない場合、`jpcoar_1.0`が指定されたものとして動作します。
- `--metadata-only`: JPCOARスキーマのメタデータのみをダウンロードします。

以下がコマンドの実行例です。実際に実行するときには、`--base-url`などを適宜変更してください。また、この実行例では本文ファイルのダウンロードを行うため、実行に長い時間がかかる場合があることにご注意ください。

```sh
uv run python -X utf8 ./togura.py migrate --base-url https://another.repo.example.ac.jp/oai --export-dir another --date-from 2025-08-01 --date-until 2025-08-31 --metadata-prefix jpcoar_1.0
```

コマンドの実行が完了すると、`--export-dir`で指定したフォルダ（上記の例では`another`）の中に各資料のフォルダが作成され、その中に本文ファイルとメタデータ`jpcoar20.yaml`が保存されています。この各資料のフォルダを`work`フォルダに移動し、`togura.py generate`コマンドを実行すると、移行した資料がToguraに登録されます。

なお、指定した期間に登録された資料がない場合、以下のエラーが出力されます。対象の期間を広げて、再度実行してください。

```
sickle.oaiexceptions.NoRecordsMatch
```

### エンバーゴ期間が終了している資料のチェック

`togura.py check_expired_embargo`コマンドを用いて、エンバーゴ期間が終了している資料の一括チェックを行うことができます。具体的には、以下の条件にあてはまる資料の一覧を出力することができます。

- メタデータの`access_rights`が`embargoed access`になっている
- メタデータの`date`の`date_type`が`Available`、かつ`date`が実行日よりも前の日付になっている

指定できる項目は以下のとおりです。

- `--dir`: チェック対象のフォルダを指定します。個別の資料のフォルダではなく、`work`フォルダのような、資料の一式が保存されているフォルダを指定してください。指定しない場合、`work`が指定されたものとして動作します。

以下がコマンドの実行例です。

```sh
uv run python -X utf8 ./togura.py check_expired_embargo --dir work
```

出力結果は以下のようになります。メタデータに記述した利用可能日（`date_type`に`Available`を指定している`date`）と、資料のメタデータの保存場所が出力されますので、メタデータの`access_rights`の値を`open access`などに変更してください。

```
2016-04-01	work/02_journal_article_embargoed/jpcoar20.yaml
2016-04-01	work/04_journal_article_accepted_embargoed/jpcoar20.yaml
```

出力結果はテキストファイルに書き出すこともできます。以下の実行例は、`archive`フォルダに保存されている資料のエンバーゴ期間をチェックし、結果を`expired_embargo.txt`というファイルに書き出す例です。この例では、`expired_embargo.txt`ファイルはToguraのフォルダに保存されます。
- Windowsの場合:
    ```powershell
    uv run python -X utf8 ./togura.py check_expired_embargo --dir archive | Tee-Object -FilePath expired_embargo.txt
    ```
- macOSやLinuxの場合:
    ```sh
    uv run python -X utf8 ./togura.py check_expired_embargo --dir archive | tee expired_embargo.txt
    ```

### 公開した資料の取り下げ

以下の手順で実施します。

1. すでにWebサーバで取り下げ対象の資料を公開している場合、サーバからその資料のフォルダを削除します。
1. `public`フォルダを開き、取り下げ対象の資料のフォルダを別のフォルダに移動、もしくは削除します。
1. 同様に`work`フォルダを開き、取り下げ対象の資料のフォルダを別のフォルダに移動、もしくは削除します。Toguraのフォルダに存在する`archive`フォルダに移動することをおすすめします。
1. 「リポジトリ用ファイルの出力」の手順に沿って、`togura.py generate`コマンドを実行し、ファイルを再作成します。
1. 「リポジトリ用ファイルの公開」の手順に沿って、再作成したファイルをWebサーバにアップロードします。

### エラーへの対応

#### uvコマンドの実行時にエラーになる

VSCodeでuvコマンドのインストールを実行したのにエラーになる場合、uvコマンドがVSCodeの環境で認識されていない可能性があります。VSCodeを再起動してください。

#### togura.py generateコマンドの実行時にエラーになる

`KeyError:`と表示されている場合、メタデータのYAMLファイルに記述の誤りがある可能性があります。エラーの上部の`DEBUG:`と表示されている行に、エラーが発生している資料の登録番号が表示されています。
`work`フォルダの中にある当該登録番号のフォルダから`jpcoar20.yaml`ファイルをVSCodeで開き、メタデータでエラーになっている箇所（赤の波線が表示されています）を確認してください。メタデータを修正したら、再度`togura.py generate`コマンドを実行してください。

以下のエラーの例は、登録番号`00`の資料のメタデータで`title`の記述が抜けている場合のものです。この場合、`work`フォルダの中の`00_`から始まるフォルダを開き、`jpcoar20.yaml`ファイルを修正することになります。

```
DEBUG:jpcoar:00 created
Traceback (most recent call last):
  File "/home/nabeta/Documents/togura/./togura.py", line 178, in <module>
    main()
    ~~~~^^
  File "/home/nabeta/Documents/togura/./togura.py", line 85, in main
    generate()
    ~~~~~~~~^^
  File "/home/nabeta/Documents/togura/./togura.py", line 153, in generate
    root = jpcoar.generate(entry, base_url)
  File "/home/nabeta/Documents/togura/jpcoar.py", line 227, in generate
    for d in entry["title"]:
             ~~~~~^^^^^^^^^
KeyError: 'title'
```

メタデータでエラーが表示されている箇所がないのに`togura.py generate`コマンドでエラーになる場合、Toguraの不具合が考えられますので、後述の「[使い方の質問](#使い方の質問)」に記載されている連絡先までお問い合わせください。

#### メタデータで記述した項目がHTMLに表示されていない

Toguraの不具合の可能性が高いので、[使い方の質問](#使い方の質問)」に記載されている連絡先までお知らせください。

### バックアップ

バックアップはToguraのフォルダをコピーするだけで行えます。外付けディスクなどにコピーしておいてください。

### Toguraの更新

1. [Toguraのダウンロードリンク](https://github.com/nabeta/togura/archive/refs/heads/main.zip)からzipファイルをダウンロードし、適当なディレクトリに展開します。
1. 展開したディレクトリに含まれるすべてのフォルダとファイルを、これまで使っていたToguraのフォルダに上書きコピーします。
1. VSCodeを起動し、ターミナルで以下のコマンドを実行して、必要なPythonのモジュールを更新します。
    ```sh
    uv pip install -r requirements.txt
    ```

ToguraのダウンロードをGitで実行された方は、`git pull`でToguraを更新することができます。

### VSCode以外での動作

メタデータの編集は、VSCodeのほかにも、メモ帳などUTF-8の扱えるテキストエディタで行うことができます。ただし、メタデータの項目のチェック機能が使えなくなりますのでご注意ください。また、メタデータの保存の際には、文字コードがUTF-8になっていることを確認してください。  
メモ帳などVSCode以外のテキストエディタで作成したメタデータでも、VSCodeでToguraを実行することで、メタデータの項目のチェック機能が使えるようになります。チェック機能を有効にするには、上述の「メタデータの書き方」に沿った場所にメタデータのファイルを保存し、かつメタデータの1行目に以下の行を追加する必要があります。

```yaml
# yaml-language-server: $schema=../../schema/jpcoar.json
```

コマンドの実行に使用するターミナルには、VSCode内蔵以外のものを使用することも可能です。Windowsの場合、PowerShellや[Windows Terminal](https://apps.microsoft.com/detail/9n0dx20hk701?hl=ja-JP&gl=JP)が利用可能です。ターミナルのウインドウの位置を自由に設定したい場合は、こちらのほうがおすすめです。
VSCode内蔵以外のターミナルを使用する場合は、Toguraのコマンドの実行前に、ターミナルの作業フォルダをToguraのフォルダに変更する必要があります。以下の実行例は、Toguraのフォルダが`ドキュメント`→`togura`にある場合のものです。

```powershell
# Windowsの場合
cd $home
cd "Documents\togura"
```

```sh
# macOS・Linuxの場合
cd
cd Documents/togura
```

### フォルダの構成

- `archive`: 作業済み・取り下げ済みのファイルを保存するフォルダ
- `public`: 公開用のファイルが出力されるフォルダ
    - データを公開するには、このフォルダの中身をWebサーバにアップロードすること
    - このフォルダに保存されたファイルは編集しないこと
- `samples`: メタデータのサンプルのフォルダ
- `schema`: メタデータスキーマの定義ファイル（開発者用）
- `templates`: HTMLテンプレートファイル
    - `index.j2`: トップページのテンプレート
    - `index.j2`: 2ページ目以降の資料一覧画面のテンプレート
    - `show.j2`: 資料詳細画面のテンプレート
- `test`: テスト用スクリプトを保存するフォルダ（開発者用）
- `work`: 作業用フォルダ
    - このフォルダに保存されたファイルを編集すること

### メタデータスキーマの定義ファイルの更新

この作業は開発者が行うもので、メタデータの編集では必要ありません。

1. yqコマンドをインストールします。
    ```sh
    sudo apt-get install yq
    ```
1. `schema/jpcoar.yaml`ファイルを編集します。
1. yqコマンドで`schema/jpcoar.yaml`ファイルをJSON Schemaのファイルに変換します。
    ```sh
    yq . schema/jpcoar.yaml > schema/jpcoar.json
    ```

## TODO

- `jpcoar20.yaml`のプロパティ名を整理する
- ResourceSyncの`changelist.xml`を作成できるようにする
- RO-Crateで出力する項目を追加する
- [JaLCのWebAPI](https://japanlinkcenter.org/top/material/service_technical.html)を用いてDOIを直接付与できるようにする
- CiNiiやJaLC、CrossrefやDataCiteの書誌情報を用いて、自動的にメタデータのYAMLファイルを作成する
- [GakuNin RDMのコマンドラインツール](https://support.rdm.nii.ac.jp/usermanual/Setting-07/)と連携して、GakuNin RDMからファイルとメタデータの情報を取得する

## 使い方の質問

使い方やエラーの対応でわからないことがある場合は、[Code4Lib JAPANのDiscord](https://wiki.code4lib.jp/#Code4Lib_JAPAN_Discord)、もしくは[GitHubのIssues](https://github.com/nabeta/togura/issues)でお知らせください。  
[作者](#作者)にメールを送っていただいてもかまいませんが、返信が遅れることがあるため、できるだけDiscordかGitHubでの連絡をお願いします。

## 参考資料

- [Togura（とぐら、鳥座）: 超省力機関リポジトリ](https://doi.org/10.34477/0002000593) （COAR Annual Conference 2025のポスター）
- [Hussein Suleman. Designing Repositories in Poor Countries, Open Repositories 2023, 2023.](https://doi.org/10.5281/zenodo.8111568)
    - [Simple DL](https://github.com/slumou/simpledl)
- [Super – Simple – Static – Sustainable: a low resource repository jam](https://or2024.openrepositories.org/program-registration/workshops-and-tutorials/w02/) （Open Repositories 2024のワークショップ）
    - [Super-Simple-Static-Sustainable](https://github.com/OpenRepositoriesConference/Super-Simple-Static-Sustainable) （ワークショップの成果物）
- [阿達 藍留, 山田 俊幸, 大向 一輝. DAKit: 低コストなデータ共有のための静的デジタルアーカイブジェネレータの提案, 情報知識学会誌, 2022, 32巻4号, p.406-409.](https://doi.org/10.2964/jsik_2022_035)
    - [DAKit](https://github.com/utokyodh/dakit)

## 作者

田辺浩介 ([@nabeta](https://github.com/nabeta), nabeta at fastmail dot fm)
