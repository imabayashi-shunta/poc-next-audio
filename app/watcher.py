import os
import shutil
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from main import process_file, INCOMING_DIR, PROCESSED_DIR

class FileIncomingHandler(FileSystemEventHandler):
    def on_created(self, event):
        # ディレクトリ作成イベントは無視
        if event.is_directory:
            return
        
        file_path = event.src_path
        print(f"【検知】新しいファイルを検出しました: {file_path}")
        
        # ファイルの書き込み（転送）が完全に終わるまで少し待機
        time.sleep(2)
        
        try:
            # 既存の解析・DB登録ロジックを実行
            process_file(file_path)
            
            # 処理完了後、processed フォルダへ移動
            dest_path = os.path.join(PROCESSED_DIR, os.path.basename(file_path))
            shutil.move(file_path, dest_path)
            print(f"【移動完了】: {os.path.basename(file_path)} -> processed/")
        except Exception as e:
            print(f"【エラー】リアルタイム処理に失敗しました ({file_path}): {e}")

def start_watching():
    print(f"--- Watchdogによるリアルタイム監視を開始します ({INCOMING_DIR}) ---")
    os.makedirs(INCOMING_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    event_handler = FileIncomingHandler()
    observer = Observer()
    observer.schedule(event_handler, path=INCOMING_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()