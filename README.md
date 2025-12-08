# ホワイトアウトサバイバル　工程ステーション保護解除時間計算ツール

ホワイトアウトサバイバル の「ステーション保護解除」の時間を自動計算し、  
Googleカレンダーに登録するためのツールです。

## 機能

-  同盟⇒拠点争奪⇒工程ステーション　のスクリーンショットから保護状態時間の取得
-  Googleカレンダーへの自動登録

## 前提

- Python 3.6以上
- 以下のPythonライブラリ:
  - 
 
## 使い方

python station_calc.py
でスクリーンショットから時間計算

## 3. Google カレンダー登録ツール

ファイル例: `station_gcal.py`  
役割: ICS を介さず、Google カレンダー API 経由で直接予定を作成します。

「API を使って自動登録したい派」の場合はこちらを使います。

### 事前準備（Google 側）

1. Google Cloud Console でプロジェクト作成。[web:159][web:167]
2. 「API とサービス → ライブラリ」で「Google Calendar API」を有効化。[web:169]
3. 「API とサービス → 認証情報」で「OAuth クライアント ID」を作成。
   - アプリケーションの種類: デスクトップ アプリ
4. ダウンロードした `credentials.json` を、このリポジトリ直下に配置します。
5. 初回実行時にブラウザが開き、Google アカウントへのアクセス許可を求められます。
   - 許可すると `token.json` が自動生成され、次回以降は再認証不要になります。[web:159][web:175]

### 追加インストール

pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

text

### 使い方

python station_gcal.py

text

1. 基準日時を `yyyy/mm/dd hh:mm:ss` で入力。
2. `times.txt` の内容に基づいて計算結果が表示されます。
3. `y` を入力すると、`primary` カレンダーに予定がまとめて作成されます。

出力例:

これらの予定を Google カレンダー (primary) に登録しますか？ (y/n): y

Google に接続中... ブラウザが開いたら認証してください。
認証完了。予定を登録します。
登録完了: 01 -> 2025-11-28 13:10:47 (eventId=xxxxxxxxxxxxx)
...
すべての予定の登録が完了しました。Google カレンダーを確認してみてください。

text

### 作成されるイベント

- カレンダー ID: `primary`
- タイトル: `ステーション保護解除`
- タイムゾーン: `Asia/Tokyo`
- 開始時刻: 計算された解除時刻
- 終了時刻: 開始から 5 分後
- 通知: 開始 2 分前にポップアップ通知 1 回（default 通知は無効化）

---

