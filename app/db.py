import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# 1. XMLデータの登録処理
def insert_xml_data(data_list: list[dict]):
    """XMLから抽出したデータをDBに登録する"""
    if not data_list:
        print("XMLデータが存在しないためスキップします。")
        return

    query = """
        INSERT INTO xml_metadata (filename, start_timecode, duration)
        VALUES (%s, %s, %s);
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            records = [
                (d.get("Filename"), d.get("StartTimecode"), d.get("Duration"))
                for d in data_list
            ]
            cur.executemany(query, records)
        conn.commit()
        print("XMLデータをDBに正常に登録しました。")
    except Exception as e:
        conn.rollback()
        print(f"XML DB登録エラー: {e}")
    finally:
        conn.close()


# 2. CSVデータの登録処理
def insert_csv_data(data_list: list[dict]):
    """変則CSV（申請情報 + 映像明細情報）をDBに登録する"""
    if len(data_list) < 2:
        print("エラー: CSVデータが不足しています")
        return

    req_data = data_list[0]   # 1〜2行目のデータ
    item_data = data_list[1]  # 4〜5行目のデータ

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. 申請情報の登録 (RETURNING id で登録された親IDを取得)
            insert_req_query = """
                INSERT INTO csv_requests (
                    purpose, destination, favorite_list_name, applicant_name, applicant_dept_root,
                    applicant_dept, applicant_contact, usage_purpose, analysis_lang_type, responsible_person,
                    assigned_person, phone_number, extension_number, program_name, oa_scheduled_date,
                    oa_scheduled_time, preferred_datetime, comment_1, comment_2, comment_3, user_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id;
            """
            cur.execute(insert_req_query, (
                req_data.get("用途"), req_data.get("転送先"), req_data.get("お気に入りリスト名"),
                req_data.get("申請者氏名"), req_data.get("申請者原局"), req_data.get("申請者所属"),
                req_data.get("申請者連絡先"), req_data.get("使用目的"), req_data.get("解析言語区分"),
                req_data.get("責任者"), req_data.get("担当者"), req_data.get("電話番号"),
                req_data.get("内線番号"), req_data.get("使用番組"), req_data.get("OA予定日"),
                req_data.get("OA予定時刻"), req_data.get("希望日時"), req_data.get("コメント"),
                req_data.get("コメント_1"), req_data.get("コメント_2"), req_data.get("ユーザーID")
            ))
            
            # 発行された request_id を取得
            request_id = cur.fetchone()[0]

            # 2. 映像明細情報の登録
            insert_item_query = """
                INSERT INTO csv_items (
                    request_id, video_id, representative_item, meta_id, box_id,
                    in_point_tc, out_point_tc, in_point_ftc, out_point_ftc
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cur.execute(insert_item_query, (
                request_id,
                item_data.get("映像ID"), item_data.get("代表項目"), item_data.get("メタID"),
                item_data.get("BOX ID"), item_data.get("IN点（TC）"), item_data.get("OUT点（TC）"),
                item_data.get("IN点（FTC）"), item_data.get("OUT点（FTC）")
            ))

        conn.commit()
        print("CSVデータをDBに正常に登録しました。")
    except Exception as e:
        conn.rollback()
        print(f"CSV DB登録エラー: {e}")
    finally:
        conn.close()


# 3. 映像（MP4）データの登録処理
def insert_video_data(data_list: list[dict]):
    """動画メタデータをDBに登録する"""
    if not data_list:
        print("映像データが存在しないためスキップします。")
        return

    query = """
        INSERT INTO video_metadata (filename, file_size_bytes, duration_sec, width, height, frame_rate, codec)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            records = [
                (
                    d.get("ファイル名"),
                    d.get("ファイルサイズ(bytes)"),
                    d.get("再生時間(s)"),
                    d.get("Width"),
                    d.get("Height"),
                    d.get("FrameRate"),
                    d.get("Codec")
                )
                for d in data_list
            ]
            cur.executemany(query, records)
        conn.commit()
        print("映像データをDBに正常に登録しました。")
    except Exception as e:
        conn.rollback()
        print(f"映像 DB登録エラー: {e}")
    finally:
        conn.close()


# 映像ファイルの文字起こし結果登録処理
def insert_transcription_data(data: dict):
    """
    文字起こし結果（親テーブル & 子テーブル）を DB にトランザクション登録する
    """
    if not data or "parent" not in data or "words" not in data:
        print("文字起こしデータが不正または存在しないためスキップします。")
        return

    parent = data["parent"]
    words = data["words"]
    transcription_id = parent.get("transcription_id")

    if not transcription_id:
        print("エラー: transcription_id が取得できていないためDB登録を中止します。")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. 親テーブル (transcriptions) への登録
            insert_parent_query = """
                INSERT INTO transcriptions (
                    language_code, language_probability, text, channel_index,
                    additional_formats, transcription_id, entities, audio_duration_secs
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (transcription_id) DO NOTHING;
            """
            cur.execute(insert_parent_query, (
                parent.get("language_code"),
                parent.get("language_probability"),
                parent.get("text"),
                parent.get("channel_index"),
                parent.get("additional_formats"),
                transcription_id,
                parent.get("entities"),
                parent.get("audio_duration_secs")
            ))

            # 2. 子テーブル (transcription_words) への一括登録
            if words:
                insert_words_query = """
                    INSERT INTO transcription_words (
                        transcription_id, word_index, text, start_time, end_time,
                        type, speaker_id, logprob, characters, channel_index
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                word_records = [
                    (
                        transcription_id,
                        w["word_index"],
                        w["text"],
                        w["start_time"],
                        w["end_time"],
                        w["type"],
                        w["speaker_id"],
                        w["logprob"],
                        w["characters"],
                        w["channel_index"]
                    )
                    for w in words
                ]
                cur.executemany(insert_words_query, word_records)

        conn.commit()
        print(f"文字起こしデータ（ID: {transcription_id} / 単語数: {len(words)}件）をDBに正常に登録しました。")
    except Exception as e:
        conn.rollback()
        print(f"文字起こし DB登録エラー: {e}")
    finally:
        conn.close()