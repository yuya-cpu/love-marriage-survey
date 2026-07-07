# Render デプロイ（今すぐやる手順）

ローカルは動いているので、あとは **GitHub → Render** です。

---

## ステップ1: GitHub にアップロード（5分）

PowerShell を開いて:

```powershell
cd "C:\Users\koyu2\OneDrive\デスクトップ\love-marriage-survey"

git init
git branch -M main
git add .
git status
```

**確認:** `credentials/` と `.env` が **含まれていない** こと（含まれていたら止める）

```powershell
git commit -m "Deploy love marriage survey"
```

### GitHub CLI がある場合

```powershell
gh auth login
gh repo create love-marriage-survey --public --source=. --remote=origin --push
```

### ブラウザでリポジトリを作る場合

1. https://github.com/new で `love-marriage-survey` を作成
2. 次を実行:

```powershell
git remote add origin https://github.com/あなたのユーザー名/love-marriage-survey.git
git push -u origin main
```

---

## ステップ2: Render 用の秘密情報をコピー（2分）

```powershell
cd "C:\Users\koyu2\OneDrive\デスクトップ\love-marriage-survey"
python prepare_render_env.py
```

表示された内容をメモ帳に保存（あとで Render に貼る）:

| 変数名 | 値 |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | 表示された JSON 全文 |
| `GOOGLE_SPREADSHEET_ID` | `1_x2mV7q0OoAiE01G3T4UIEXbNWW3cSoNhvy8fWAr48E` |
| `GOOGLE_SHEET_NAME` | `回答` |
| `SURVEY_SECRET` | 表示されたランダム文字列 |

---

## ステップ3: Render で Web Service 作成（5分）

1. https://dashboard.render.com/ にログイン（GitHub 連携）
2. **New +** → **Web Service**
3. さきほどの `love-marriage-survey` リポジトリを選択 → **Connect**
4. 設定:

| 項目 | 値 |
|---|---|
| Name | `love-marriage-survey` |
| Region | Singapore |
| Branch | `main` |
| Root Directory | （空欄） |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| Instance Type | **Free** |

5. **Environment Variables** を追加:

| Key | Value | Secret |
|---|---|---|
| `PYTHON_VERSION` | `3.12.4` | |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON 全文 | ✅ |
| `GOOGLE_SPREADSHEET_ID` | `1_x2mV7q0OoAiE01G3T4UIEXbNWW3cSoNhvy8fWAr48E` | |
| `GOOGLE_SHEET_NAME` | `回答` | |
| `SURVEY_SECRET` | ランダム文字列 | ✅ |

6. **Create Web Service** → デプロイ完了まで待つ（3〜5分）

---

## ステップ4: 動作確認

デプロイ後の URL（例）:

```
https://love-marriage-survey.onrender.com
```

1. 上記 URL を開く
2. テスト回答を1件送信
3. Google スプレッドシートに行が追加されるか確認

---

## みんなに配るリンク

```
https://あなたのアプリ名.onrender.com
```

LINE やメールでこの URL を送れば、**どこからでも**回答できます。

---

## うまくいかないとき

| 症状 | 対処 |
|---|---|
| Build failed | Render の Logs を確認 |
| 保存失敗 | `GOOGLE_SERVICE_ACCOUNT_JSON` が全文か確認 |
| 初回アクセスが遅い | 無料プランはスリープする（正常） |
