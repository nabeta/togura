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

### ツールの準備

1. Toguraのzipファイルを以下のリンクからダウンロードし、適当なフォルダに展開します。
    https://github.com/nabeta/togura/archive/refs/heads/main.zip
1. 展開したフォルダを、「ドキュメント」フォルダなどのわかりやすいフォルダに移動します。Windowsの圧縮フォルダ機能でzipファイルを展開した場合、`togura-main`フォルダの中にもうひとつ`togura-main`フォルダが作成されていますので、そのフォルダを移動してください。
1. VSCodeのメニューから「ファイル」→「フォルダーを開く」を選び、展開したフォルダを選びます。フォルダの選択画面では、`togura-main`フォルダを選択（シングルクリック）した状態で「開く」ボタンを押してください。
1. 「このフォルダー内のファイルの作成者を信頼しますか?」と尋ねられたら、「はい、作成者を信頼します」を選びます。
1. 画面上部のメニューから「表示」→「拡張機能」を選びます。画面左側のウインドウに拡張機能の一覧が表示されるので、以下の2つに対してそれぞれ「インストール」ボタンを押します。
    - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
    - [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)
        - 画面右下に 「このリポジトリ 用のおすすめ拡張機能 をインストールしますか?」というメッセージが表示された場合、「インストール」を選んでください。ただし、この場合でも別途画面左側のウインドウでそれぞれの拡張機能に対して「インストール」ボタンを押す必要があります。
1. VSCodeのメニューで「ファイル」→「名前をつけてワークスペースを保存」を選び、そのまま「保存」を選びます。
1. VSCodeの画面上部のメニューから「ターミナル」→「新しいターミナル」を選びます。ターミナルのウインドウが画面下部に開くので、以下のコマンドを実行して、[uvコマンドをインストール](https://docs.astral.sh/uv/getting-started/installation/)します。
    ```
    # Windowsの場合
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

    # macOSやLinuxの場合
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
1. ターミナルで以下のコマンドを実行して、必要なPythonのモジュールをインストールします。
    ```sh
    uv venv
    uv pip install -r requirements.txt
    ```
1. VSCodeをいったん終了して、再度起動します。先ほどと同様にVSCodeのメニューから「ファイル」→「フォルダーを開く」を選び、toguraのフォルダを選びます。
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

1. Windowsのエクスプローラーなどで、Toguraを保存したフォルダを開きます。
1. `samples`フォルダを開き、さらにその中にある`00_sample`フォルダを開きます。`article.pdf`ファイルと`dataset.txt`ファイル、ならびにメタデータファイル`jpcoar20.yaml`が保存されていることを確認します。
1. 同様に、`samples`フォルダと同じ場所に`work`フォルダと`public`フォルダが存在することを確認します。
1. `00_sample`フォルダを`work`フォルダにコピーします。
1. VSCodeに戻ってターミナルを開き、以下のコマンドを実行します。
    ```sh
    uv run python -X utf8 ./togura.py generate
    ```
1. `public`フォルダの中に`00`フォルダが作成され、その中に以下のファイルが作成されていることを確認します。
    - `article.pdf`
    - `dataset.txt`
    - `ro-crate-preview.html`: メタデータを表示するためのHTMLファイル。[RO-Crate](https://www.researchobject.org/ro-crate/)の規格に則ったファイル名になっています
    - `ro-crate-metadata.json`: RO-CrateのメタデータJSONファイル
    - `jpcoar20.xml`: JPCOARスキーマのXMLファイル
1. 同様に、`public`フォルダの中にResourceSyncのXMLファイル`capabilitylist.xml`と`resourcelist.xml`が作成されていることを確認します。

### メタデータの書き方

1. Windowsのエクスプローラーなどで、Toguraを保存したフォルダを開き、`work`フォルダの中に新しいフォルダを作成します。フォルダ名は以下の規則で作成する必要があります。
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
    - `jpcoar20.yaml`の文字コードはUTF-8としてください。VSCodeで編集する際には、特になにも設定しなくてもよいですが、メモ帳などの他のテキストエディタで編集する場合はご注意ください。
    - `jpcoar20.yaml`の編集はVSCode以外のテキストエディタでも行うことができますが、VSCodeで編集する場合、以下の機能が利用できます。
        - 一部のメタデータ項目名の最初の数文字を入力すると、自動的に入力候補が表示されます。
        - JPCOARスキーマに適合しないメタデータを記述している場合、赤色の波線が表示されます。
    - ファイルの1行目にある以下の記述は削除しないでください。もし削除した場合、1行目に同じ記述を追加し直してください。
      ```yaml
      # yaml-language-server: $schema=../../schema/jpcoar.json
      ```

### リポジトリ用ファイルの出力

VSCodeのターミナルで`togura.py generate`コマンドを実行し、YAMLで作成したメタデータファイルをJPCOARスキーマのXMLファイルに変換します。
```sh
uv run python -X utf8 ./togura.py generate
```
スクリプトを実行すると、`public`フォルダの中に以下のファイルとフォルダが作成されます。

- 登録一覧のHTMLファイル`index.html`
- 登録番号のついたフォルダ
    - 登録した論文ファイル・研究データファイル
    - `ro-crate-preview.html`: メタデータを表示するためのHTMLファイル
    - `ro-crate-metadata.json`: RO-CrateのメタデータJSONファイル
    - `jpcoar20.xml`: JPCOARスキーマのXMLファイル

メタデータの編集は`work`フォルダの中のファイルのみを用いて行います。`public`フォルダの中に作成されたファイルは編集しないでください。編集しても、再度`togura.py generate`コマンドを実行することで上書きされます。

### 他の機関リポジトリからの移行

JPCOARスキーマ1.0でのOAI-PMHの出力に対応している機関リポジトリから、登録されている資料をToguraに移行することができます。移行には`togura.py migrate`コマンドを使用します。

指定できる項目は以下のとおりです。

- `--base-url`（必須）: OAI-PMHのベースURLです。JAIRO Cloudの場合、各リポジトリのトップページのURLに`/oai`を追加したものになります。たとえばリポジトリのトップページのURLが`https://jpcoar.repo.nii.ac.jp`の場合、OAI-PMHのベースURLは`https://jpcoar.repo.nii.ac.jp/oai`になります。
- `--date-from`: 移行対象の開始日です。この日よりも後に登録・更新された資料を移行します。指定しない場合、自動的に30日前の日付が指定されたものとして動作します。
- `--date-until`: 移行対象の終了日です。この日よりも前に登録・更新された資料を移行します。指定しない場合、自動的に実行時の日付が指定されたものとして動作します。
- `--metadata-prefix`: 取得するメタデータの種類です。指定しない場合、自動的に`jpcoar_1.0`が指定されたものとして動作します。
- `--export-dir`（必須）: 取得した資料のメタデータと本文ファイルを保存するフォルダ（ディレクトリ）です。任意の名前のフォルダを指定できます。

以下がコマンドの実行例です。実際に実行するときには、`--base-url`などを適宜変更してください。また、このコマンドでは本文ファイルのダウンロードを行うため、実行に時間がかかることにご注意ください。

```sh
uv run python -X utf8 ./togura.py migrate --base-url https://another.repo.example.ac.jp/oai --date-from 2025-08-01 --date-until 2025-08-31 --metadata-prefix jpcoar_1.0 --export-dir another
```

コマンドの実行が完了すると、`--export-dir`で指定したフォルダ（上記の例では`another`）の中に各資料のフォルダが作成され、その中に本文ファイルとメタデータ`jpcoar20.yaml`が保存されています。この各資料のフォルダを`work`フォルダに移動し、`togura.py generate`コマンドを実行すると、移行した資料がToguraに登録されます。

### リポジトリ用ファイルの公開

`public`フォルダに保存されたフォルダとファイルの一式を、Webサーバにアップロードします。アップロードの方法は、FTPクライアントやWeb管理画面など、お使いのWebサーバによって異なりますので、サーバの管理者（大学のIT担当部署・レンタルサーバの業者など）におたずねください。

### 公開した資料の取り下げ

以下の手順で実施します。

1. すでにWebサーバーで取り下げ対象の資料を公開している場合、サーバーからその資料のフォルダを削除します。
1. `public`フォルダを開き、取り下げ対象の資料のフォルダを別のフォルダに移動、もしくは削除します。
1. 同様に`work`フォルダを開き、取り下げ対象の資料のフォルダを別のフォルダに移動、もしくは削除します。Toguraのフォルダに存在する`archive`フォルダに移動することをおすすめします。
1. 「リポジトリ用ファイルの出力」の手順に沿って、`togura.py generate`コマンドを実行し、ファイルを再作成します。
1. 「リポジトリ用ファイルの公開」の手順に沿って、再作成したファイルをWebサーバーにアップロードします。

### バックアップ

バックアップは`togura`フォルダをコピーするだけで行えます。外付けディスクなどにコピーしておいてください。

### ツールの更新

1. [Toguraのダウンロードリンク](https://github.com/nabeta/togura/archive/refs/heads/main.zip)からzipファイルをダウンロードし、適当なディレクトリに展開します。
1. 展開したディレクトリに含まれるすべてのフォルダとファイルを、これまで使っていたToguraのフォルダに上書きコピーします。
1. VSCodeを起動し、ターミナルで以下のコマンドを実行して、必要なPythonのモジュールを更新します。
    ```sh
    uv pip install -r requirements.txt
    ```

### フォルダの構成

- `archive`: 作業済みのファイルを保存するフォルダ（未使用）
- `public`: 公開用のファイルが出力されるフォルダ
    - データを公開するには、このフォルダの中身をWebサーバにアップロードすること
    - このフォルダに保存されたファイルは編集しないこと
- `samples`: メタデータのサンプルのフォルダ
- `schema`: メタデータスキーマの定義ファイル（開発者用）
- `templates`: HTMLテンプレートファイル
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

## 使い方の質問

使い方やエラーの対応でわからないことがある場合は、[Code4Lib JAPANのDiscord](https://wiki.code4lib.jp/#Code4Lib_JAPAN_Discord)でお知らせください。

## 参考資料

- [Togura（とぐら、鳥座）: 超省力機関リポジトリ](https://doi.org/10.34477/0002000593) （COAR Annual Conference 2025のポスター）
- [Hussein Suleman. Designing Repositories in Poor Countries, Open Repositories 2023, 2023.](https://doi.org/10.5281/zenodo.8111568)
    - [Simple DL](https://github.com/slumou/simpledl)
- [Super – Simple – Static – Sustainable: a low resource repository jam](https://or2024.openrepositories.org/program-registration/workshops-and-tutorials/w02/) （Open Repositories 2024のワークショップ）
    - [Super-Simple-Static-Sustainable](https://github.com/OpenRepositoriesConference/Super-Simple-Static-Sustainable) （ワークショップの成果物）
- [阿達 藍留, 山田 俊幸, 大向 一輝. DAKit: 低コストなデータ共有のための静的デジタルアーカイブジェネレータの提案, 情報知識学会誌, 2022, 32巻4号, p.406-409.](https://doi.org/10.2964/jsik_2022_035)
    - [DAKit](https://github.com/utokyodh/dakit)

## 作者

田辺浩介 ([@nabeta](https://github.com/nabeta))
