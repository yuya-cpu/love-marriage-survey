"""
Google Forms API を使ってアンケートを自動作成するスクリプト。

事前準備:
  1. Google Cloud Console でプロジェクトを作成
  2. Google Forms API と Google Drive API を有効化
  3. OAuth 2.0 クライアント ID（デスクトップアプリ）を作成し credentials.json をこのフォルダに配置
  4. pip install -r requirements.txt
  5. python create_survey.py
"""

from __future__ import annotations

import os
import pickle
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from survey_data import (
    AFFILIATION_OPTIONS,
    AGE_OPTIONS,
    APP_INTENT,
    CHILD_COUNT,
    CHILD_FEELINGS,
    CHILD_IMAGE,
    FORM_DESCRIPTION,
    FORM_TITLE,
    GENDER_OPTIONS,
    INCOME_OPTIONS,
    LIVING_OPTIONS,
    LOVER_CONDITIONS,
    MARRIAGE_CONDITIONS,
    MARRIAGE_INTENT,
    MARRIAGE_WISH,
    PRIORITY_RANKS,
    SIBLINGS_OPTIONS,
)

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive.file",
]
TOKEN_FILE = "token.pickle"
CREDENTIALS_FILE = "credentials.json"


def get_credentials() -> Credentials:
    creds: Credentials | None = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"{CREDENTIALS_FILE} が見つかりません。"
                    "Google Cloud Console から OAuth クライアント ID をダウンロードしてください。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return creds


def opts(values: list[str]) -> list[dict[str, str]]:
    return [{"value": v} for v in values]


def dropdown(title: str, choices: list[str], required: bool = True, description: str = "") -> dict:
    question: dict[str, Any] = {
        "required": required,
        "choiceQuestion": {"type": "DROP_DOWN", "options": opts(choices)},
    }
    item: dict[str, Any] = {
        "title": title,
        "questionItem": {"question": question},
    }
    if description:
        item["description"] = description
    return item


def radio(title: str, choices: list[str], required: bool = True, description: str = "") -> dict:
    question: dict[str, Any] = {
        "required": required,
        "choiceQuestion": {"type": "RADIO", "options": opts(choices)},
    }
    item: dict[str, Any] = {
        "title": title,
        "questionItem": {"question": question},
    }
    if description:
        item["description"] = description
    return item


def checkbox(title: str, choices: list[str], required: bool = True, description: str = "") -> dict:
    question: dict[str, Any] = {
        "required": required,
        "choiceQuestion": {"type": "CHECKBOX", "options": opts(choices)},
    }
    item: dict[str, Any] = {
        "title": title,
        "questionItem": {"question": question},
    }
    if description:
        item["description"] = description
    return item


def text_question(title: str, required: bool = False, paragraph: bool = True) -> dict:
    return {
        "title": title,
        "questionItem": {
            "question": {
                "required": required,
                "textQuestion": {"paragraph": paragraph},
            }
        },
    }


def page_break(title: str = "", description: str = "") -> dict:
    item: dict[str, Any] = {"pageBreakItem": {}}
    if title:
        item["title"] = title
    if description:
        item["description"] = description
    return item


def create_item_request(item: dict, index: int) -> dict:
    return {"createItem": {"item": item, "location": {"index": index}}}


def build_all_items() -> list[dict]:
    """フォームに追加する全質問アイテムを順番に返す"""
    items: list[dict] = []

    # --- 問1: 恋人に求める条件（優先順位付きドロップダウン） ---
    items.append(
        page_break(
            "1. 現在、恋人に求める条件は何ですか？",
            "重要だと思うものを優先順位順に3つ選んでください（同じ項目は選べません）。",
        )
    )
    for rank_label, rank_desc in PRIORITY_RANKS:
        items.append(
            dropdown(
                f"1-{rank_label}: 恋人に求める条件（{rank_desc}）",
                LOVER_CONDITIONS,
            )
        )

    # --- 問2: 結婚相手に求める条件（優先順位付きドロップダウン） ---
    items.append(
        page_break(
            "2. もし今結婚するとしたら、相手に求める条件は何ですか？",
            "重要だと思うものを優先順位順に3つ選んでください（同じ項目は選べません）。",
        )
    )
    for rank_label, rank_desc in PRIORITY_RANKS:
        items.append(
            dropdown(
                f"2-{rank_label}: 結婚相手に求める条件（{rank_desc}）",
                MARRIAGE_CONDITIONS,
            )
        )

    # --- 問3: 子ども ---
    items.append(page_break("3. 子どもについて"))
    items.append(radio("3-1. 子どもを持つことにどのようなイメージがありますか？", CHILD_IMAGE))
    items.append(radio("3-2. 子どもは何人ほしいですか？", CHILD_COUNT))
    items.append(
        checkbox(
            "3-3. 子どもを持つことについて感じること（複数選択可）",
            CHILD_FEELINGS,
        )
    )

    # --- 問4: 恋人の有無（セクション分岐用） ---
    items.append(page_break("4. 恋人について"))
    items.append(radio("4. 現在、恋人はいますか？", ["いる", "いない"]))

    # --- 4-1, 4-2: 恋人がいる人のみ ---
    items.append(page_break("4-1〜4-2. 恋人がいる方へ"))
    items.append(radio("4-1. 現在の恋人と結婚したいと思いますか？", MARRIAGE_INTENT))
    items.append(text_question("4-2. その理由を教えてください"))

    # --- 問5: 結婚願望 ---
    items.append(page_break("5. 結婚願望"))
    items.append(radio("5-1. 将来的に結婚したいと思いますか？", MARRIAGE_WISH))
    items.append(text_question("5-2. その理由を教えてください"))

    # --- 問6: マッチングアプリ ---
    items.append(page_break("6. マッチングアプリ"))
    items.append(
        radio(
            "6. 大学生・大学院生向けの「結婚を見据えたマッチングアプリ」があった場合、利用したいと思いますか？",
            APP_INTENT,
        )
    )
    items.append(text_question("6-1. その理由を教えてください"))

    # --- 問7: 属性 ---
    items.append(page_break("7. 属性質問（回答者の背景）"))
    items.append(dropdown("年齢", AGE_OPTIONS))
    items.append(radio("性別", GENDER_OPTIONS))
    items.append(radio("所属", AFFILIATION_OPTIONS))
    items.append(radio("居住形態", LIVING_OPTIONS))
    items.append(radio("兄弟姉妹の人数", SIBLINGS_OPTIONS))
    items.append(radio("世帯収入（概算）", INCOME_OPTIONS, required=False))

    return items


def setup_branching(service, form_id: str) -> None:
    """問4の「いる/いない」でセクション分岐を設定"""
    form = service.forms().get(formId=form_id).execute()
    items = form.get("items", [])

    q4_item_id = None
    section_lover_id = None
    section_marriage_id = None

    for item in items:
        title = item.get("title", "")
        item_id = item["itemId"]
        if title == "4. 現在、恋人はいますか？":
            q4_item_id = item_id
        elif title == "4-1〜4-2. 恋人がいる方へ":
            section_lover_id = item_id
        elif title == "5. 結婚願望":
            section_marriage_id = item_id

    if not all([q4_item_id, section_lover_id, section_marriage_id]):
        print("警告: セクション分岐の設定に必要な質問 ID が見つかりませんでした。手動で設定してください。")
        return

    service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": [
                {
                    "updateItem": {
                        "item": {
                            "itemId": q4_item_id,
                            "title": "4. 現在、恋人はいますか？",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": [
                                            {
                                                "value": "いる",
                                                "goToSectionId": section_lover_id,
                                            },
                                            {
                                                "value": "いない",
                                                "goToSectionId": section_marriage_id,
                                            },
                                        ],
                                    },
                                }
                            },
                        },
                        "updateMask": "questionItem.question",
                    }
                }
            ]
        },
    ).execute()
    print("セクション分岐（問4）を設定しました。")


def main() -> None:
    creds = get_credentials()
    service = build("forms", "v1", credentials=creds)

    form = (
        service.forms()
        .create(
            body={
                "info": {
                    "title": FORM_TITLE,
                    "documentTitle": FORM_TITLE,
                }
            }
        )
        .execute()
    )
    form_id = form["formId"]
    print(f"フォームを作成しました: {form_id}")

    service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": [
                {
                    "updateFormInfo": {
                        "info": {"description": FORM_DESCRIPTION},
                        "updateMask": "description",
                    }
                }
            ]
        },
    ).execute()

    all_items = build_all_items()
    batch_size = 20
    for start in range(0, len(all_items), batch_size):
        chunk = all_items[start : start + batch_size]
        requests = [
            create_item_request(item, start + i) for i, item in enumerate(chunk)
        ]
        service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()

    setup_branching(service, form_id)

    responder_url = form.get("responderUri", f"https://docs.google.com/forms/d/{form_id}/viewform")
    edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
    print()
    print("=" * 60)
    print("アンケート作成完了！")
    print(f"編集URL: {edit_url}")
    print(f"回答URL: {responder_url}")
    print("=" * 60)


if __name__ == "__main__":
    main()
