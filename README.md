# 恋愛・結婚観に関するアンケート

Flask + Google Sheets を使った Web アンケートです（ゼミ研究用）。

## ローカル起動

1. Python の依存関係をインストールする  
   `pip install -r requirements.txt`
2. Google Sheets 用の認証情報を配置する（`credentials/` など。詳細は環境に合わせる）
3. 起動する  
   - `python app.py`  
   - または `start_local.bat`

ブラウザで `http://127.0.0.1:5000` を開きます。

## Render へのデプロイ

起動コマンド:

```
gunicorn app:app
```

`render.yaml` がある場合はそれに従ってデプロイできます。秘密情報は Render の環境変数で設定してください。

## プライバシー

ご回答いただいた内容は統計的に処理し、ゼミ研究以外の目的では使用しません。個人が特定されることはありません。
