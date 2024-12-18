# JPCOAR Schema Helper

[JPCOARスキーマ](https://schema.irdb.nii.ac.jp/ja/schema) 2.0のメタデータを、YAMLを使って少しかんたんに記述できるようにするためのツールです。作成したYAMLファイルは、付属のスクリプトでJPCOARスキーマのXMLファイルに変換することができます。

## 使い方

### メタデータの書き方

1. [Visual Studio Code](https://code.visualstudio.com/)(VSCode)をインストールします。
1. VSCodeの[YAML拡張機能](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)をインストールします。
1. GitHubリポジトリの"Code"から"Download ZIP"を選択し、ツールのファイル一式をダウンロードして、適当なフォルダに展開します。
1. samplesフォルダの中にあるサンプルのメタデータファイルを、workフォルダにコピーします。ファイル名は半角英数文字とし、拡張子は".yaml"のままにしておいてください。
1. VSCodeで上記のフォルダを開きます。
1. VSCodeのファイル一覧から、workフォルダにコピーしたメタデータファイルを開き、編集と保存を行います。

### JPCOARスキーマのXMLへの変換　

1. 必要なPythonのモジュールをインストールします。venv環境での実行をおすすめします。
    ```sh
    pip install pyyaml
    ```
1. VSCodeのメニューから"Terminal"を選びます。ターミナルのウインドウが画面下部に開きます。
1. ターミナルで`jpcoar.py`スクリプトを実行し、YAMLで作成したメタデータファイルをJPCOARスキーマのXMLファイルに変換します。まずテストとして、以下のコマンドで、サンプルのメタデータファイルがXMLに変換され、表示されることを確認してください。
    ```sh
    ./jpcoar.py samples/01_departmental_bulletin_paper_oa.yaml
    ```
    テストが成功したら、workフォルダに保存したYAMLのメタデータファイルを、XMLファイルに変換して保存します。以下のコマンドは、`my_article.yaml`という名前で作成したYAMLのメタデータファイルをXMLに変換し、同じworkフォルダの中に`my_article.xml`というファイル名で保存する例です。
    ```sh
    ./jpcoar.py work/my_article.yaml > work/my_article.xml
    ```

## 作成の背景

- テキストエディタでJPCOARスキーマのメタデータを書けるようにしたい
- Pythonなどのプログラミング言語でJPCOARスキーマのメタデータを書けるようにしたい
- [JAIRO Cloud](https://jpcoar.repo.nii.ac.jp/page/42)以外の環境からメタデータを[IRDB](https://irdb.nii.ac.jp/)に送付したい

## 想定する作業フロー

1. フォルダを作成し、論文や研究データのファイルをその中に保存する
1. YAMLで論文や研究データのメタデータファイルを作成し、フォルダの中に保存する
1. `jpcoar.py`スクリプトを用いて、フォルダ内のメタデータファイルをJPCOARスキーマのXMLファイルに変換する
1. スクリプト（今後追加予定）を用いて、フォルダ内のメタデータファイルをもとに、[ResourceSync](https://www.openarchives.org/rs/1.1/resourcesync)のXMLファイルを作成する
1. フォルダとResourceSyncのXMLファイルをWebサーバにアップロードする
1. IRDBがResourceSyncのXMLファイルとメタデータファイルを収集できるようにようにする

## 作者

田辺浩介 ([@nabeta](https://github.com/nabeta))
