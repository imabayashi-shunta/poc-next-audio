import os
from dotenv import load_dotenv
from parser import parse_xml, parse_csv, parse_video
from db import insert_xml_data, insert_csv_data, insert_video_data

load_dotenv()

# ベースパスをEFS上のディレクトリに変更
EFS_BASE = "/mnt/efs/sample_data/PoC_test"

def main():

    print("--- EFSデータ参照 & DB登録 PoC 開始 ---")

    # 1. XMLの解析とDB登録
    xml_file = os.path.join(EFS_BASE, "STM2026072800333/EXN_STM2026072800333_20260728143556.XML")
    xml_data = parse_xml(xml_file)
    if xml_data:
        insert_xml_data(xml_data)

    # 2. CSVの解析とDB登録
    csv_file = os.path.join(EFS_BASE, "EXI_天気：葛飾花火大会_20260728143554.CSV")
    csv_data = parse_csv(csv_file)
    if csv_data:
        insert_csv_data(csv_data)

    # 3. 映像ファイルの解析とDB登録
    mp4_file = os.path.join(EFS_BASE, "20260818_次期音声PoCの映像素材.mp4")
    mp4_data = parse_video(mp4_file)
    if mp4_data:
        insert_video_data(mp4_data)

    print("--- EFS経由でのDB登録処理が完了しました ---")

if __name__ == "__main__":
    main()