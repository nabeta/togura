# Togura - 極めてシンプルな機関リポジトリ

Togura（とぐら、[鳥座](https://ja.wiktionary.org/wiki/%E9%B3%A5%E5%BA%A7)）は、極めてシンプルな機関リポジトリを構築するためのアプリケーションです。

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
- Toguraの画面のデザインを変更するには、HTMLテンプレートファイルを直接編集する必要があります。

## 使い方

### 必要なソフトウェアのダウンロードとインストール

1. Pythonをインストールします。3.11以降のバージョンをインストールしてください。Windowsをお使いの場合、[MicrosoftのWebサイト](https://learn.microsoft.com/ja-jp/windows/python/beginners)にインストールや動作確認の方法が掲載されていますので、参考にしてください。
1. [Visual Studio Code](https://code.visualstudio.com/)(VSCode)をインストールします。
1. [Git](https://git-scm.com/downloads)をインストールします。途中の選択肢はすべて「Next」を選ぶのでかまいません。
1. VSCodeを起動し、画面上部のメニューから「表示」→「拡張機能」を選びます。画面左側のウインドウに拡張機能の一覧が表示されるので、以下の3つに対してそれぞれ「インストール」ボタンを押します。
    - [Japanese Language Pack for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=MS-CEINTL.vscode-language-pack-ja)
    - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
    - [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

    画面右下に 「このリポジトリ 用のおすすめ拡張機能 をインストールしますか?」というメッセージが表示された場合、「インストール」を選んでください。ただし、この場合でも別途画面左側のウインドウでそれぞれの拡張機能に対して「インストール」ボタンを押す必要があります。
1. VSCodeの表示言語を切り替えます。画面上部のメニューから「表示」→「コマンド パレット」を選び、画面上部に表示されたウインドウに`display`と入力してEnterキーを押します。「日本語」を選び、メッセージに従ってVSCodeを再起動します。

### ツールの準備

1. Toguraのファイル一式をダウンロードします。VSCodeのメニューの「表示」→「ソース管理」を選び、画面左側のウインドウの「リポジトリの複製」を選びます。画面上部のウインドウに「リポジトリ URL を指定するか、リポジトリ ソースを選択します。」と表示されますので、以下の文字列をコピーしてウインドウに入力し、Enterキーを押します。
    ```
    https://github.com/nabeta/togura
    ```
1. 保存先のフォルダを尋ねるウインドウが表示されますので、適当なフォルダを指定します。「クローンしたリポジトリを開きますか?」というメッセージが表示されますので、「開く」を選びます。
1. 「このフォルダー内のファイルの作成者を信頼しますか?」と尋ねられたら、「はい、作成者を信頼します」を選びます。
1. VSCodeのメニューで「ファイル」→「名前をつけてワークスペースを保存」を選び、そのまま「保存」を選びます。
1. VSCodeの画面上部のメニューから「ターミナル」→「新しいターミナル」を選びます。ターミナルのウインドウが画面下部に開くので、以下のコマンドを実行して、Pythonのvenv環境（仮想環境）をインストールします。
    ```sh
    python3 -m venv .venv
    ```
    画面右下に「新しい環境が作成されました。これをワークスペース フォルダーに選択しますか?」というメッセージが表示されたら、「はい」を選びます。
1. いったんVScodeを終了し、再起動して、VSCodeの画面上部のメニューから「ターミナル」→「新しいターミナル」を選びます。
1. ターミナルで以下のコマンドを実行して、必要なPythonのモジュールをインストールします。
    ```sh
    pip install -r requirements.txt
    ```

### 動作テスト

1. Windowsのエクスプローラーなどで、Toguraを保存したフォルダを開きます。
1. `config.example.yml`ファイルを同じフォルダに`config.yml`という名前でコピーします。
1. `templates`フォルダを開き、`bootstrap.html`ファイルを同じフォルダに`head_custom.html`という名前でコピーします。
1. `samples`フォルダを開き、さらにその中にある`00_sample`フォルダを開きます。`article.pdf`ファイルと`dataset.txt`ファイル、ならびにメタデータファイル`jpcoar20.yaml`が保存されていることを確認します。
1. 同様に`samples`フォルダと同じ場所に保存されている`public`フォルダを開き、`.well-known`というフォルダしかないことを確認します。
1. VSCodeに戻ってターミナルを開き、以下のコマンドを実行します。
    ```sh
    ./togura.py
    ```
1. `public`フォルダの中に`1000`フォルダが作成され、その中に以下のファイルが作成されていることを確認します。
    - `article.pdf`
    - `dataset.txt`
    - `ro-crate-preview.html`: メタデータを表示するためのHTMLファイル。[RO-Crate](https://www.researchobject.org/ro-crate/)の規格に則ったファイル名になっています
    - `ro-crate-metadata.json`: RO-CrateのメタデータJSONファイル
    - `jpcoar20.xml`: JPCOARスキーマのXMLファイル
1. 同様に、`public`フォルダの中にResourceSyncのXML`capabilitylist.xml`と`resourcelist.xml`が作成されていることを確認します。

### メタデータの書き方

1. Windowsのエクスプローラーなどで、Toguraを保存したフォルダを開き、`work`フォルダの中に新しいフォルダを作成します。フォルダ名は以下の規則で作成する必要があります。
    - 1文字以上の半角数字で始まること
        - この数字がリポジトリの登録番号となり、公開する際のURLとして使用されます
        - 登録番号は連番である必要はありませんが、重複していない番号を使用する必要があります
    - 数字の後ろに`_`（半角のアンダースコア）を含めること
    - `_`の後ろの文字は任意の文字列を入力可能
        - 資料名など、わかりやすいものであればなんでもかまいません
    ここでは`work`フォルダの中に`1001_my_article`フォルダを作ったこととして、以降そのフォルダを`work/1001_my_article`フォルダと記述します。
1. `samples`フォルダの中にあるサンプルのメタデータファイルから、登録する資料の種類に適したものを選んで、`work/1001_my_article`フォルダにコピーします。ファイル名は`jpcoar20.yaml`のままとしてください。
1. `work/1001_my_article`フォルダに、登録したい論文ファイルや研究データファイルをコピーします。ファイル名はなんでもかまいませんが、データを公開するときのURLに使用されるため、英数小文字を使用することをおすすめします。ただし、`work/1001_my_article`フォルダの中にフォルダを作成すると、これ以降の処理が正常に動作しなくなりますので注意してください。
1. VSCodeのファイル一覧から`work/1001_my_article`フォルダを開き、メタデータファイル`jpcoar20.yaml`の編集と保存を行ってください。編集の際には、以下の2点に注意してください。
    - `jpcoar20.yaml`の文字コードはUTF-8としてください。VSCodeで編集する際には、特になにも設定しなくてもよいですが、メモ帳などの他のテキストエディタで編集する場合はご注意ください。
    - ファイルの1行目にある以下の記述は削除しないでください。もし削除した場合、1行目に同じ記述を追加し直してください。
      ```yaml
      # yaml-language-server: $schema=../../schema/jpcoar.json
      ```
    - `jpcoar20.yaml`の編集はVSCode以外のテキストエディタでも行うことができますが、VSCodeで編集する場合、以下の機能が利用できます。
        - 一部のメタデータ項目名の最初の数文字を入力すると、自動的に入力候補が表示されます。
        - JPCOARスキーマに適合しないメタデータを記述している場合、赤色の波線が表示されます。

### リポジトリ用ファイルの出力

VSCodeのターミナルで`togura.py`スクリプトを実行し、YAMLで作成したメタデータファイルをJPCOARスキーマのXMLファイルに変換します。
```sh
./togura.py
```
スクリプトを実行すると、`public`フォルダの中に以下のファイルとフォルダが作成されます。

- 登録一覧のHTMLファイル`index.html`
- 登録番号のついたフォルダ
    - 登録した論文ファイル・研究データファイル
    - `ro-crate-preview.html`: メタデータを表示するためのHTMLファイル
    - `ro-crate-metadata.json`: RO-CrateのメタデータJSONファイル
    - `jpcoar20.xml`: JPCOARスキーマのXMLファイル

メタデータの編集は`work`フォルダの中のファイルのみを用いて行います。`public`フォルダの中に作成されたファイルは編集しないでください。編集しても、再度`togura.py`スクリプトを実行することで上書きされます。

### リポジトリ用ファイルの公開

`public`フォルダに保存されたフォルダとファイルの一式を、Webサーバにアップロードします。アップロードの方法は、FTPクライアントやWeb管理画面など、お使いのWebサーバによって異なりますので、サーバの管理者（大学のIT担当部署・レンタルサーバの業者など）におたずねください。

### バックアップ

バックアップは`togura`フォルダをコピーするだけで行えます。外付けディスクなどにコピーしておいてください。

### ツールの更新

1. VSCodeのメニューで「表示」→「コマンド パレット」を選び、「ソース管理」を選びます。
1. 画面左下の「ソース管理グラフ」を選びます。ツールの変更内容の一覧が表示されます。
、横に表示されているボタンの中から「プル」を選びます。下向きの実線矢印のアイコンになっています。
1. 「Visual Studio Codeに定期的に 「git fetch」を実行する にしますか?」というメッセージが表示された場合、「いいえ」を選びます。
1. しばらく待って、「ソース管理グラフ」ウインドウに新しい変更内容が記述されれば、更新が完了しています。なお、ツールがすでに最新の状態になっている場合は、「プル」を実行してもなにも起こりません。
1. なんらかの理由で、ツールのファイルが変更されている場合、「プル」に失敗することがあります。この場合、画面左上の「ソース管理」ウインドウにある「…」ボタンを押し、「変更」→「すべての変更を破棄」を選んだ後、再度「プル」を実行してください。
1. 最後に、ターミナルで以下のコマンドを実行して、必要なPythonのモジュールを更新します。
    ```sh
    pip install -r requirements.txt
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
- JaLC DOIの直接付与のサポート

## 使い方の質問

使い方やエラーの対応でわからないことがある場合は、[Code4Lib JAPANのDiscord](https://wiki.code4lib.jp/#Code4Lib_JAPAN_Discord)でお知らせください。

## 参考資料

- [Hussein Suleman. Designing Repositories in Poor Countries, Open Repositories 2023, 2023.](https://doi.org/10.5281/zenodo.8111568)
    - [Simple DL](https://github.com/slumou/simpledl)
- [Super – Simple – Static – Sustainable: a low resource repository jam](https://or2024.openrepositories.org/program-registration/workshops-and-tutorials/w02/) （Open Repositories 2024のワークショップ）
    - [Super-Simple-Static-Sustainable](https://github.com/OpenRepositoriesConference/Super-Simple-Static-Sustainable) （ワークショップの成果物）
- [阿達 藍留, 山田 俊幸, 大向 一輝. DAKit: 低コストなデータ共有のための静的デジタルアーカイブジェネレータの提案, 情報知識学会誌, 2022, 32巻4号, p.406-409.](https://doi.org/10.2964/jsik_2022_035)
    - [DAKit](https://github.com/utokyodh/dakit)

## 作者

田辺浩介 ([@nabeta](https://github.com/nabeta))
