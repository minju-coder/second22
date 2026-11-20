# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction

import streamlit as st


st.set_page_config(
    page_title="소수 나눗셈 탐험대",
    layout="wide",
)

st.markdown(
    """
    <style>
    html, body, [class*="st-"] {
        font-family: "Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo",
                     "Nanum Gothic", sans-serif;
    }
    .stApp { background: #f5f9ff; }
    .block-container { max-width: 1080px; padding-top: 2rem; }
    .hero {
        padding: 1.7rem 2rem; border-radius: 22px;
        background: linear-gradient(120deg, #dff4ff, #f1eaff);
        border: 1px solid #d6e8ff; margin-bottom: 1rem;
    }
    .hero-label {
        display: inline-block; margin-bottom: .45rem; padding: .2rem .65rem;
        color: #315887; background: #fff; border-radius: 999px;
        font-size: .85rem; font-weight: 700;
    }
    .hero h1 { color: #23395d; margin: 0 0 .45rem; }
    .hero p { color: #405675; margin: 0; font-size: 1.05rem; }
    .visual-label { color: #405675; font-weight: 700; margin: .6rem 0 .3rem; }
    .ribbon { display: flex; gap: 5px; margin: .5rem 0 1rem; }
    .ribbon-part {
        flex: 1; min-width: 0; padding: .8rem .2rem; text-align: center;
        color: #23395d; background: #ffe08a; border: 2px solid #fff;
        border-radius: 9px; font-size: .86rem; font-weight: 700;
    }
    .juice-track {
        height: 25px; background: #e7edf5; border-radius: 14px;
        overflow: hidden; border: 1px solid #d8e1ed;
    }
    .juice-fill {
        height: 100%; background: linear-gradient(90deg, #ffbd59, #ff8c69);
        border-radius: 14px;
    }
    .cups { display: flex; flex-wrap: wrap; gap: 8px; margin: .8rem 0; }
    .cup {
        border: 2px solid #78a9e8; border-top: 0; border-radius: 4px 4px 12px 12px;
        width: 58px; height: 48px; display: flex; align-items: end;
        justify-content: center; padding-bottom: 5px; color: #234;
        background: linear-gradient(to top, #ffbd59 0 55%, #fff 55% 100%);
        font-size: .76rem; font-weight: 700;
    }
    .principle {
        padding: 1rem 1.2rem; background: #e9f8ed; border-left: 5px solid #58ae72;
        border-radius: 10px; color: #294d35;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <span class="hero-label">수학 탐험 학습</span>
      <h1>소수 나눗셈 탐험대</h1>
      <p>생활 속 장면을 살펴보고, 그림으로 나누어 보고, 계산 원리를 직접 찾아보세요!</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def parse_decimal(raw_value: str, label: str) -> Decimal:
    """Convert student-entered text to a finite decimal, with a clear error."""
    value = raw_value.strip()
    if not value:
        raise ValueError(f"{label}을(를) 입력해 주세요.")
    if len(value) > 40:
        raise ValueError(f"{label}은(는) 40자 이내로 입력해 주세요.")
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"{label}을(를) 숫자로 입력해 주세요.") from error
    if not number.is_finite():
        raise ValueError(f"{label}은(는) 유한한 숫자로 입력해 주세요.")
    return number


def exact_quotient(dividend: Decimal, divisor: Decimal) -> Fraction:
    if divisor == 0:
        raise ValueError("0으로 나눌 수 없어요. 나누는 수를 확인해 주세요.")
    return Fraction(dividend) / Fraction(divisor)


def format_fraction(value: Fraction) -> str:
    """Show terminating decimal answers exactly, and repeating answers as fractions."""
    denominator = value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        twos += 1
        denominator //= 2
    while denominator % 5 == 0:
        fives += 1
        denominator //= 5
    if denominator == 1:
        precision = max(twos, fives)
        with localcontext() as context:
            context.prec = max(50, len(str(abs(value.numerator))) + precision + 2)
            result = Decimal(value.numerator) / Decimal(value.denominator)
        return decimal_text(result)
    with localcontext() as context:
        context.prec = 12
        approximation = Decimal(value.numerator) / Decimal(value.denominator)
    return f"{value.numerator}/{value.denominator} (약 {decimal_text(approximation)})"


def decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def check_answer(raw_answer: str, answer: Fraction, label: str) -> tuple[bool | None, str]:
    try:
        entered = parse_decimal(raw_answer, label)
    except ValueError as error:
        return None, str(error)
    if Fraction(entered) == answer:
        return True, "정답이에요! 멋진 탐험가네요."
    return False, "조금 달라요. 그림과 나눗셈식을 다시 살펴보고 한 번 더 생각해 보세요."


def show_interactive_activity(
    *,
    key: str,
    title: str,
    situation: str,
    dividend_label: str,
    divisor_label: str,
    initial_dividend: str,
    initial_divisor: str,
    answer_label: str,
    visual_type: str,
) -> None:
    with st.container(border=True):
        st.subheader(title)
        st.write(situation)
        first, second = st.columns(2)
        with first:
            dividend_raw = st.text_input(
                dividend_label, value=initial_dividend, key=f"{key}_dividend"
            )
        with second:
            divisor_raw = st.text_input(
                divisor_label, value=initial_divisor, key=f"{key}_divisor"
            )

        try:
            dividend = parse_decimal(dividend_raw, dividend_label)
            divisor = parse_decimal(divisor_raw, divisor_label)
            if divisor == 0:
                raise ValueError("0으로 나눌 수 없어요. 나누는 수를 확인해 주세요.")
            if dividend < 0 or divisor < 0:
                raise ValueError("양수로 입력해 주세요.")
            answer = exact_quotient(dividend, divisor)

            if visual_type == "ribbon":
                if divisor != divisor.to_integral_value():
                    raise ValueError("리본을 나눌 사람 수는 자연수로 입력해 주세요.")
                part_count = int(divisor)
                st.markdown(
                    f'<div class="visual-label">리본 {decimal_text(dividend)}m를 '
                    f'{part_count}명이 똑같이 나누어요.</div>',
                    unsafe_allow_html=True,
                )
                if part_count <= 24:
                    parts = "".join(
                        f'<div class="ribbon-part">{format_fraction(answer)}m</div>'
                        for _ in range(part_count)
                    )
                    st.markdown(
                        f'<div class="ribbon">{parts}</div>', unsafe_allow_html=True
                    )
                else:
                    st.info(
                        f"리본을 {part_count}조각으로 나눕니다. "
                        f"한 조각은 {format_fraction(answer)}m예요."
                    )
            else:
                common_scale = max(dividend, divisor)
                total_width = 100.0 if common_scale == 0 else float(dividend / common_scale * 100)
                cup_width = 0.0 if common_scale == 0 else float(divisor / common_scale * 100)
                st.markdown(
                    f'<div class="visual-label">전체 주스 {decimal_text(dividend)}L</div>'
                    f'<div class="juice-track"><div class="juice-fill" '
                    f'style="width:{total_width:.2f}%"></div></div>'
                    f'<div class="visual-label">컵 하나에 {decimal_text(divisor)}L</div>'
                    f'<div class="juice-track"><div class="juice-fill" '
                    f'style="width:{cup_width:.2f}%"></div></div>',
                    unsafe_allow_html=True,
                )
                if answer.denominator == 1 and 0 < answer.numerator <= 24:
                    cups = "".join(
                        f'<div class="cup"><span>{decimal_text(divisor)}L</span></div>'
                        for _ in range(answer.numerator)
                    )
                    st.markdown(f'<div class="cups">{cups}</div>', unsafe_allow_html=True)
                    st.caption(f"컵 {answer.numerator}개에 똑같이 담았어요.")
                else:
                    st.caption(
                        f"나눗셈식: {decimal_text(dividend)} ÷ {decimal_text(divisor)}"
                    )

            prediction = st.text_input(
                answer_label, placeholder="답을 예상해서 숫자로 써 보세요",
                key=f"{key}_answer",
            )
            if st.button("정답 확인하기", key=f"{key}_check"):
                correct, message = check_answer(prediction, answer, "예상한 답")
                st.session_state[f"{key}_feedback"] = (
                    correct,
                    message,
                    prediction,
                )
            feedback = st.session_state.get(f"{key}_feedback")
            if feedback and feedback[2] == prediction:
                correct, message, _ = feedback
                if correct is None:
                    st.warning(message)
                else:
                    if correct:
                        st.success(message)
                    else:
                        st.info(message)
                    st.info(
                        f"정답: {format_fraction(answer)} | 풀이: "
                        f"{decimal_text(dividend)} ÷ {decimal_text(divisor)} "
                        f"= {format_fraction(answer)}"
                    )
        except (ValueError, OverflowError) as error:
            st.warning(str(error))


show_interactive_activity(
    key="ribbon",
    title="활동 1. 소수 ÷ 자연수",
    situation="리본 3.6m를 4명이 똑같이 나누어 가지려고 해요. 한 사람은 몇 m씩 가질까요?",
    dividend_label="나누어지는 수 (리본 전체, m)",
    divisor_label="나누는 수 (사람 수)",
    initial_dividend="3.6",
    initial_divisor="4",
    answer_label="한 사람이 받을 리본의 길이 (m)",
    visual_type="ribbon",
)

show_interactive_activity(
    key="juice",
    title="활동 2. 소수 ÷ 소수",
    situation="주스 3.6L를 한 컵에 0.6L씩 담으려고 해요. 몇 컵에 담을 수 있을까요?",
    dividend_label="전체 주스의 양 (L)",
    divisor_label="컵 하나에 담는 양 (L)",
    initial_dividend="3.6",
    initial_divisor="0.6",
    answer_label="주스를 담을 수 있는 컵 수",
    visual_type="juice",
)

with st.container(border=True):
    st.subheader("계산 원리 탐험: 3.6 ÷ 0.6")
    st.write("나누는 수를 자연수로 바꾸려면, 나누어지는 수도 똑같이 바꾸면 어떻게 될까요?")
    if "transform_multiplier" not in st.session_state:
        st.session_state.transform_multiplier = 10
    ten_col, hundred_col = st.columns(2)
    with ten_col:
        if st.button("두 수에 10을 곱하기", key="multiply_10"):
            st.session_state.transform_multiplier = 10
    with hundred_col:
        if st.button("두 수에 100을 곱하기", key="multiply_100"):
            st.session_state.transform_multiplier = 100

    multiplier = st.session_state.transform_multiplier
    converted_dividend = Decimal("3.6") * multiplier
    converted_divisor = Decimal("0.6") * multiplier
    original_answer = exact_quotient(Decimal("3.6"), Decimal("0.6"))
    converted_answer = exact_quotient(converted_dividend, converted_divisor)
    st.markdown(f"1. 처음 식: **3.6 ÷ 0.6 = {format_fraction(original_answer)}**")
    st.markdown(
        f"2. 두 수에 {multiplier}을(를) 곱해요: "
        f"**3.6 × {multiplier} = {decimal_text(converted_dividend)}**, "
        f"**0.6 × {multiplier} = {decimal_text(converted_divisor)}**"
    )
    st.markdown(
        f"3. 바뀐 식: **{decimal_text(converted_dividend)} ÷ "
        f"{decimal_text(converted_divisor)} = {format_fraction(converted_answer)}**"
    )
    st.markdown(
        '<div class="principle"><b>발견한 원리</b><br>'
        "나누어지는 수와 나누는 수에 같은 수를 곱해도 몫은 변하지 않아요. "
        "그래서 소수로 나누는 식을 자연수의 나눗셈으로 바꾸어 계산할 수 있어요!"
        "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        f"비교해 보세요: 처음 몫 {format_fraction(original_answer)} "
        f"= 바뀐 식의 몫 {format_fraction(converted_answer)}"
    )

missions = [
    ("mission_1", "미션 1", "4.8 ÷ 2", Decimal("4.8"), Decimal("2"),
     "4.8을 2개의 같은 양으로 나누어 보세요."),
    ("mission_2", "미션 2", "5.4 ÷ 0.9", Decimal("5.4"), Decimal("0.9"),
     "나누는 수 0.9에 10을 곱하면 나누어지는 수는 어떻게 바뀔까요?"),
    ("mission_3", "미션 3", "7.2 ÷ 0.6", Decimal("7.2"), Decimal("0.6"),
     "두 수에 10을 곱해 자연수의 나눗셈으로 바꾸어 보세요."),
]

st.subheader("탐구 미션")
st.write("배운 원리를 써서 미션을 해결해 보세요!")
mission_columns = st.columns(3)
for column, (key, title, equation, dividend, divisor, hint) in zip(
    mission_columns, missions
):
    with column:
        with st.container(border=True):
            st.markdown(f"#### {title}")
            st.markdown(f"### {equation}")
            answer_raw = st.text_input(
                "답", placeholder="숫자를 입력하세요", key=f"{key}_answer"
            )
            if st.button("미션 확인", key=f"{key}_check"):
                try:
                    entered = parse_decimal(answer_raw, "답")
                    is_correct = Fraction(entered) == exact_quotient(dividend, divisor)
                    feedback = (
                        is_correct,
                        "미션 성공! 다음 탐험으로 출발해요." if is_correct else hint,
                    )
                except ValueError as error:
                    feedback = (None, str(error))
                st.session_state[f"{key}_feedback"] = (*feedback, answer_raw)
            feedback = st.session_state.get(f"{key}_feedback")
            if feedback and feedback[2] == answer_raw:
                correct, message, _ = feedback
                if correct:
                    st.success(message)
                elif correct is None:
                    st.warning(message)
                else:
                    st.info(message)

with st.container(border=True):
    st.subheader("오늘의 탐험 정리")
    st.markdown(
        """
        - 소수의 나눗셈은 생활에서 **양을 똑같이 나누거나**, 어떤 양이 **몇 번 들어가는지** 알아볼 때 사용해요.
        - 소수로 나눌 때는 **나누어지는 수와 나누는 수에 같은 수를 곱해** 자연수의 나눗셈으로 바꿀 수 있어요.
        - 두 수를 똑같은 수만큼 바꾸어도 나눗셈의 **몫은 변하지 않아요**.
        """
    )
