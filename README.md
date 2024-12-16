# JPCOARスキーマの非公式JSON Schemaファイル

[JPCOARスキーマ](https://schema.irdb.nii.ac.jp/ja/schema) 2.0のメタデータをYAMLやJSONで記述するためのJSON Schemaファイルを提供することを目標とします。
記述のしやすさを優先するため、[XML Schema](https://github.com/JPCOAR/schema/blob/master/2.0/jpcoar_scm.xsd)をそのままJSON Schemaに変換するのではなく、簡略化した書式でJPCOARスキーマ準拠のメタデータを作成できるよう、新規にスキーマファイルを作成しています。

## 作成の背景

- テキストエディタでJPCOARスキーマのメタデータを書けるようにしたい
- Pythonなどのプログラミング言語でJPCOARスキーマのメタデータを書けるようにしたい

## 想定する作業フロー

1. フォルダを作成し、リポジトリに登録するファイルをその中に保存する
1. YAMLやJSONでメタデータファイルを作成し、フォルダの中に保存する
1. スクリプト（今後作成予定）を用いて、以下の作業を行う
    - フォルダ内のメタデータファイルをJPCOARスキーマのXMLファイルに変換する
    - 複数のフォルダ内のメタデータファイルに対して、[ResourceSync](https://www.openarchives.org/rs/1.1/resourcesync)のXMLファイルを作成する
1. フォルダとResourceSyncのXMLファイルをWebサーバにアップロードする
1. [IRDB](https://irdb.nii.ac.jp/)がResourceSyncのXMLファイルとメタデータファイルを収集できるようにようにする

## 作者

田辺浩介 ([@nabeta](https://github.com/nabeta))
