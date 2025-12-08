import os
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ======== 基本設定 ========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TIMES_FILE = os.path.join(SCRIPT_DIR, "times.txt")
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")

# カレンダーAPIで予定作成に必要なスコープ
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

TIMEZONE = "Asia/Tokyo"  # イベントのタイムゾーン
CALENDAR_ID = "primary"  # 追加先カレンダー


# ======== 時間処理まわり ========
def parse_duration(line: str) -> timedelta:
    """
    'hh:mm:ss' または 'Xd hh:mm:ss' を timedelta に変換
    """
    line = line.strip()
    if not line:
        return None

    days = 0
    time_part = line

    # 'Xd hh:mm:ss' 形式の場合
    if "d " in line:
        d_part, time_part = line.split("d ")
        days = int(d_part)

    h, m, s = time_part.split(":")
    return timedelta(days=days, hours=int(h), minutes=int(m), seconds=int(s))


def read_times():
    """
    times.txt を読み込んで [(元の文字列, timedelta), ...] を返す
    """
    items = []
    with open(TIMES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue
            td = parse_duration(raw)
            if td is not None:
                items.append((raw, td))
    return items


def ask_base_time():
    """
    ユーザーに 'yyyy/mm/dd hh:mm:ss' 形式で時刻を入力させて datetime を返す
    例: 2025/11/28 09:30:00
    """
    while True:
        s = input(
            "スクリーンショットの取得時刻を yyyy/mm/dd hh:mm:ss 形式で入力してください"
            "（例 2025/11/28 09:30:00）： "
        )
        try:
            base_dt = datetime.strptime(s, "%Y/%m/%d %H:%M:%S")
            return base_dt
        except ValueError:
            print("フォーマットが違います。もう一度入力してください。")


# ======== Google カレンダー API 認証 ========

def get_calendar_service():
    """
    OAuth2 で認証し、Calendar API の service オブジェクトを返す
    token.json があれば再利用し、失効していたらリフレッシュする。[web:159][web:167][web:171]
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "credentials.json がありません。Google Cloud Console から"
                    " ダウンロードしてこのスクリプトと同じフォルダに置いてください。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # 認証情報を保存
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service


# ======== メイン処理 ========

def main():
    # 1) times.txt 読み込み
    if not os.path.exists(TIMES_FILE):
        print("times.txt が見つかりません。同じフォルダに置いてください。")
        return

    items = read_times()  # (raw, timedelta) のリスト
    if not items:
        print("times.txt に有効な時間がありません。")
        return

    # 2) ユーザーから日時を入力
    base_dt = ask_base_time()
    print(f"基準日時: {base_dt}")

    # 3) 各時間を加算して結果表示
    results = []
    print("\n計算結果:")
    for idx, (raw, td) in enumerate(items, start=1):
        target = base_dt + td
        results.append(target)
        print(f"{idx:02d}: {raw} -> {target.strftime('%Y-%m-%d %H:%M:%S')}")

    # 4) Google カレンダーに登録するか確認
    ans = input(
        "\nこれらの予定を Google カレンダー (primary) に登録しますか？ (y/n): "
    ).strip().lower()
    if ans not in ("y", "yes"):
        print("Google カレンダーには登録しませんでした。")
        return

    # 5) Calendar API の service オブジェクト取得
    print("\nGoogle に接続中... ブラウザが開いたら認証してください。")
    service = get_calendar_service()
    print("認証完了。予定を登録します。")

    # 6) イベント作成
    created_ids = []
    for i, start in enumerate(results, start=1):
        # とりあえず5分枠
        end = start + timedelta(minutes=5)

        # RFC3339 形式に変換（タイムゾーン付き）[web:169][web:180]
        start_str = start.isoformat()
        end_str = end.isoformat()

        event = {
            "summary": "ステーション保護解除",
            "start": {
                "dateTime": start_str,
                "timeZone": TIMEZONE,
            },
            "end": {
                "dateTime": end_str,
                "timeZone": TIMEZONE,
            },
            # 2分前通知
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 2},
                ],
            },
        }

        created = service.events().insert(
            calendarId=CALENDAR_ID, body=event
        ).execute()
        created_ids.append(created.get("id"))

        print(
            f"登録完了: {i:02d} -> {start.strftime('%Y-%m-%d %H:%M:%S')} "
            f"(eventId={created.get('id')})"
        )

    print("\nすべての予定の登録が完了しました。Google カレンダーを確認してみてください。")


if __name__ == "__main__":
    main()
