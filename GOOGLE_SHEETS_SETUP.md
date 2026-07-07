# Google Sheets 連携セットアップ

## 1. Google Cloud の設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. **APIとサービス → ライブラリ** で以下を有効化
   - Google Sheets API
   - Google Drive API
3. **APIとサービス → 認証情報 → 認証情報を作成 → サービスアカウント**
4. サービスアカウントを作成し、JSON キーをダウンロード
5. ダウンロードした JSON を `credentials/service-account.json` に配置（ローカル開発用）

## 2. スプレッドシートの準備

1. Google スプレッドシートを新規作成（例: `恋愛・結婚観アンケート回答`）
2. シート名を `回答` にする（または `GOOGLE_SHEET_NAME` で変更）
3. スプレッドシートの **共有** で、サービスアカウントのメール（`xxx@xxx.iam.gserviceaccount.com`）に **編集者** 権限を付与
4. スプレッドシート URL から ID を取得  
   `https://docs.google.com/spreadsheets/d/【ここがID】/edit`

## 3. 環境変数

| 変数名 | 必須 | 説明 |
|---|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Render等 | サービスアカウント JSON の全文（1行） |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | ローカル | JSON ファイルのパス |
| `GOOGLE_SPREADSHEET_ID` | 推奨 | スプレッドシート ID |
| `GOOGLE_SPREADSHEET_NAME` | 代替 | スプレッドシート名（ID 未設定時） |
| `GOOGLE_SHEET_NAME` | 任意 | シート名（既定: `回答`） |
| `SURVEY_SECRET` | 推奨 | Flask セッション用秘密鍵 |
| `PORT` | 任意 | 起動ポート（既定: 5000） |

ローカル例（`.env` を使う場合は `python-dotenv` を追加するか、手動で export）:

```powershell
$env:GOOGLE_SERVICE_ACCOUNT_FILE="credentials/service-account.json"
$env:GOOGLE_SPREADSHEET_ID="your-spreadsheet-id"
$env:GOOGLE_SHEET_NAME="回答"
python app.py
```

## 4. Render へのデプロイ

1. GitHub に `love-marriage-survey` をプッシュ
2. [Render](https://render.com/) → **New → Web Service**
3. リポジトリを接続
4. 設定:
   - **Root Directory**: `love-marriage-survey`（リポジトリ構成に応じて）
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. **Environment** に以下を追加:
   - `GOOGLE_SERVICE_ACCOUNT_JSON` = サービスアカウント JSON の全文（Secret）
   - `GOOGLE_SPREADSHEET_ID` = スプレッドシート ID
   - `GOOGLE_SHEET_NAME` = `回答`
   - `SURVEY_SECRET` = ランダムな長い文字列
6. Deploy

デプロイ後の URL（例: `https://your-app.onrender.com`）を回答者に共有。

## 5. レガシー保存（ローカル CSV / Excel）

`storage/response_store.py` 内のコメントアウト部分を有効化すると、Google Sheets 保存に加えてローカルにも保存できます。

- CSV: `storage/legacy_storage.py` → `save_response_to_csv`
- Excel: `storage/legacy_storage.py` → `save_response_to_excel`（openpyxl）

## 6. トラブルシューティング

| 症状 | 対処 |
|---|---|
| `SpreadsheetNotFound` | サービスアカウントにスプレッドシートの編集権限を付与 |
| `Invalid JWT` | JSON の内容が壊れていないか確認（Render では改行を含む1行 JSON） |
| 保存失敗の画面 | Render のログで `Google Sheets への保存に失敗` を確認 |
