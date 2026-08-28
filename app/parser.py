import os
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from pymediainfo import MediaInfo
from elevenlabs.client import ElevenLabs


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


# 映像ファイルの文字起こし解析処理
def transcribe_video(file_path: str) -> dict:
    """
    EFS上の映像ファイルを読み込み、ElevenLabs APIで文字起こしを実行して
    親テーブル・子テーブル用の辞書データを返す
    """
    path = Path(file_path)
    if not path.exists():
        print(f"エラー: 文字起こし対象ファイルが存在しません -> {file_path}")
        return {}

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("エラー: ELEVENLABS_API_KEY が環境変数に設定されていません。")
        return {}

    client = ElevenLabs(api_key=api_key)

    try:
        # EFS上の動画ファイルをバイナリで読み込んでAPIに送信
        with open(path, "rb") as f:
            transcription = client.speech_to_text.convert(
                model_id="scribe_v2",
                file=f,
            )

        # 1. 親テーブル (transcriptions) 用のデータ作成
        parent_data = {
            "language_code": getattr(transcription, "language_code", ""),
            "language_probability": getattr(transcription, "language_probability", 0.0),
            "text": getattr(transcription, "text", ""),
            "channel_index": getattr(transcription, "channel_index", None),
            "additional_formats": str(getattr(transcription, "additional_formats", "")) if getattr(transcription, "additional_formats", None) is not None else None,
            "transcription_id": getattr(transcription, "transcription_id", ""),
            "entities": str(getattr(transcription, "entities", "")) if getattr(transcription, "entities", None) is not None else None,
            "audio_duration_secs": getattr(transcription, "audio_duration_secs", 0.0),
        }

        # 2. 子テーブル (transcription_words) 用のデータ作成
        words_data = []
        raw_words = getattr(transcription, "words", []) or []
        
        for idx, w in enumerate(raw_words):
            # オブジェクト属性を取得（辞書またはモデル属性に対応）
            get_val = lambda key: getattr(w, key, None) if not isinstance(w, dict) else w.get(key)
            
            chars = get_val("characters")
            
            words_data.append({
                "word_index": idx,
                "text": get_val("text") or "",
                "start_time": get_val("start") or 0.0,
                "end_time": get_val("end") or 0.0,
                "type": get_val("type") or "word",
                "speaker_id": get_val("speaker_id"),
                "logprob": get_val("logprob") or 0.0,
                "characters": str(chars) if chars is not None else None,
                "channel_index": get_val("channel_index"),
            })

        return {
            "parent": parent_data,
            "words": words_data
        }

    except Exception as e:
        print(f"文字起こし API 実行エラー: {e}")
        return {}