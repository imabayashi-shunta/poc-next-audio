import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from pymediainfo import MediaInfo


# XMLの解析処理
def parse_xml(file_path: str) -> list[dict]:
    """XMLファイルを解析して必要なタグの情報を取得する"""
    path = Path(file_path)
    if not path.exists():
        print(f"エラー: ファイルが存在しません -> {file_path}")
        return []

    tree = ET.parse(path)
    root = tree.getroot()

    results = []
    # XML構造に合わせてタグ名（例: 'UpdateFile'）を指定して繰り返し取得
    for Up in root.findall(".//UpdateFile"):
        # タグの値を取得する設定
        data = {
            "Filename": Up.find("Filename").text if Up.find("Filename") is not None else None,
            "StartTimecode": Up.find("StartTimecode").text if Up.find("StartTimecode") is not None else None,
            "Duration": Up.find("Duration").text if Up.find("Duration") is not None else None,
        }
        results.append(data)

    return results


# CSVの解析処理
def parse_csv(file_path: str) -> list[dict]:
    """変則的なCSV（ヘッダー・値・空行の繰り返し）を読み込んで辞書型のリストで返す"""
    path = Path(file_path)
    if not path.exists():
        print(f"エラー: ファイルが存在しません -> {file_path}")
        return []

    results = []
    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        current_header = None

        for row in reader:
            # 空行（または要素がすべて空の行）は無視してリセット
            if not row or not any(row):
                current_header = None
                continue

            # ヘッダーが未保持の場合は現在の行をヘッダーとしてセット
            if current_header is None:
                current_header = row
            else:
                # ヘッダー保持済みの場合は値の行として処理し、辞書を作成
                data_dict = dict(zip(current_header, row))
                results.append(data_dict)
                current_header = None  # 次のブロックに備えてリセット

    return results


# 映像ファイルの解析処理
def parse_video(file_path: str) -> list[dict]:
    """MP4ファイルを解析して動画のメタデータ情報を取得し、辞書型のリストで返す"""
    path = Path(file_path)
    if not path.exists():
        print(f"エラー: ファイルが存在しません -> {file_path}")
        return []

    # MediaInfoで動画ファイルを解析
    media_info = MediaInfo.parse(str(path))
    
    filename = path.name
    file_size = path.stat().st_size
    duration = None
    width = None
    height = None
    frame_rate = None
    codec = None

    for track in media_info.tracks:
        if track.track_type == 'General':
            # ミリ秒単位で取得されるため秒に変換
            if track.duration:
                duration = float(track.duration) / 1000
        elif track.track_type == 'Video':
            width = track.width
            height = track.height
            frame_rate = track.frame_rate
            codec = track.format

    data = {
        "ファイル名": filename,
        "ファイルサイズ(bytes)": file_size,
        "再生時間(s)": duration,
        "Width": width,
        "Height": height,
        "FrameRate": frame_rate,
        "Codec": codec,
    }

    # 他の関数と統一して list[dict] 形式で返す
    return [data]