# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
from html import escape

import streamlit as st


st.set_page_config(
    page_title="소수 나눗셈 탐험대",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-family: 'Gowun Dodum', sans-serif; }
    h1, h2, h3 { font-family: 'Jua', sans-serif !important; color: #29365f; }
    .hero {
        padding: 2rem 2.2rem; border-radius: 26px; margin: .4rem 0 1.4rem;
        background: linear-gradient(120deg, #fff2cc 0%, #ffe1e8 52%, #e2f4ff 100%);
        border: 1px solid #f3dfe1;
    }
    .hero h1 { font-size: clamp(2.2rem, 5vw, 3.5rem); margin: 0 0 .4rem; }
    .goal { color: #44506e; font-size: 1.12rem; margin-bottom: 0; }
    .section-label {
        display: inline-block; padding: .35rem .85rem; border-radius: 999px;
        background: #edf2ff; color: #47578d; font-weight: 700; margin: 1.1rem 0 .25rem;
    }
    .visual {
        background: #fbfcff; border: 1px solid #e8ecf5; border-radius: 18px;
        padding: .6rem; margin: .7rem 0;
    }
    .equation {
        background: #f4f3ff; border: 1px solid #e2defc; border-radius: 16px;
        padding: 1rem; text-align: center; font-size: clamp(1.3rem, 3vw, 2rem);
        font-weight: 700; color: #39356f; margin: .6rem 0;
    }
    .step {
        background: #fff; border-left: 5px solid #9a8ee8; padding: .75rem 1rem;
        border-radius: 8px; margin: .5rem 0;
    }
    .tiny-note { color: #5f6b85; font-size: .92rem; }
    @media (max-width: 700px) {
        .hero { padding: 1.3rem; }
        .visual { padding: .3rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def parse_decimal(raw_value: str, label: str) -> Decimal:
    value = raw_value.strip()
    if not value:
        raise ValueError(f"‘{label}’ 입력란을 채워 주세요.")
    if len(value) > 40:
        raise ValueError("입력값은 40자 이내로 써 주세요.")
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("숫자만 입력해 주세요.") from error
    if not number.is_finite():
        raise ValueError("올바른 숫자를 입력해 주세요.")
    if number.as_tuple().exponent > 12 or number.as_tuple().exponent < -12:
        raise ValueError("소수점 아래 12자리 이내로 입력해 주세요.")
    if number.adjusted() > 12:
        raise ValueError("1조보다 작은 수를 입력해 주세요.")
    return number


def exact_quotient(dividend: Decimal, divisor: Decimal) -> Fraction:
    if divisor == 0:
        raise ValueError("나누는 수가 0이에요. 0이 아닌 수를 입력해 주세요.")
    return Fraction(dividend) / Fraction(divisor)


def decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def fraction_text(value: Fraction) -> str:
    denominator = value.denominator
    remainder = denominator
    twos = fives = 0
    while remainder % 2 == 0:
        twos += 1
        remainder //= 2
    while remainder % 5 == 0:
        fives += 1
        remainder //= 5
    if remainder == 1:
        with localcontext() as context:
            context.prec = max(50, len(str(abs(value.numerator))) + twos + fives + 2)
            result = Decimal(value.numerator) / Decimal(value.denominator)
        return decimal_text(result)
    with localcontext() as context:
        context.prec = 12
        result = Decimal(value.numerator) / Decimal(value.denominator)
    return f"{value.numerator}/{value.denominator} (약 {decimal_text(result)})"


def svg_image(svg: str) -> None:
    st.markdown(f'<div class="visual">{svg}</div>', unsafe_allow_html=True)


def ribbon_svg(dividend: Decimal, parts: int) -> str:
    columns = min(parts, 8)
    rows = (parts + columns - 1) // columns
    cell_width, row_height = 88, 52
    width, height = columns * cell_width + 16, rows * row_height + 55
    part = fraction_text(exact_quotient(dividend, Decimal(parts)))
    pieces = []
    for index in range(parts):
        x = 8 + (index % columns) * cell_width
        y = 16 + (index // columns) * row_height
        pieces.append(
            f'<rect x="{x}" y="{y}" width="{cell_width - 5}" height="26" '
            'rx="7" fill="#ff9aaf" stroke="#dc6281" stroke-width="2"/>'
            f'<line x1="{x + cell_width - 5}" y1="{y}" x2="{x + cell_width - 5}" '
            f'y2="{y + 26}" stroke="#fff" stroke-width="3"/>'
            f'<text x="{x + (cell_width - 5) / 2}" y="{y + 45}" text-anchor="middle" '
            f'font-size="12" fill="#39415c">{part}m</text>'
        )
    return (
        f'<svg role="img" aria-label="리본 {decimal_text(dividend)}미터를 '
        f'{parts}조각으로 나눈 그림" viewBox="0 0 {width} {height}" '
        f'width="100%" style="max-width:760px;height:auto" xmlns="http://www.w3.org/2000/svg">'
        f'<text x="8" y="12" font-size="12" font-weight="bold" fill="#60435a">'
        f'전체 리본 {decimal_text(dividend)}m</text>{"".join(pieces)}</svg>'
    )


def juice_svg(total: Decimal, cup_amount: Decimal, count: Fraction) -> str:
    whole_cups = count.numerator // count.denominator
    has_remainder = count.denominator != 1
    shown_cups = min(max(1, whole_cups + int(has_remainder)), 24)
    columns = min(shown_cups, 6)
    rows = max(1, (shown_cups + columns - 1) // columns)
    width, height = max(470, columns * 92 + 140), rows * 120 + 120
    elements = [
        '<text x="16" y="23" font-size="14" font-weight="bold" fill="#34516b">'
        f'큰 용기: {decimal_text(total)}L</text>',
        '<rect x="24" y="42" width="72" height="112" rx="14" '
        'fill="#e8f7ff" stroke="#4789a8" stroke-width="3"/>',
        '<path d="M29 91 Q60 82 91 91 L91 143 Q91 149 84 149 L36 149 Q29 149 29 143Z" '
        'fill="#72c8f2"/>',
        '<path d="M96 62 Q122 62 122 83 L122 98" fill="none" stroke="#4789a8" '
        'stroke-width="6" stroke-linecap="round"/>',
        '<path d="M122 99 L122 111" stroke="#72c8f2" stroke-width="5" stroke-linecap="round"/>',
    ]
    for index in range(shown_cups):
        col, row = index % columns, index // columns
        x, y = 157 + col * 90, 45 + row * 112
        full = index < whole_cups
        if count == 0:
            label, fill_height = "0L", 0
        elif full:
            label = f"{decimal_text(cup_amount)}L"
            fill_height = 43
        else:
            remainder = count - whole_cups
            with localcontext() as context:
                context.prec = 12
                partial = Decimal(remainder.numerator) / Decimal(remainder.denominator) * cup_amount
            label = f"{decimal_text(partial)}L"
            fill_height = max(8, int(43 * float(remainder)))
        liquid = (
            f'<path d="M{x + 7} {y + 15} L{x + 51} {y + 15} L{x + 47} {y + 54} '
            f'Q{x + 29} {y + 60} {x + 11} {y + 54}Z" fill="#70c9ef" '
            f'transform="translate(0 {43 - fill_height})"/>'
            if fill_height
            else ""
        )
        elements.append(
            f'<path d="M{x} {y} L{x + 58} {y} L{x + 51} {y + 58} '
            f'Q{x + 29} {y + 66} {x + 7} {y + 58}Z" fill="#fff" '
            'stroke="#5884a1" stroke-width="2"/>'
            f'{liquid}'
            f'<text x="{x + 29}" y="{y + 84}" text-anchor="middle" font-size="12" '
            f'fill="#34455b">{label}</text>'
        )
    footer = f"컵마다 {decimal_text(cup_amount)}L씩"
    return (
        f'<svg role="img" aria-label="{escape(footer)} 주스를 컵에 나누어 담은 그림" '
        f'viewBox="0 0 {width} {height}" width="100%" style="max-width:780px;height:auto" '
        f'xmlns="http://www.w3.org/2000/svg">{"".join(elements)}'
        f'<text x="16" y="{height - 18}" font-size="13" fill="#34516b">{footer}</text></svg>'
    )


def tenths_svg() -> str:
    blocks = []
    for index in range(36):
        x, y = 15 + (index % 12) * 28, 30 + (index // 12) * 39
        blocks.append(
            f'<rect x="{x}" y="{y}" width="23" height="30" rx="4" '
            f'fill="{"#8dcdf0" if index < 30 else "#ffd36f"}" stroke="#6688a1"/>'
        )
    return (
        '<svg role="img" aria-label="3.6을 나타내는 십분의 일 모형 36개" '
        'viewBox="0 0 360 170" width="100%" style="max-width:560px;height:auto" '
        'xmlns="http://www.w3.org/2000/svg">'
        '<text x="15" y="20" font-size="13" fill="#40536a">3.6은 0.1이 36개예요</text>'
        f'{"".join(blocks)}'
        '<text x="15" y="157" font-size="12" fill="#40536a">파란 모형 30개와 노란 모형 6개</text></svg>'
    )


def number_line_svg() -> str:
    ticks = []
    for index in range(41):
        x = 30 + index * 14
        major = index % 10 == 0
        ticks.append(
            f'<line x1="{x}" y1="66" x2="{x}" y2="{78 if major else 72}" '
            f'stroke="#65718a" stroke-width="{"2" if major else "1"}"/>'
        )
    marker_x = 30 + 36 * 14
    return (
        '<svg role="img" aria-label="0부터 4까지 수직선에서 3.6의 위치" '
        'viewBox="0 0 620 112" width="100%" style="max-width:680px;height:auto" '
        'xmlns="http://www.w3.org/2000/svg">'
        '<line x1="30" y1="70" x2="590" y2="70" stroke="#65718a" stroke-width="3"/>'
        f'{"".join(ticks)}'
        '<text x="30" y="98" text-anchor="middle" font-size="12">0</text>'
        '<text x="170" y="98" text-anchor="middle" font-size="12">1</text>'
        '<text x="310" y="98" text-anchor="middle" font-size="12">2</text>'
        '<text x="450" y="98" text-anchor="middle" font-size="12">3</text>'
        '<text x="590" y="98" text-anchor="middle" font-size="12">4</text>'
        f'<circle cx="{marker_x}" cy="51" r="8" fill="#fa7188"/>'
        f'<text x="{marker_x}" y="35" text-anchor="middle" font-size="13" '
        'font-weight="bold" fill="#b84865">3.6</text></svg>'
    )


def division_process_svg(multiplier: int, dividend: Decimal, divisor: Decimal) -> str:
    scaled_dividend = dividend * multiplier
    scaled_divisor = divisor * multiplier
    return (
        '<svg role="img" aria-label="나누어지는 수와 나누는 수에 같은 수를 곱하는 과정" '
        'viewBox="0 0 700 126" width="100%" style="max-width:740px;height:auto" '
        'xmlns="http://www.w3.org/2000/svg">'
        '<rect x="15" y="18" width="180" height="86" rx="15" fill="#fff0f3" stroke="#e5a1b1"/>'
        '<text x="105" y="53" text-anchor="middle" font-size="12" fill="#704b57">나누어지는 수</text>'
        f'<text x="105" y="82" text-anchor="middle" font-size="20" font-weight="bold">'
        f'{decimal_text(dividend)} → {decimal_text(scaled_dividend)}</text>'
        '<rect x="260" y="18" width="180" height="86" rx="15" fill="#edf8ff" stroke="#96c7df"/>'
        '<text x="350" y="53" text-anchor="middle" font-size="12" fill="#456275">나누는 수</text>'
        f'<text x="350" y="82" text-anchor="middle" font-size="20" font-weight="bold">'
        f'{decimal_text(divisor)} → {decimal_text(scaled_divisor)}</text>'
        '<path d="M205 61 L247 61 M450 61 L492 61" stroke="#8378c7" stroke-width="3"/>'
        '<path d="M239 53 L248 61 L239 69 M484 53 L493 61 L484 69" '
        'fill="none" stroke="#8378c7" stroke-width="3"/>'
        f'<rect x="505" y="18" width="180" height="86" rx="15" fill="#f3f0ff" stroke="#b3a8df"/>'
        f'<text x="595" y="54" text-anchor="middle" font-size="13">두 수에 ×{multiplier}</text>'
        '<text x="595" y="81" text-anchor="middle" font-size="13">몫은 같아요</text></svg>'
    )


def show_activity(
    *,
    key: str,
    title: str,
    question: str,
    dividend_label: str,
    divisor_label: str,
    initial_dividend: str,
    initial_divisor: str,
    answer_label: str,
    kind: str,
) -> None:
    with st.container(border=True):
        st.subheader(title)
        st.write(question)
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
            if dividend < 0 or divisor < 0:
                raise ValueError("0 이상의 수를 입력해 주세요.")
            if divisor == 0:
                raise ValueError("나누는 수가 0이에요. 0이 아닌 수를 입력해 주세요.")

            answer = exact_quotient(dividend, divisor)

            if kind == "ribbon":
                if divisor != divisor.to_integral_value():
                    st.info("리본을 나눌 사람 수는 1 이상의 자연수로 입력해 주세요.")
                elif divisor > 60:
                    st.info("그림은 최대 60명까지 나누어 보여 줄 수 있어요.")
                else:
                    svg_image(ribbon_svg(dividend, int(divisor)))
                    st.caption(
                        f"리본 {decimal_text(dividend)}m를 {int(divisor)}명이 똑같이 나누면 "
                        f"한 사람은 {fraction_text(answer)}m를 가져요."
                    )
            else:
                svg_image(juice_svg(dividend, divisor, answer))
                st.caption(
                    f"주스 {decimal_text(dividend)}L를 한 컵에 "
                    f"{decimal_text(divisor)}L씩 담아요."
                )

            prediction = st.text_input(
                answer_label, placeholder="먼저 답을 예상해 숫자로 입력해 보세요.",
                key=f"{key}_answer",
            )
            if st.button("정답 확인", key=f"{key}_check"):
                try:
                    entered = parse_decimal(prediction, "예상한 답")
                    correct = Fraction(entered) == answer
                    st.session_state[f"{key}_feedback"] = {
                        "correct": correct,
                        "prediction": prediction,
                        "dividend": dividend_raw,
                        "divisor": divisor_raw,
                    }
                except ValueError as error:
                    st.session_state[f"{key}_feedback"] = {
                        "correct": None,
                        "prediction": prediction,
                        "dividend": dividend_raw,
                        "divisor": divisor_raw,
                        "error": str(error),
                    }

            feedback = st.session_state.get(f"{key}_feedback")
            if (
                feedback
                and feedback["prediction"] == prediction
                and feedback["dividend"] == dividend_raw
                and feedback["divisor"] == divisor_raw
            ):
                if feedback["correct"] is None:
                    st.warning(feedback["error"])
                else:
                    if feedback["correct"]:
                        st.success("정답이에요! 아래에서 풀이도 확인해 보세요.")
                    else:
                        st.info("입력한 답과 정답이 달라요. 아래 풀이를 살펴보세요.")
                    scale_places = max(0, -dividend.normalize().as_tuple().exponent)
                    multiplier = 10 ** scale_places
                    scaled_dividend = dividend * multiplier
                    scaled_divisor = (
                        divisor if kind == "ribbon" else divisor * multiplier
                    )
                    quotient_scaled = exact_quotient(scaled_dividend, scaled_divisor)
                    if kind == "ribbon":
                        if dividend == Decimal("3.6") and divisor == Decimal("4"):
                            st.markdown(
                                "**3.6 나누기 4는 36 나누기 4를 계산한 다음 "
                                "10분의 1로 바꾸는 것과 같아요.**"
                            )
                            st.markdown("**따라서 정답은 0.9미터예요.**")
                        st.markdown(
                            f"계산: {decimal_text(dividend)} ÷ {decimal_text(divisor)} "
                            f"= {decimal_text(scaled_dividend)} ÷ "
                            f"{decimal_text(divisor)} "
                            f"= {fraction_text(quotient_scaled)}"
                            + (f" ÷ {multiplier}" if multiplier > 1 else "")
                            + f" = **{fraction_text(answer)}m**"
                        )
                    else:
                        places = max(0, -divisor.normalize().as_tuple().exponent)
                        common_multiplier = 10 ** places
                        a, b = dividend * common_multiplier, divisor * common_multiplier
                        if dividend == Decimal("3.6") and divisor == Decimal("0.6"):
                            st.markdown(
                                "**3.6 나누기 0.6은 두 수에 똑같이 10을 곱하여 "
                                "36 나누기 6으로 바꿀 수 있어요.**"
                            )
                            st.markdown("**따라서 정답은 6컵이에요.**")
                        else:
                            st.markdown(
                                f"두 수에 똑같이 {common_multiplier}을 곱해 "
                                "자연수의 나눗셈으로 바꾸어 계산해요."
                            )
                        st.markdown(
                            f"계산: {decimal_text(dividend)} ÷ {decimal_text(divisor)} "
                            f"= ({decimal_text(dividend)} × {common_multiplier}) ÷ "
                            f"({decimal_text(divisor)} × {common_multiplier}) "
                            f"= {decimal_text(a)} ÷ {decimal_text(b)} "
                            f"= **{fraction_text(answer)}컵**"
                        )
        except (ValueError, OverflowError) as error:
            st.warning(str(error))


st.markdown(
    """
    <div class="hero">
      <h1>소수 나눗셈 탐험대</h1>
      <p class="goal"><b>오늘의 학습 목표</b> · 그림과 생활 속 상황을 통해 소수 나눗셈의 뜻을 알아보고,
      두 수에 같은 수를 곱해도 몫이 바뀌지 않는 이유를 찾아봐요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">학습 안내</div>', unsafe_allow_html=True)
with st.container(border=True):
    st.subheader("학습 안내")
    st.write(
        "리본을 똑같이 나누고 주스를 컵에 담으며 소수 나눗셈을 알아봐요. "
        "수를 바꾸면 그림과 계산 결과도 함께 달라져요. 활동을 차례로 해 보고 마지막 미션에 도전해 보세요!"
    )

st.markdown('<div class="section-label">첫 번째 활동</div>', unsafe_allow_html=True)
show_activity(
    key="ribbon",
    title="똑같이 나누기",
    question="리본 3.6미터를 4명이 똑같이 나누어 가지려고 합니다. 한 명이 가지는 리본은 몇 미터일까요?",
    dividend_label="나누어지는 수 (리본 전체, m)",
    divisor_label="나누는 수 (사람 수)",
    initial_dividend="3.6",
    initial_divisor="4",
    answer_label="한 명이 가지는 리본 (m)",
    kind="ribbon",
)

st.markdown('<div class="section-label">두 번째 활동</div>', unsafe_allow_html=True)
show_activity(
    key="juice",
    title="소수로 몇 번 나눌 수 있을까",
    question="3.6리터의 주스를 한 컵에 0.6리터씩 담으려고 합니다. 몇 컵에 담을 수 있을까요?",
    dividend_label="전체 주스의 양 (L)",
    divisor_label="한 컵에 담기는 양 (L)",
    initial_dividend="3.6",
    initial_divisor="0.6",
    answer_label="주스를 담을 수 있는 컵 수",
    kind="juice",
)

st.markdown('<div class="section-label">계산 원리 탐구</div>', unsafe_allow_html=True)
with st.container(border=True):
    st.subheader("소수점을 없애는 마법")
    st.markdown('<div class="equation">3.6 ÷ 0.6</div>', unsafe_allow_html=True)
    st.write(
        "나누어지는 수와 나누는 수에 같은 수를 곱해도 몫은 바뀌지 않아요. "
        "이 방법으로 3.6 ÷ 0.6을 자연수의 나눗셈으로 바꾸어 계산해 볼게요."
    )
    if "transform_multiplier" not in st.session_state:
        st.session_state.transform_multiplier = 10
    ten_col, hundred_col = st.columns(2)
    with ten_col:
        if st.button("두 수에 10을 곱하기", key="multiply_10", use_container_width=True):
            st.session_state.transform_multiplier = 10
    with hundred_col:
        if st.button("두 수에 100을 곱하기", key="multiply_100", use_container_width=True):
            st.session_state.transform_multiplier = 100

    multiplier = st.session_state.transform_multiplier
    start_a, start_b = Decimal("3.6"), Decimal("0.6")
    changed_a, changed_b = start_a * multiplier, start_b * multiplier
    original = exact_quotient(start_a, start_b)
    changed = exact_quotient(changed_a, changed_b)
    st.markdown(
        f'<div class="step"><b>1. 처음 식</b><br>3.6 ÷ 0.6 = {fraction_text(original)}</div>',
        unsafe_allow_html=True,
    )
    svg_image(division_process_svg(multiplier, start_a, start_b))
    st.markdown(
        f'<div class="step"><b>2. 두 수에 각각 {multiplier}을 곱해요</b><br>'
        f'3.6 × {multiplier} = {decimal_text(changed_a)}, '
        f'0.6 × {multiplier} = {decimal_text(changed_b)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="equation">{decimal_text(changed_a)} ÷ '
        f'{decimal_text(changed_b)} = {fraction_text(changed)}</div>',
        unsafe_allow_html=True,
    )
    compare_left, compare_right = st.columns(2)
    with compare_left:
        st.metric("처음 식의 몫", fraction_text(original))
    with compare_right:
        st.metric("바뀐 식의 몫", fraction_text(changed))
    st.success(
        "두 수에 같은 수를 곱해도 나눗셈의 몫은 바뀌지 않아요. "
        "따라서 3.6 ÷ 0.6은 36 ÷ 6으로 바꾸어 계산할 수 있고, 몫은 6이에요."
    )
    left_visual, right_visual = st.columns(2)
    with left_visual:
        st.caption("십분의 일 모형으로 보는 3.6")
        svg_image(tenths_svg())
    with right_visual:
        st.caption("수직선에서 3.6의 위치")
        svg_image(number_line_svg())

st.markdown('<div class="section-label">탐험 미션</div>', unsafe_allow_html=True)
with st.container(border=True):
    st.subheader("탐험 미션")
    st.write("배운 내용을 미션에 적용해 보세요. 정답이 아니어도 괜찮아요. 힌트를 읽고 다시 풀어 보세요.")
    mission_data = [
        ("mission_1", "첫 번째 미션", "4.8 ÷ 2", Decimal("4.8"), Decimal("2"),
         "4.8을 두 사람이 똑같이 나눈다고 생각해 보세요."),
        ("mission_2", "두 번째 미션", "5.4 ÷ 0.9", Decimal("5.4"), Decimal("0.9"),
         "0.9에 10을 곱해 자연수로 바꿔 보세요. 나누어지는 수에도 같은 수를 곱해야 해요."),
        ("mission_3", "세 번째 미션", "7.2 ÷ 0.6", Decimal("7.2"), Decimal("0.6"),
         "두 수에 각각 10을 곱해 자연수의 나눗셈으로 바꿔 보세요."),
    ]
    mission_columns = st.columns(3)
    for column, (key, title, equation, dividend, divisor, hint) in zip(
        mission_columns, mission_data
    ):
        with column:
            with st.container(border=True):
                st.markdown(f"#### {title}")
                st.markdown(f'<div class="equation">{equation}</div>', unsafe_allow_html=True)
                answer_raw = st.text_input(
                    "정답", placeholder="답을 숫자로 입력해 보세요.", key=f"{key}_answer"
                )
                if st.button("정답 확인", key=f"{key}_check", use_container_width=True):
                    try:
                        entered = parse_decimal(answer_raw, "정답")
                        correct = Fraction(entered) == exact_quotient(dividend, divisor)
                        st.session_state[f"{key}_feedback"] = (correct, answer_raw)
                        if correct:
                            st.session_state[f"{key}_completed"] = True
                    except ValueError as error:
                        st.session_state[f"{key}_feedback"] = (None, answer_raw, str(error))
                feedback = st.session_state.get(f"{key}_feedback")
                if feedback and feedback[1] == answer_raw:
                    if feedback[0] is None:
                        st.warning(feedback[2])
                    elif feedback[0]:
                        st.success("미션 성공! 잘 풀었어요.")
                        st.markdown(
                            '<div class="visual"><svg role="img" aria-label="축하 메달과 반짝이는 별" '
                            'viewBox="0 0 220 100" width="100%" style="max-width:230px;height:auto;display:block;margin:auto" '
                            'xmlns="http://www.w3.org/2000/svg"><path d="M75 5 L95 5 L100 42 L85 53 L70 42Z" '
                            'fill="#ff91a4"/><path d="M125 5 L145 5 L150 42 L135 53 L120 42Z" fill="#83c8ed"/>'
                            '<circle cx="110" cy="58" r="32" fill="#ffd66e" stroke="#d79c32" stroke-width="4"/>'
                            '<path d="M110 35 L117 50 L134 52 L122 64 L125 81 L110 73 L95 81 L98 64 L86 52 L103 50Z" '
                            'fill="#fff8d8" stroke="#d79c32" stroke-width="2"/>'
                            '<path d="M35 39 L39 49 L50 50 L42 58 L44 69 L35 64 L26 69 L28 58 L20 50 L31 49Z" '
                            'fill="#b49af2"/><path d="M185 24 L189 34 L200 35 L192 43 L194 54 L185 49 L176 54 L178 43 L170 35 L181 34Z" '
                            'fill="#b49af2"/></svg></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.info(f"힌트: {hint}")
    completed = sum(
        bool(st.session_state.get(f"{key}_completed"))
        for key, *_ in mission_data
    )
    st.progress(completed / len(mission_data), text=f"미션 진행 상황: {completed} / 3 완료")
    if completed == len(mission_data):
        st.balloons()
        st.success("축하해요! 세 가지 미션을 모두 해결했어요. 소수 나눗셈의 원리를 잘 이해했네요!")

st.markdown('<div class="section-label">학습 정리</div>', unsafe_allow_html=True)
with st.container(border=True):
    st.subheader("학습 정리")
    st.markdown(
        """
        - 소수의 나눗셈은 양을 똑같이 나누거나, 어떤 양 안에 다른 양이 몇 번 들어가는지 알아볼 때 사용해요.
        - 소수로 나눌 때는 나누어지는 수와 나누는 수에 같은 수를 곱해 자연수의 나눗셈으로 바꿔 계산할 수 있어요.
        - 두 수에 같은 수를 곱해도 나눗셈의 몫은 바뀌지 않아요.
        """
    )
    st.markdown("#### 오늘 배운 내용 스스로 확인하기")
    reflection = st.radio(
        "3.6 ÷ 0.6을 36 ÷ 6으로 바꾸려면 두 수를 어떻게 해야 할까요?",
        ["두 수에 각각 10을 곱해요.", "나누어지는 수에만 10을 곱해요.", "두 수를 더해요."],
        index=None,
        key="reflection",
    )
    if reflection == "두 수에 각각 10을 곱해요.":
        st.success("맞아요! 두 수에 같은 수를 곱해도 몫은 바뀌지 않아요.")
    elif reflection:
        st.info("두 수 모두에 같은 수를 곱해야 몫이 바뀌지 않아요. 계산 원리를 다시 생각해 보세요.")

