#!/usr/bin/env python3
import argparse
import glob
import logging
import os
import re
import sys
import yaml
from datetime import datetime, date, timedelta
from collections import Counter
import config
import html
import jalc
import jpcoar
import migrate
import resourcesync
import ro_crate

# ログ出力の設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def main():
  # 引数の取得
  parser = argparse.ArgumentParser(
    prog = "togura.py",
    description = "Togura: 超シンプルな機関リポジトリ"
  )

  subparser = parser.add_subparsers(
    title = "サブコマンド",
    dest = "subcommand",
    required = True
  )

  generate_parser = subparser.add_parser(
    "generate",
    help = "HTMLファイルとメタデータファイルを出力します。"
  )

  migrate_parser = subparser.add_parser(
    "migrate",
    help = "他の機関リポジトリから本文ファイルとメタデータファイルをToguraに移行します。"
  )

  migrate_parser.add_argument(
    '--base-url', required=True, type=str, help='移行元のOAI-PMHのベースURL'
  )
  migrate_parser.add_argument(
    '--export-dir', required=True, type=str, help='ファイルの保存先のディレクトリ'
  )
  migrate_parser.add_argument(
    '--metadata-prefix', type=str, help='移行元のmetadataPrefix'
  )
  migrate_parser.add_argument(
    '--date-from', type=str, help='移行対象の開始日'
  )
  migrate_parser.add_argument(
    '--date-until', type=str, help='移行対象の終了日'
  )
  args = parser.parse_args()

  match args.subcommand:
    case "generate":
      generate()
    case "migrate":
      if args.metadata_prefix is None:
        metadata_prefix = "jpcoar_1.0"
      else:
        metadata_prefix = args.metadata_prefix
      if args.date_from is None:
        date_from = datetime.strftime(datetime.today() - timedelta(days = 30), '%Y-%m-%d')
      else:
        date_from = args.date_from

      if args.date_until is None:
        date_until = datetime.strftime(datetime.today(), '%Y-%m-%d')
      else:
        date_until = args.date_until

      migrate.migrate(args.base_url, metadata_prefix, date_from, date_until, args.export_dir)
    case _:
      main()

def generate():
  data_dir = "./work"
  output_dir = "./public"
  base_url = config.base_url()

  paths  = sorted(glob.glob(f"{data_dir}/*"))
  if len(paths) != len(set(paths)):
    duplicate_ids = ", ".join(Counter(paths).items())
    raise Exception(f"エラー: 登録番号 {duplicate_ids} が重複しています。別の番号を使用してください。")

  for path in paths:
    entry_id = os.path.basename(path).split("_")[0]

    if not re.search(r'\d+', entry_id):
      raise Exception(f"エラー: 登録番号 {entry_id} の書式が正しくありません。半角の数字に変更してください。また、登録番号のあとに _ （アンダースコア）を入力していることを確認してください。")

    with open(f"{path}/jpcoar20.yaml", encoding = "utf-8") as file:
      entry = yaml.load(file, Loader = yaml.Loader)
      entry["id"] = entry_id

      #try:
      root = jpcoar.generate(entry, base_url)
      jpcoar.add_directory_file(path, entry, root, base_url)
      ro_crate.generate(path, output_dir, root)
      jalc.generate(path, output_dir, base_url)
      #except KeyError as e:
      #  logger.error(f"invalid metadata in {path}")
      #  continue

  html.generate(data_dir, output_dir, base_url)
  resourcesync.generate(output_dir, base_url)

if __name__ == "__main__":
  main()
