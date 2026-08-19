import os
from dotenv import load_dotenv
from parser import parse_xml, parse_csv, parse_video
from pprint import pprint

load_dotenv()

def main():
    print("--- データ解析 PoC 開始 ---")

    # XMLの検証
    xml_data = parse_xml("sample_data/PoC_test/STM2026072800333/EXN_STM2026072800333_20260728143556.XML")
    pprint(f"【XML抽出結果】\n{xml_data}")
    print("")

    # CSVの検証
    csv_data = parse_csv("sample_data/PoC_test/EXI_天気：葛飾花火大会_20260728143554.CSV")
    pprint(f"【CSV抽出結果】\n{csv_data}")
    print("")

    # 映像ファイルの検証
    mp4_data = parse_video("sample_data/PoC_test/20260818_次期音声PoCの映像素材.mp4")
    pprint(f"【MP4抽出結果】\n{mp4_data}")
    print("")

if __name__ == "__main__":
    main()