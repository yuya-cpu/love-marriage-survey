"""認証JSONを Downloads から再配置し、PEM形式を修復する"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

SOURCE = Path.home() / "Downloads" / "love-marriage-survey-e0195a07e049.json"
TARGET = Path(__file__).resolve().parent / "credentials" / "service-account.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def normalize_info(info: dict) -> dict:
    private_key = info.get("private_key", "")
    if isinstance(private_key, str):
        info["private_key"] = private_key.replace("\\n", "\n")
    return info


def main() -> int:
    TARGET.parent.mkdir(parents=True, exist_ok=True)

    if not SOURCE.exists():
        print(f"NG: 元ファイルが見つかりません: {SOURCE}")
        return 1

    shutil.copy2(SOURCE, TARGET)

    with TARGET.open(encoding="utf-8-sig") as f:
        info = normalize_info(json.load(f))

    with TARGET.open("w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
        f.write("\n")

    try:
        from google.oauth2.service_account import Credentials

        Credentials.from_service_account_info(info, scopes=SCOPES)
    except Exception as exc:
        print(f"NG: 認証キーの検証に失敗しました → {exc}")
        print("Python 3.12 の利用を推奨します（3.14 では互換性問題が出ることがあります）")
        return 1

    print(f"OK: 認証ファイルを修復しました → {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
