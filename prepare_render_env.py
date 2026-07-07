"""Render 用の環境変数値を表示（秘密情報はローカルでのみ実行）"""

from __future__ import annotations

import json
import secrets
from pathlib import Path


def main() -> None:
    cred_path = Path(__file__).resolve().parent / "credentials" / "service-account.json"
    env_path = Path(__file__).resolve().parent / ".env"

    print("=" * 60)
    print("Render 環境変数セットアップ用")
    print("=" * 60)
    print()

    if cred_path.exists():
        json_text = cred_path.read_text(encoding="utf-8")
        json.loads(json_text)
        print("[GOOGLE_SERVICE_ACCOUNT_JSON]")
        print("Render の Environment → Secret として以下を貼り付け:")
        print("-" * 60)
        print(json_text.strip())
        print("-" * 60)
    else:
        print("NG: credentials/service-account.json が見つかりません")

    print()
    spreadsheet_id = ""
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("GOOGLE_SPREADSHEET_ID="):
                spreadsheet_id = line.split("=", 1)[1].strip()
                break

    print("[GOOGLE_SPREADSHEET_ID]")
    print(spreadsheet_id or "(.env に未設定)")
    print()
    print("[GOOGLE_SHEET_NAME]")
    print("回答")
    print()
    print("[SURVEY_SECRET]")
    print(secrets.token_urlsafe(32))
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
