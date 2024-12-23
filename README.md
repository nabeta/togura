# JPCOAR Schema Helper

[JPCOARスキーマ](https://schema.irdb.nii.ac.jp/ja/schema) 2.0のメタデータを、YAMLを使って少しかんたんに記述できるようにするためのツールです。作成したYAMLファイルは、付属のスクリプトでJPCOARスキーマのXMLファイルに変換することができます。  
また、作成したメタデータファイルをもとに、[ResourceSync](https://www.openarchives.org/rs/1.1/resourcesync)のXMLファイルを作成することができます。

## 使い方

### 準備

1. Pythonをインストールします。3.11以降のバージョンをインストールしてください。Windowsをお使いの場合、[MicrosoftのWebサイト](https://learn.microsoft.com/ja-jp/windows/python/beginners)にインストールや動作確認の方法が掲載されていますので、参考にしてください。
1. [Visual Studio Code](https://code.visualstudio.com/)(VSCode)をインストールします。
1. VSCodeのユーザインターフェースを日本語で表示するため、[Japanese Language Pack for VS Code](https://marketplace.visualstudio.com/items?itemName=MS-CEINTL.vscode-language-pack-ja)をインストールします。VSCodeを起動してCtrlキーとPキーを同時に押し、表示された入力欄に以下の文字列を入力して、Enterキーを押します。
    ```
    ext install MS-CEINTL.vscode-language-pack-ja
    ```
1. VSCodeの[YAML拡張機能](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)をインストールします。先ほどと同様に、VSCodeを起動した状態でCtrlキーとPキーを同時に押し、表示された入力欄に以下の文字列を入力して、Enterキーを押します。
    ```
    ext install redhat.vscode-yaml
    ```
1. VSCodeの画面上部のメニューから"ターミナル"を選び、さらに"新しいターミナル"を選びます。ターミナルのウインドウが画面下部に開くので、以下のコマンドを実行して、必要なPythonのモジュールをインストールします。
    ```sh
    pip install pyyaml setuptools resync rocrate
    ```
1. [ツールのファイル一式のzipファイル](https://github.com/nabeta/jpcoar-schema-helper/archive/refs/heads/main.zip)をダウンロードして、適当なフォルダに展開します。ここでは`jpcoar-schema-helper-main`フォルダに展開したものとします。

### 動作テスト

1. VSCodeで`jpcoar-schema-helper-main`フォルダを開きます。
1. VSCodeのターミナルを開き、以下のコマンドを実行します。
    ```sh
    ./jpcoar.py samples/00_sample/ https://example.com
    ```
1. 同様に、ターミナルで以下のコマンドを実行します。
    ```sh
    ./resourcesync.py https://example.com
    ```
1. `public`フォルダの中にResourceSyncのXML`capabilitylist.xml`と`resourcelist.xml`が作成されていることを確認します。
1. `public`フォルダの中に`1000`フォルダが作成され、その中にJPCOARスキーマのXMLファイル`jpcoar20.xml`が作成されていることを確認します。

### メタデータの書き方

1. Windowsのエクスプローラーで`jpcoar-schema-helper-main`フォルダを開き、`work`フォルダの中に新しいフォルダを作成します。フォルダ名は資料名などわかりやすいものであれば、なんでもかまいません。ここでは`work`フォルダの中に`my_article`フォルダを作ったこととして、以降そのフォルダを`work/my_article`フォルダと記述します。
1. `samples`フォルダの中にあるサンプルのメタデータファイルから、登録する資料の種類に適したものを選んで、`work/my_article`フォルダにコピーします。ファイル名は`jpcoar20.yaml`のままとしてください。
1. `work/my_article`フォルダに、登録したい論文ファイルや研究データファイルをコピーします。ファイル名はなんでもかまいませんが、データを公開するときのURLに使用されるため、英数小文字を使用することをおすすめします。ただし、`work/my_article`フォルダの中にフォルダを作成すると、これ以降の処理が正常に動作しなくなりますので注意してください。
1. VSCodeで`jpcoar-schema-helper-main`フォルダを開きます。
1. VSCodeのファイル一覧から`work/my_article`フォルダを開き、メタデータファイル`jpcoar20.yaml`の編集と保存を行ってください。編集の際には、以下の2点に注意してください。
    - ファイルの1行目にある以下の記述は削除しないでください。もし削除した場合、1行目に同じ記述を追加し直してください。
      ```yaml
      # yaml-language-server: $schema=../../schema/jpcoar.json
      ```
    - ファイルの5行目にある`id`に、他のメタデータファイルと重複しない通し番号を記入してください。この番号は、データを公開するときのURLに使用されます。
      ```yaml
      id: 1001
      ```

### JPCOARスキーマのXMLへの変換　

1. VSCodeのターミナルで`jpcoar.py`スクリプトを実行し、YAMLで作成したメタデータファイルをJPCOARスキーマのXMLファイルに変換します。スクリプトを実行すると、`public`フォルダの中に`id`の番号でフォルダが作成され、そのフォルダの中にJPCOARスキーマのXMLファイル`jpcoar20.xml`と、登録する論文ファイル・研究データファイルが保存されます。
    以下のコマンドは、`work/my_article`フォルダの内容を変換する例です。コマンド文中の`https://example.com`は、実際にファイルを公開するWebサーバの名前に変更してください（テストとして実行している場合は、変更する必要はありません）。
    ```sh
    ./jpcoar.py work/my_article/ https://example.com
    ```
    メタデータの編集は`work`フォルダの中のファイルのみを用いて行います。`public`フォルダの中に作成されたファイルは編集しないでください。編集しても、再度`jpcoar.py`スクリプトを実行することで上書きされます。
1. VSCodeのターミナルで`resourcesync.py`スクリプトを実行し、ResourceSyncのXMLファイルを`public`フォルダの中に作成します。コマンド文中の`https://example.com`は、`jpcoar.py`を実行するときに指定したWebサーバの名前に変更してください（テストとして実行している場合は、変更する必要はありません）。
    ```sh
    ./resourcesync.py https://example.com
    ```
1. `public`フォルダに保存されたフォルダを、`jpcoar.py`と`resourcesync.py`で指定したWebサーバにアップロードします。

### フォルダの構成

- `public`: 公開用のファイルが出力されるフォルダ
    - このフォルダに保存されたファイルは編集しないこと
- `samples`: メタデータのサンプルのフォルダ
- `schema`: メタデータスキーマの定義ファイル
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

## 作成の背景

- テキストエディタでJPCOARスキーマのメタデータを書けるようにしたい
- Pythonなどのプログラミング言語でJPCOARスキーマのメタデータを書けるようにしたい
- [JAIRO Cloud](https://jpcoar.repo.nii.ac.jp/page/42)以外の環境からメタデータを[IRDB](https://irdb.nii.ac.jp/)に送付したい
- 静的なファイルのアップロードだけでデータリポジトリを運用できるようにしたい

## TODO

- `jpcoar20.yaml`のプロパティ名を整理する
- ResourceSyncの`changelist.xml`を作成できるようにする
- [RO-Crate](https://www.researchobject.org/ro-crate/)での出力を行えるようにする
- GitHub PagesやGitLab PagesでのHTMLの出力を行えるようにする

## 作者

田辺浩介 ([@nabeta](https://github.com/nabeta))
