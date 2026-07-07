# Render デプロイ手順（完全版）

アンケートをインターネット上で誰でも使えるようにする手順です。
**所要時間: 約30〜45分**

---

## 全体の流れ

```
① Google Sheets 準備 → ② GitHub にアップロード → ③ Render でデプロイ → ④ URL を共有
```

---

## 事前準備① Google Sheets（回答の保存先）

### A. Google Cloud でサービスアカウントを作る

1. https://console.cloud.google.com/ を開く
2. 新しいプロジェクトを作成
3. **APIとサービス → ライブラリ** で検索して有効化:
   - `Google Sheets API`
   - `Google Drive API`
4. **APIとサービス → 認証情報 → 認証情報を作成 → サービスアカウント**
5. 名前を入力して作成 → 完了
6. 作成したサービスアカウントをクリック → **キー** タブ → **鍵を追加 → JSON**
7. ダウンロードした `.json` ファイルを大切に保管（後で Render に貼る）

### B. スプレッドシートを準備

1. https://sheets.google.com/ で新規スプレッドシート作成
2. 名前を `恋愛・結婚観アンケート回答` などに変更
3. 下のシートタブ名を `回答` に変更
4. **共有** ボタンをクリック
5. サービスアカウントのメール（JSON 内の `client_email`、例: `xxx@xxx.iam.gserviceaccount.com`）を入力
6. 権限を **編集者** にして招待
7. URL からスプレッドシート ID をコピー  
   `https://docs.google.com/spreadsheets/d/【この部分がID】/edit`

---

## 事前準備② GitHub にコードを上げる

### 方法A: このフォルダだけを新リポジトリにする（推奨）

1. https://github.com/new で新リポジトリ作成（例: `love-marriage-survey`）
2. ターミナルで実行:

```powershell
cd love-marriage-survey
git init
git add .
git commit -m "Initial commit: survey app for Render"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/love-marriage-survey.git
git push -u origin main
```

> **注意**: `credentials/` や `.env` は `.gitignore` に入っているのでアップロードされません（安全です）。

### 方法B: 既存リポジトリのサブフォルダにある場合

Render の **Root Directory** を `love-marriage-survey` に設定します。

---

## ③ Render でデプロイ

### 1. アカウント作成

1. https://render.com/ にアクセス
2. **Get Started** → GitHub アカウントでサインアップ

### 2. Web Service を作成

1. ダッシュボード → **New +** → **Web Service**
2. 先ほどの GitHub リポジトリを選択 → **Connect**
3. 以下のように設定:

| 項目 | 設定値 |
|---|---|
| **Name** | `love-marriage-survey`（任意） |
| **Region** | Singapore（日本に近い） |
| **Branch** | `main` |
| **Root Directory** | 空欄（リポジトリ直下が `love-marriage-survey` の場合）または `love-marriage-survey` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| **Instance Type** | Free（無料） |

### 3. 環境変数を設定（重要）

**Environment** セクションで **Add Environment Variable**:

| Key | Value | 備考 |
|---|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON ファイルの**全文**を貼り付け | Secret にチェック ✅ |
| `GOOGLE_SPREADSHEET_ID` | スプレッドシート ID | |
| `GOOGLE_SHEET_NAME` | `回答` | |
| `SURVEY_SECRET` | ランダムな長い文字列 | Secret にチェック ✅ |

#### JSON の貼り方（コツ）

1. ダウンロードした `.json` をメモ帳で開く
2. **全文**をコピー（`{` から `}` まで1行でも複数行でも可）
3. Render の `GOOGLE_SERVICE_ACCOUNT_JSON` の Value に貼り付け

`SURVEY_SECRET` の例（PowerShell で生成）:
```powershell
-join ((48..57)+(65..90)+(97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### 4. デプロイ開始

1. **Create Web Service** をクリック
2. ビルドが完了するまで 3〜5 分待つ
3. 画面上部に **URL** が表示される（例: `https://love-marriage-survey.onrender.com`）

---

## ④ アンケートを使う

| 用途 | URL |
|---|---|
| **回答用（みんなにシェア）** | `https://あなたのアプリ名.onrender.com` |
| **回答一覧** | `https://あなたのアプリ名.onrender.com/results` |
| **CSVダウンロード** | `https://あなたのアプリ名.onrender.com/download` |
| **回答データ（スプレッドシート）** | Google スプレッドシートを直接開く |

LINE やメールで回答用 URL を送れば、**どこからでも**回答できます。

---

## 無料プランの注意点

- **15分間アクセスがないとスリープ** → 最初のアクセスに30秒ほどかかることがある
- 月間の無料利用時間に上限あり（個人のアンケート用途なら通常十分）

スリープを避けたい場合は有料プラン（$7/月〜）へ変更。

---

## うまくいかないとき

### デプロイが失敗する

Render の **Logs** タブを確認。

| エラー | 対処 |
|---|---|
| `ModuleNotFoundError` | `requirements.txt` が正しいか確認 |
| `No module named 'response_schema'` | Root Directory が `love-marriage-survey` になっているか確認 |
| `Application failed to respond` | Start Command が `gunicorn app:app --bind 0.0.0.0:$PORT` か確認 |

### 回答送信で「保存に失敗しました」

1. Render Logs で `Google Sheets` のエラーを確認
2. サービスアカウントにスプレッドシートの**編集者**権限があるか
3. `GOOGLE_SPREADSHEET_ID` が正しいか
4. `GOOGLE_SERVICE_ACCOUNT_JSON` が壊れていないか（余分なスペースや引用符）

### 動作確認

デプロイ後、自分でアンケートに回答 → Google スプレッドシートに1行追加されていれば成功。

---

## チェックリスト

- [ ] Google Sheets API / Drive API を有効化
- [ ] サービスアカウント JSON を取得
- [ ] スプレッドシートにサービスアカウントを編集者として共有
- [ ] GitHub にコードをプッシュ
- [ ] Render で Web Service 作成
- [ ] 環境変数 4 つを設定
- [ ] デプロイ成功
- [ ] テスト回答 → スプレッドシートに反映
