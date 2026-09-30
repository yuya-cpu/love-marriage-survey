from __future__ import annotations

import csv
import io
import logging
import os
import socket
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

import secrets

from flask import Flask, redirect, render_template, request, send_file, session, url_for

from response_schema import RESPONSE_HEADERS
from storage import SaveResponseError, load_responses, save_response
from survey_data import (
    AFFILIATION_OPTIONS,
    AGE_OPTIONS,
    APP_INTENT,
    CHILD_COUNT,
    CHILD_FEELINGS,
    CHILD_IMAGE,
    FORM_DESCRIPTION,
    FORM_PRIVACY_NOTICE,
    FORM_TITLE,
    GENDER_OPTIONS,
    INCOME_OPTIONS,
    LIVING_OPTIONS,
    LOVER_CONDITIONS,
    MARRIAGE_CONDITIONS,
    LOVER_NOT_MARRY_REASONS,
    MARRIAGE_WISH,
    NOT_MARRY_INTENT_ANSWERS,
    PRIORITY_RANKS,
    SIBLINGS_OPTIONS,
    SCORE_HINT,
    SCORE_OPTIONS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SURVEY_SECRET", "love-marriage-survey-dev")

CSV_HEADERS = RESPONSE_HEADERS

OTHER_LABEL = "その他（回答を記述）"
_USED_SUBMIT_TOKENS: set[str] = set()
_USED_SUBMIT_TOKENS_MAX = 2000


def _issue_submit_token() -> str:
    token = secrets.token_urlsafe(24)
    session["submit_token"] = token
    return token


def _consume_submit_token(token: str) -> bool:
    token = (token or "").strip()
    if not token:
        return False
    if token in _USED_SUBMIT_TOKENS:
        return False
    expected = session.pop("submit_token", None)
    if not expected or not secrets.compare_digest(expected, token):
        return False
    _USED_SUBMIT_TOKENS.add(token)
    if len(_USED_SUBMIT_TOKENS) > _USED_SUBMIT_TOKENS_MAX:
        # 古い分を間引く（厳密なFIFOではないが連打対策には十分）
        for old in list(_USED_SUBMIT_TOKENS)[: len(_USED_SUBMIT_TOKENS) - _USED_SUBMIT_TOKENS_MAX // 2]:
            _USED_SUBMIT_TOKENS.discard(old)
    return True


def _survey_template_kwargs(**extra):
    base = dict(
        title=FORM_TITLE,
        description=FORM_DESCRIPTION,
        privacy_notice=FORM_PRIVACY_NOTICE,
        lover_conditions=LOVER_CONDITIONS,
        marriage_conditions=MARRIAGE_CONDITIONS,
        priority_ranks=PRIORITY_RANKS,
        score_options=SCORE_OPTIONS,
        score_hint=SCORE_HINT,
        child_image=CHILD_IMAGE,
        child_count=CHILD_COUNT,
        child_feelings=CHILD_FEELINGS,
        marriage_wish=MARRIAGE_WISH,
        lover_not_marry_reasons=LOVER_NOT_MARRY_REASONS,
        not_marry_answers=NOT_MARRY_INTENT_ANSWERS,
        app_intent=APP_INTENT,
        age_options=AGE_OPTIONS,
        gender_options=GENDER_OPTIONS,
        affiliation_options=AFFILIATION_OPTIONS,
        living_options=LIVING_OPTIONS,
        siblings_options=SIBLINGS_OPTIONS,
        income_options=INCOME_OPTIONS,
        submit_token=_issue_submit_token(),
    )
    base.update(extra)
    return base


def validate_priority(fields: list[str], options: list[str], prefix: str) -> list[str]:
    errors: list[str] = []
    values = [request.form.get(f"{prefix}_rank{r}", "").strip() for r in ("1", "2", "3")]
    if not all(values):
        errors.append(f"{prefix.upper()} の1位〜3位をすべて選択してください。")
        return errors
    if len(set(values)) != 3:
        errors.append(f"{prefix.upper()} で同じ項目を複数回選ぶことはできません。")
        return errors
    for v in values:
        if v not in options:
            errors.append(f"{prefix.upper()} に無効な選択肢が含まれています。")
    return errors


def validate_scores(prefix: str, label: str) -> list[str]:
    errors: list[str] = []
    for r in ("1", "2", "3"):
        score = request.form.get(f"{prefix}_score{r}", "").strip()
        if score not in SCORE_OPTIONS:
            errors.append(f"「{label}」で選んだ項目の重要度（{r}位）を10段階で評価してください。")
    return errors


@app.route("/")
def index():
    return render_template(
        "survey.html",
        **_survey_template_kwargs(errors=[], form={}, q4_2_reasons_selected=[], q3_3_selected=[]),
    )


@app.route("/submit", methods=["POST"])
def submit():
    errors: list[str] = []
    form = {k: v for k, v in request.form.items()}

    if not _consume_submit_token(form.get("submit_token", "")):
        return redirect(url_for("thanks", rid="already-submitted"))

    errors.extend(validate_priority(["q1_rank1", "q1_rank2", "q1_rank3"], LOVER_CONDITIONS, "q1"))
    errors.extend(validate_priority(["q2_rank1", "q2_rank2", "q2_rank3"], MARRIAGE_CONDITIONS, "q2"))
    errors.extend(validate_scores("q1", "問1"))
    errors.extend(validate_scores("q2", "問2"))

    required_radio = {
        "q3_1_child_image": "3-1",
        "q3_2_child_count": "3-2",
        "q4_has_lover": "4",
        "q5_1_marriage_wish": "5-1",
        "q6_app_intent": "6",
        "age": "年齢",
        "gender": "性別",
        "affiliation": "所属",
        "living": "居住形態",
        "siblings": "兄弟姉妹の人数",
    }
    for field, label in required_radio.items():
        if not form.get(field, "").strip():
            errors.append(f"「{label}」は必須です。")

    child_feelings = request.form.getlist("q3_3_child_feelings")
    if not child_feelings:
        errors.append("「3-3 子どもを持つことについて感じること」は1つ以上選択してください。")
    if OTHER_LABEL in child_feelings and not form.get("q3_3_other_text", "").strip():
        errors.append("「3-3」で『その他（回答を記述）』を選んだ場合、内容を記入してください。")

    has_lover = form.get("q4_has_lover", "")
    q4_1_intent = form.get("q4_1_marriage_intent", "")
    q4_2_reasons = request.form.getlist("q4_2_reasons")
    if has_lover == "いる":
        if not q4_1_intent:
            errors.append("「4-1 現在の恋人と結婚したいと思いますか？」は必須です。")
        elif q4_1_intent in NOT_MARRY_INTENT_ANSWERS and not q4_2_reasons:
            errors.append("「4-2 その理由を教えてください」は1つ以上選択してください。")

    # 問1 / 問2 で「その他（回答を記述）」をいずれかの順位で選んだ場合の自由記述
    q1_ranks = [form.get("q1_rank1", ""), form.get("q1_rank2", ""), form.get("q1_rank3", "")]
    q2_ranks = [form.get("q2_rank1", ""), form.get("q2_rank2", ""), form.get("q2_rank3", "")]
    if OTHER_LABEL in q1_ranks and not form.get("q1_other_text", "").strip():
        errors.append("「問1」で『その他（回答を記述）』を選んだ場合、内容を記入してください。")
    if OTHER_LABEL in q2_ranks and not form.get("q2_other_text", "").strip():
        errors.append("「問2」で『その他（回答を記述）』を選んだ場合、内容を記入してください。")

    if errors:
        return (
            render_template(
                "survey.html",
                **_survey_template_kwargs(
                    errors=errors,
                    form=form,
                    q4_2_reasons_selected=q4_2_reasons,
                    q3_3_selected=child_feelings,
                ),
            ),
            400,
        )

    row = {
        "q1_rank1": form.get("q1_rank1", ""),
        "q1_rank2": form.get("q1_rank2", ""),
        "q1_rank3": form.get("q1_rank3", ""),
        "q1_score1": form.get("q1_score1", ""),
        "q1_score2": form.get("q1_score2", ""),
        "q1_score3": form.get("q1_score3", ""),
        "q1_other_text": form.get("q1_other_text", "") if OTHER_LABEL in q1_ranks else "",
        "q2_rank1": form.get("q2_rank1", ""),
        "q2_rank2": form.get("q2_rank2", ""),
        "q2_rank3": form.get("q2_rank3", ""),
        "q2_score1": form.get("q2_score1", ""),
        "q2_score2": form.get("q2_score2", ""),
        "q2_score3": form.get("q2_score3", ""),
        "q2_other_text": form.get("q2_other_text", "") if OTHER_LABEL in q2_ranks else "",
        "q3_1_child_image": form.get("q3_1_child_image", ""),
        "q3_2_child_count": form.get("q3_2_child_count", ""),
        "q3_3_child_feelings": " / ".join(child_feelings),
        "q3_3_other_text": form.get("q3_3_other_text", "") if OTHER_LABEL in child_feelings else "",
        "q4_has_lover": has_lover,
        "q4_1_marriage_intent": q4_1_intent if has_lover == "いる" else "",
        "q4_2_reasons": " / ".join(q4_2_reasons) if has_lover == "いる" and q4_1_intent in NOT_MARRY_INTENT_ANSWERS else "",
        "q5_1_marriage_wish": form.get("q5_1_marriage_wish", ""),
        "q5_2_reason": form.get("q5_2_reason", ""),
        "q6_app_intent": form.get("q6_app_intent", ""),
        "q6_1_reason": form.get("q6_1_reason", ""),
        "age": form.get("age", ""),
        "gender": form.get("gender", ""),
        "affiliation": form.get("affiliation", ""),
        "living": form.get("living", ""),
        "siblings": form.get("siblings", ""),
        "income": form.get("income", ""),
    }

    try:
        response_id = save_response(row)
    except SaveResponseError:
        return (
            render_template(
                "survey.html",
                **_survey_template_kwargs(
                    errors=["回答の保存に失敗しました。時間をおいて再度お試しください。"],
                    form=form,
                    q4_2_reasons_selected=q4_2_reasons,
                ),
            ),
            500,
        )

    return redirect(url_for("thanks", rid=response_id))


@app.route("/thanks")
def thanks():
    return render_template("thanks.html", title=FORM_TITLE, response_id=request.args.get("rid", ""))


@app.route("/results")
def results():
    responses = load_responses()
    return render_template(
        "results.html",
        title=FORM_TITLE,
        responses=responses,
        headers=CSV_HEADERS,
        count=len(responses),
    )


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


@app.route("/info")
def info():
    port = request.environ.get("SERVER_PORT", os.environ.get("PORT", "5000"))
    local_ip = get_local_ip()
    return render_template(
        "info.html",
        title=FORM_TITLE,
        survey_url=url_for("index", _external=True),
        results_url=url_for("results", _external=True),
        lan_url=f"http://{local_ip}:{port}",
    )


@app.route("/download")
def download():
    responses = load_responses()
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_HEADERS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(responses)
    buffer.seek(0)
    return send_file(
        io.BytesIO(buffer.getvalue().encode("utf-8-sig")),
        as_attachment=True,
        download_name=f"survey_responses_{datetime.now().strftime('%Y%m%d')}.csv",
        mimetype="text/csv",
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    local_ip = get_local_ip()
    print("=" * 60)
    print("恋愛・結婚観アンケート — サーバー起動完了")
    print()
    print(f"  回答用リンク:     http://localhost:{port}")
    print(f"  スマホ等（LAN）:  http://{local_ip}:{port}")
    print(f"  リンク一覧:       http://localhost:{port}/info")
    print(f"  回答一覧・CSV:    http://localhost:{port}/results")
    print()
    print("  終了: Ctrl+C")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
