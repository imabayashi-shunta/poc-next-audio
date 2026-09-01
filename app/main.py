import os
import shutil
from dotenv import load_dotenv
from parser import parse_xml, parse_csv, parse_video, transcribe_video
from db import insert_xml_data, insert_csv_data, insert_video_data, insert_transcription_data

load_dotenv()

# EFS上のディレクトリ構成
EFS_BASE = "/mnt/efs/sample_data/PoC_test"
INCOMING_DIR = os.path.join(EFS_BASE, "incoming")   # 未処理ファイルを置くフォルダ
PROCESSED_DIR = os.path.join(EFS_BASE, "processed") # 処理済みファイルの移動先フォルダ

def process_file(file_path: str):
    """ファイルの種類に応じて解析・DB登録を行う"""
    ext = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)
    print(f"【処理開始】: {file_name}")

    if ext == ".xml":
        data = parse_xml(file_path)
        if data: insert_xml_data(data)

    elif ext == ".csv":
        data = parse_csv(file_path)
        if data: insert_csv_data(data)

    elif ext == ".mp4":
        # メタデータ解析 ＆ 文字起こし
        v_data = parse_video(file_path)
        if v_data: insert_video_data(v_data)

        t_data = transcribe_video(file_path)
        if t_data: insert_transcription_data(t_data)

def main():
    print("--- 定期実行タスク開始 ---")
    os.makedirs(INCOMING_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # incoming フォルダ内の全ファイルを取得
    files = [os.path.join(INCOMING_DIR, f) for f in os.listdir(INCOMING_DIR) if os.path.isfile(os.path.join(INCOMING_DIR, f))]

    if not files:
        print("未処理のファイルはありません。処理を終了します。")
        return

    for file_path in files:
        try:
            # 1. 解析とDB登録
            process_file(file_path)

            # 2. 処理完了後、processed フォルダへ移動
            dest_path = os.path.join(PROCESSED_DIR, os.path.basename(file_path))
            shutil.move(file_path, dest_path)
            print(f"【移動完了】: {os.path.basename(file_path)} -> processed/")
        except Exception as e:
            print(f"【エラー】ファイル処理に失敗しました ({file_path}): {e}")

    print("--- 全ファイルの処理が完了しました ---")

if __name__ == "__main__":
    main()