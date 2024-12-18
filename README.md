# JPCOAR Schema Helper

[JPCOARスキーマ](https://schema.irdb.nii.ac.jp/ja/schema) 2.0のメタデータを、YAMLを使って少しかんたんに記述できるようにするためのツールです。作成したYAMLファイルは、付属のスクリプトでJPCOARスキーマのXMLファイルに変換することができます。

## 使い方

1. 必要なPythonのモジュールをインストールします。venv環境での実行をおすすめします。
    ```sh
    pip install pyyaml
    ```
1. `samples`以下のサンプルファイルの要領で、メタデータファイルを作成します。
1. `jpcoar.py`スクリプトで、YAMLで作成したメタデータファイルをJPCOARスキーマのXMLファイルに変換します。以下のコマンドは、サンプルのメタデータファイルの変換を実行する例です。
    ```sh
    ./jpcoar.py samples/01_departmental_bulletin_paper_oa.yaml
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
