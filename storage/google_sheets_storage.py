"""Google Sheets への回答保存"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from response_schema import RESPONSE_HEADERS

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _resolve_credentials_path(json_file: str) -> Path:
    path = Path(json_file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / path
    return path


def _normalize_service_account_info(info: dict) -> dict:
    private_key = info.get("private_key", "")
    if isinstance(private_key, str) and "\\n" in private_key:
        info["private_key"] = private_key.replace("\\n", "\n")
    return info


def _credentials_from_info(info: dict) -> Credentials:
    return Credentials.from_service_account_info(
        _normalize_service_account_info(info),
        scopes=SCOPES,
    )


def _credentials_from_file(path: Path) -> Credentials:
    with path.open(encoding="utf-8-sig") as f:
        info = json.load(f)
    return _credentials_from_info(info)


class GoogleSheetsStorage:
    def __init__(self) -> None:
        self._spreadsheet_id = os.environ.get("GOOGLE_SPREADSHEET_ID", "").strip()
        self._spreadsheet_name = os.environ.get("GOOGLE_SPREADSHEET_NAME", "").strip()
        self._sheet_name = os.environ.get("GOOGLE_SHEET_NAME", "回答").strip() or "回答"
        self._client = self._build_client()
        self._worksheet = self._open_worksheet()

    def _build_client(self) -> gspread.Client:
        json_content = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
        json_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()

        if json_content:
            info = json.loads(json_content)
            creds = _credentials_from_info(info)
        elif json_file:
            creds = _credentials_from_file(_resolve_credentials_path(json_file))
        else:
            raise ValueError(
                "GOOGLE_SERVICE_ACCOUNT_JSON または GOOGLE_SERVICE_ACCOUNT_FILE が未設定です。"
            )

        return gspread.authorize(creds)

    def _open_worksheet(self) -> gspread.Worksheet:
        if self._spreadsheet_id:
            spreadsheet = self._client.open_by_key(self._spreadsheet_id)
        elif self._spreadsheet_name:
            spreadsheet = self._client.open(self._spreadsheet_name)
        else:
            raise ValueError(
                "GOOGLE_SPREADSHEET_ID または GOOGLE_SPREADSHEET_NAME が未設定です。"
            )

        try:
            return spreadsheet.worksheet(self._sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=self._sheet_name,
                rows=1000,
                cols=len(RESPONSE_HEADERS),
            )
            worksheet.append_row(RESPONSE_HEADERS)
            return worksheet

    def ensure_headers(self) -> None:
        first_row = self._worksheet.row_values(1)
        if not first_row:
            self._worksheet.insert_row(RESPONSE_HEADERS, index=1)
        elif first_row != RESPONSE_HEADERS:
            logger.warning("スプレッドシートの1行目が想定ヘッダーと一致しません")

    def append_row(self, record: list[str]) -> None:
        self.ensure_headers()
        self._worksheet.append_row(record, value_input_option="USER_ENTERED")

    def get_all_records(self) -> list[dict[str, str]]:
        self.ensure_headers()
        return self._worksheet.get_all_records()


@lru_cache(maxsize=1)
def get_storage() -> GoogleSheetsStorage:
    return GoogleSheetsStorage()
