# JPCOAR Schema Helper

[JPCOARスキーマ](https://schema.irdb.nii.ac.jp/ja/schema) 2.0のメタデータを、YAMLを使って少しかんたんに記述できるようにするためのツールです。作成したYAMLファイルは、付属のスクリプトでJPCOARスキーマのXMLファイルに変換することができます。  
また、作成したメタデータファイルをもとに、[ResourceSync](https://www.openarchives.org/rs/1.1/resourcesync)のXMLファイルを作成することができます。

## 使い方

### 準備

1. Pythonをインストールします。Windowsをお使いの場合、[MicrosoftのWebサイト](https://learn.microsoft.com/ja-jp/windows/python/beginners)にインストールや動作確認の方法が掲載されています。
1. [Visual Studio Code](https://code.visualstudio.com/)(VSCode)をインストールします。
1. VSCodeのユーザインターフェースを日本語で表示するため、[Japanese Language Pack for VS Code](https://marketplace.visualstudio.com/items?itemName=MS-CEINTL.vscode-language-pack-ja)をインストールします。VSCodeを起動してCtrlキーとPキーを同時に押し、表示された入力欄に以下の文字列を入力して、Enterキーを押します。
    ```
    ext install MS-CEINTL.vscode-language-pack-ja
    ```
1. VSCodeの[YAML拡張機能](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)をインストールします。先ほどと同様に、VSCodeを起動した状態でCtrlキーとPキーを同時に押し、表示された入力欄に以下の文字列を入力して、Enterキーを押します。
    ```
    ext install redhat.vscode-yaml
    ```
1. VSCodeの画面上部のメニューから"ターミナル"を選びます。ターミナルのウインドウが画面下部に開くので、以下のコマンドを実行して、必要なPythonのモジュールをインストールします。
    ```sh
    pip install pyyaml resync
    ```
1. [ツールのファイル一式のzipファイル](https://github.com/nabeta/jpcoar-schema-helper/archive/refs/heads/main.zip)をダウンロードして、適当なフォルダに展開します。ここでは`jpcoar-schema-helper-main`フォルダに展開したものとします。

### メタデータの書き方

1. 展開した`jpcoar-schema-helper-main`フォルダを開き、`samples`フォルダの中にあるサンプルのメタデータファイルを、`work`フォルダの中にコピーします。ファイル名は半角英数文字とし、拡張子は".yaml"のままにしておいてください。
1. VSCodeで`jpcoar-schema-helper-main`フォルダを開きます。
1. VSCodeのファイル一覧から、`work`フォルダにコピーしたメタデータファイルを開き、メタデータの編集と保存を行ってください。このとき、ファイルの1行目にある以下の記述は削除しないでください。
   ```yaml
   # yaml-language-server: $schema=../schema/jpcoar.json
   ```

### JPCOARスキーマのXMLへの変換　

1. VSCodeのターミナルで`jpcoar.py`スクリプトを実行し、YAMLで作成したメタデータファイルをJPCOARスキーマのXMLファイルに変換します。まずテストとして、以下のコマンドで、サンプルのメタデータファイルがXMLに変換され、表示されることを確認してください。
    ```sh
    ./jpcoar.py samples/01_departmental_bulletin_paper_oa.yaml
    ```
    テストが成功したら、`work`フォルダに保存したYAMLのメタデータファイルを、XMLファイルに変換して保存します。以下のコマンドは、`my_article.yaml`という名前で作成したYAMLのメタデータファイルをXMLに変換し、`public`フォルダの中に`my_article.xml`というファイル名で保存する例です。
    ```sh
    ./jpcoar.py work/my_article.yaml > public/my_article.xml
    ```
1. VSCodeのターミナルで`resourcesync.py`スクリプトを実行し、ResourceSyncのXMLファイルを作成して`public`フォルダの中に保存します。`https://example.com`は、実際にファイルを公開するWebサーバの名前に変更してください（テストとして実行している場合は、変更する必要はありません）。
    ```sh
    ./resourcesync.py https://example.com > public/resourcelist.xml
    ```
1. `public`フォルダに保存されたファイルをWebサーバにアップロードします。

## 作成の背景

- テキストエディタでJPCOARスキーマのメタデータを書けるようにしたい
- Pythonなどのプログラミング言語でJPCOARスキーマのメタデータを書けるようにしたい
- [JAIRO Cloud](https://jpcoar.repo.nii.ac.jp/page/42)以外の環境からメタデータを[IRDB](https://irdb.nii.ac.jp/)に送付したい
- 静的なファイルのアップロードだけでデータリポジトリを運用できるようにしたい

## TODO

- 論文以外のメタデータ項目への対応を追加する
- メタデータの記述対象となる実ファイルの情報を自動的にメタデータファイルに追加する
- ResourceSyncの`capabilitylist.xml`と`changelist.xml`を作成できるようにする
- レコードIDの採番方法を決める
- YAMLのプロパティ名を整理する

## 作者

田辺浩介 ([@nabeta](https://github.com/nabeta))
