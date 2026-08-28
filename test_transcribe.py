import os
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# .env から環境変数を読み込む場合（設定ファイル代わり）
load_dotenv()

# 設定（setting.json の内容をここで指定）
CONFIG = {
    "APIKey": os.getenv("ELEVENLABS_API_KEY"),
    "audioPath": "sample_data/PoC_test/Mojiokoshi_test/15_one.mp4",
    "outputPath": "output/result.txt"
}

# APIキーが設定されているかチェック（CONFIGの直後に記述）
if not CONFIG["APIKey"]:
    raise ValueError("エラー: .env ファイルに ELEVENLABS_API_KEY が設定されていません。")

# APIキーの設定
key = CONFIG["APIKey"]
#print("APIキー",key)
elevenlabs = ElevenLabs(
  api_key=key,
)

audio_path = Path(CONFIG["audioPath"])

with open(audio_path, "rb") as f:
    audio_data = BytesIO(f.read())

# APIの呼び出し
try:
    transcription = elevenlabs.speech_to_text.convert(
        model_id="scribe_v2",
        file=audio_data,
    )
except Exception as e:
    # Exceptionオブジェクトの属性チェック（安全のため追加）
    print("STATUS:", getattr(e, 'status_code', e))
    print("BODY:", getattr(e, 'body', ''))
    raise

# レスポンスから登録用にファイルの作成
file_path = Path(CONFIG["outputPath"])
# 出力用ディレクトリが存在しない場合は作成
file_path.parent.mkdir(parents=True, exist_ok=True)

print(file_path.resolve())
try:
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        # 属性を順番に取り出して改行出力
        for k, value in transcription.__dict__.items():
            f.write(f"{k}: {value}\n")
    if file_path.exists():
        print(f"出力完了: {file_path}")

#    print(transcription)

except Exception as e:
    print(f"出力失敗: {e}")


print("完了")