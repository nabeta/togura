#!/usr/bin/env python3
import glob
import logging
import os
import re
import yaml
from collections import Counter
import config
import jpcoar
import html
import ro_crate
import jalc
import resourcesync

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def main():
  data_dir = "./work"
  output_dir = "./public"
  base_url = config.base_url()

  paths  = sorted(glob.glob(f"{data_dir}/*"))
  if len(paths) != len(set(paths)):
    duplicate_ids = ", ".join(Counter(paths).items())
    raise Exception(f"エラー: 登録番号 {duplicate_ids} が重複しています。別の番号を使用してください。")

  for path in paths:
    entry_id = os.path.basename(path).split("_")[0][:2]

    if not re.search(r'\d+', entry_id):
      raise Exception(f"エラー: 登録番号 {entry_id} の書式が正しくありません。半角の数字に変更してください。また、登録番号のあとに _ （アンダースコア）を入力していることを確認してください。")

    os.makedirs(f"./pub1/{entry_id}", exist_ok = True)

    with open(f"{path}/jpcoar20.yaml", encoding = "utf-8") as file:
      entry = yaml.load(file, Loader = yaml.Loader)
      entry["id"] = entry_id

      root = jpcoar.generate(entry, base_url)
      jpcoar.add_directory_file(path, entry, root, base_url)
      ro_crate.generate(path, output_dir, root)
      jalc.generate(path, output_dir, base_url)
  html.generate(data_dir, output_dir, base_url)
  resourcesync.generate(output_dir, base_url)

if __name__ == "__main__":
  main()
