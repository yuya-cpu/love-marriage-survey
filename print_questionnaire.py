"""
Googleフォームに手動でコピー＆ペーストできる形式でアンケート全文を出力するスクリプト。
API認証なしで実行可能: python print_questionnaire.py
"""

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


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"  * {item}" for item in items)


def main() -> None:
    lines = [
        f"タイトル: {FORM_TITLE}",
        f"説明: {FORM_DESCRIPTION}",
        "",
        "=" * 60,
        "",
        "【1. 現在、恋人に求める条件は何ですか？】",
        "※ 重要だと思うものを優先順位順に3つ選ぶ（プルダウン × 3）",
        "※ 同じ項目は選べないよう説明文に記載",
        "",
    ]
    for rank_label, rank_desc in PRIORITY_RANKS:
        lines += [
            f"  [プルダウン] 1-{rank_label}: 恋人に求める条件（{rank_desc}）",
            bullet_list(LOVER_CONDITIONS),
            "",
        ]

    lines += [
        "【2. もし今結婚するとしたら、相手に求める条件は何ですか？】",
        "※ 重要だと思うものを優先順位順に3つ選ぶ（プルダウン × 3）",
        "",
    ]
    for rank_label, rank_desc in PRIORITY_RANKS:
        lines += [
            f"  [プルダウン] 2-{rank_label}: 結婚相手に求める条件（{rank_desc}）",
            bullet_list(MARRIAGE_CONDITIONS),
            "",
        ]

    lines += [
        "【3. 子どもについての考えを教えてください】",
        "",
        "  [ラジオ] 3-1. 子どもを持つことにどのようなイメージがありますか？",
        bullet_list(CHILD_IMAGE),
        "",
        "  [ラジオ] 3-2. 子どもは何人ほしいですか？",
        bullet_list(CHILD_COUNT),
        "",
        "  [チェックボックス] 3-3. 子どもを持つことについて感じること（複数選択可）",
        bullet_list(CHILD_FEELINGS),
        "",
        "【4. 現在、恋人はいますか？】 [ラジオ]",
        "  * いる",
        "  * いない",
        "  → 「いる」→ 4-1へ / 「いない」→ 5へ（セクション分岐を設定）",
        "",
        "  --- セクション: 恋人がいる方のみ ---",
        "  [ラジオ] 4-1. 現在の恋人と結婚したいと思いますか？",
        bullet_list(MARRIAGE_INTENT),
        "",
        "  [記述式] 4-2. その理由を教えてください",
        "",
        "【5. あなた自身の結婚願望について教えてください】",
        "",
        "  [ラジオ] 5-1. 将来的に結婚したいと思いますか？",
        bullet_list(MARRIAGE_WISH),
        "",
        "  [記述式] 5-2. その理由を教えてください",
        "",
        "【6. 大学生・大学院生向けの「結婚を見据えたマッチングアプリ」があった場合、利用したいと思いますか？】",
        "  [ラジオ]",
        bullet_list(APP_INTENT),
        "",
        "  [記述式] 6-1. その理由を教えてください",
        "",
        "【7. 属性質問（回答者の背景）】",
        "",
        "  [プルダウン] 年齢（必須）",
        bullet_list(AGE_OPTIONS),
        "",
        "  [ラジオ] 性別（必須）",
        bullet_list(GENDER_OPTIONS),
        "",
        "  [ラジオ] 所属（必須）",
        bullet_list(AFFILIATION_OPTIONS),
        "",
        "  [ラジオ] 居住形態（必須）",
        bullet_list(LIVING_OPTIONS),
        "",
        "  [ラジオ] 兄弟姉妹の人数（必須）",
        bullet_list(SIBLINGS_OPTIONS),
        "",
        "  [ラジオ] 世帯収入（概算）（任意推奨）",
        bullet_list(INCOME_OPTIONS),
        "",
        "=" * 60,
        "【作成時のテクニック】",
        "1. 問4の右下 ⋮ →「回答に応じてセクションに移動」",
        "   「いる」→ 4-1セクション / 「いない」→ 5セクション",
        "2. 属性質問は基本的にすべて必須（世帯収入のみ任意可）",
        "3. 問1・問2はプルダウン3問で優先順位がスプレッドシートで分析しやすい",
    ]

    output = "\n".join(lines)
    print(output)

    out_path = "questionnaire_manual.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"\n→ {out_path} にも保存しました。")


if __name__ == "__main__":
    main()
