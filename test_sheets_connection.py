"""Google Sheets 接続テスト。python test_sheets_connection.py で実行"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass


def main() -> int:
    if sys.version_info >= (3, 14):
        print("注意: Python 3.14 では認証ライブラリの互換性問題が出ることがあります。")
        print("      うまくいかない場合は Python 3.12 をご利用ください。")
        print()

    cred_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()
    if cred_file and not Path(cred_file).is_absolute():
        cred_file = str(Path(__file__).resolve().parent / cred_file)
    spreadsheet_id = os.environ.get("GOOGLE_SPREADSHEET_ID", "").strip()

    print("=" * 50)
    print("Google Sheets 接続テスト")
    print("=" * 50)

    if not cred_file or not os.path.exists(cred_file):
        print("NG: 認証ファイルが見つかりません")
        print(f"   GOOGLE_SERVICE_ACCOUNT_FILE={cred_file or '(未設定)'}")
        return 1
    print(f"OK: 認証ファイル → {cred_file}")

    if not spreadsheet_id:
        print("NG: GOOGLE_SPREADSHEET_ID が未設定です")
        print()
        print("次の手順:")
        print("  1. Google スプレッドシートを作成")
        print("  2. シート名を「回答」に変更")
        print("  3. 共有 → survey-writer@love-marriage-survey.iam.gserviceaccount.com を編集者で招待")
        print("  4. .env の GOOGLE_SPREADSHEET_ID に URL の ID を貼る")
        return 1
    print(f"OK: スプレッドシート ID → {spreadsheet_id}")

    try:
        from storage.google_sheets_storage import get_storage

        storage = get_storage()
        storage.ensure_headers()
        print("OK: Google Sheets に接続できました")
        print(f"   シート名: {os.environ.get('GOOGLE_SHEET_NAME', '回答')}")
        print()
        print("次: start_local.bat を実行して http://localhost:5000 を開いてください")
        return 0
    except Exception as exc:
        print(f"NG: 接続失敗 → {exc}")
        print()
        print("確認事項:")
        print("  - Google Sheets API / Drive API が有効か")
        print("  - サービスアカウントにスプレッドシートの編集権限があるか")
        return 1


if __name__ == "__main__":
    sys.exit(main())
