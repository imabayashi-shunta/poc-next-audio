import os
from dotenv import load_dotenv
from parser import parse_xml, parse_csv, parse_video
from db import insert_xml_data, insert_csv_data, insert_video_data
import shutil

# ソース（Dockerイメージ内のパス）と同期先（EFSのパス）
LOCAL_DATA_DIR = "sample_data"
EFS_DATA_DIR = "/mnt/efs/sample_data"

def upload_to_efs():
    print("--- EFSへのデータ転送開始 ---")
    if os.path.exists(LOCAL_DATA_DIR):
        # sample_data フォルダごと EFS 側にコピー
        shutil.copytree(LOCAL_DATA_DIR, EFS_DATA_DIR, dirs_exist_ok=True)
        print(f"【成功】{LOCAL_DATA_DIR} を {EFS_DATA_DIR} へコピーしました。")
    else:
        print(f"【エラー】{LOCAL_DATA_DIR} が存在しません。")

if __name__ == "__main__":
    upload_to_efs()


# まとめてコメントアウト
"""
load_dotenv()

def main():

    print("--- データ解析 & DB登録 PoC 開始 ---")

    # 1. XMLの解析とDB登録
    xml_file = "sample_data/PoC_test/STM2026072800333/EXN_STM2026072800333_20260728143556.XML"
    xml_data = parse_xml(xml_file)
    if xml_data:
        insert_xml_data(xml_data)

    # 2. CSVの解析とDB登録
    csv_file = "sample_data/PoC_test/EXI_天気：葛飾花火大会_20260728143554.CSV"
    csv_data = parse_csv(csv_file)
    if csv_data:
        insert_csv_data(csv_data)

    # 3. 映像ファイルの解析とDB登録
    mp4_file = "sample_data/PoC_test/20260818_次期音声PoCの映像素材.mp4"
    mp4_data = parse_video(mp4_file)
    if mp4_data:
        insert_video_data(mp4_data)

    print("--- 処理が完了しました ---")

if __name__ == "__main__":
    main()
"""