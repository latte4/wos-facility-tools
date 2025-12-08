# ホワイトアウトサバイバル　工程ステーション保護解除時間計算ツール

ホワイトアウトサバイバルの工程ステーション保護解除時間を計算し、  
Google カレンダーへ一括登録するためのツールです。

## 機能

- **時間計算ツール (`station_calc.py`)**
  - スクリーンショット取得日時を入力して、その時間を基準に解除日時のテキストファイルを作成する

- **Googleカレンダー登録ツール (`station_gcal.py`)**
  - 時間計算ツール (`station_calc.py`)で作成したテキストファイルから、Google カレンダーに一括登録する

## 前提

- Python 3.10+ がインストールされていること。
- Tesseract がインストールされていること。
- タイムゾーンは `Asia/Tokyo` 前提で動作。
- 同盟⇒拠点争奪⇒工程ステーション のスクリーンショット(`wos.png`)
- Google カレンダー連携を使うためGoogle Cloud Console で
  Calendar API を有効化し、デスクトップアプリ用 OAuth クライアントの
  `credentials.json` を同じディレクトリに置いておくこと。

## 必要なライブラリ

共通で必要なもの
```
pip install --upgrade pytesseract opencv-python Pillow
```
Google カレンダー連携に必要なもの
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 作成されるイベント

- カレンダー ID: `primary`
- タイトル: `ステーション保護解除`
- タイムゾーン: `Asia/Tokyo`
- 開始時刻: 計算された解除時刻
- 終了時刻: 開始から 5 分後
- 通知: 開始 2 分前にポップアップ通知 1 回（default 通知は無効化）

---

