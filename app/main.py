import os
from dotenv import load_dotenv
from parser import parse_xml, parse_csv, parse_video
from db import insert_xml_data, insert_csv_data, insert_video_data

load_dotenv()

# EFSのマウント先パス（タスク定義で指定したコンテナパス）
EFS_DIR = "/mnt/efs"
FILE_PATH = os.path.join(EFS_DIR, "sample.txt")

def main():

    print("--- EFS テスト開始 ---")
    
    # 1. テスト用ファイルの書き込み
    try:
        os.makedirs(EFS_DIR, exist_ok=True)
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            f.write("Hello, Amazon EFS from ECS Fargate!\n")
        print(f"ファイルの書き込みに成功しました: {FILE_PATH}")
    except Exception as e:
        print(f"書き込みエラー: {e}")
        return

    # 2. テスト用ファイルの読み込み検証
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        print("--- ファイルの中身 ---")
        print(content)
        print("--- EFS 読み込み検証成功 ---")
    except Exception as e:
        print(f"読み込みエラー: {e}")

    """
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
    """

if __name__ == "__main__":
    main()