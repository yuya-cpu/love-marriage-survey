"""回答の保存・読み込み（Google Sheets を本番、ローカルはレガシー）"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from response_schema import RESPONSE_HEADERS

logger = logging.getLogger(__name__)


class SaveResponseError(Exception):
    """回答の保存に失敗した場合"""


def build_record(row: dict[str, str]) -> tuple[str, list[str]]:
    response_id = str(uuid.uuid4())[:8]
    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = [response_id, submitted_at] + [row.get(h, "") for h in RESPONSE_HEADERS[2:]]
    return response_id, record


def save_response(row: dict[str, str]) -> str:
    response_id, record = build_record(row)

    try:
        from storage.google_sheets_storage import get_storage

        get_storage().append_row(record)
        logger.info("Google Sheets へ回答を保存しました: response_id=%s", response_id)
    except Exception:
        logger.exception("Google Sheets への保存に失敗しました: response_id=%s", response_id)
        raise SaveResponseError("回答の保存に失敗しました") from None

    # レガシー保存（必要時のみコメントを外す）
    # try:
    #     from storage.legacy_storage import save_response_to_csv, save_response_to_excel
    #     save_response_to_csv(record)
    #     save_response_to_excel(record)
    # except Exception:
    #     logger.warning("レガシーローカル保存に失敗（本番保存は成功）", exc_info=True)

    return response_id


def load_responses() -> list[dict[str, str]]:
    try:
        from storage.google_sheets_storage import get_storage

        return get_storage().get_all_records()
    except Exception:
        logger.warning("Google Sheets からの読み込みに失敗。CSV にフォールバックします。", exc_info=True)
        from storage.legacy_storage import load_responses_from_csv

        return load_responses_from_csv()
