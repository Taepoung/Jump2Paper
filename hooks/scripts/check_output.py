#!/usr/bin/env python3
"""
PostToolUse hook: Write/Edit 후 .html 파일의 JS 문법 오류와 LaTeX 오염을 감지.
stdout 출력 → Claude에게 피드백으로 전달됨.
"""

import json
import os
import re
import sys


# ─── 진입점 ──────────────────────────────────────────────────────────────────

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path.endswith(".html"):
        return
    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    issues = []
    issues.extend(check_js(content))
    issues.extend(check_latex(content))

    if issues:
        print("=== [자동 검토] 출력 파일에서 오류가 발견되었습니다. 즉시 수정하세요. ===")
        for issue in issues:
            print(issue)
        print("=" * 60)


# ─── JS 문법 검사 ─────────────────────────────────────────────────────────────

def check_js(content: str) -> list[str]:
    issues = []

    # <script> 블록 추출 (src 없는 인라인만)
    script_re = re.compile(
        r"<script(?![^>]*\bsrc\b)[^>]*>(.*?)</script>",
        re.DOTALL | re.IGNORECASE,
    )
    scripts = [(m.group(1), m.start()) for m in script_re.finditer(content)]

    for idx, (code, offset) in enumerate(scripts, 1):
        if not code.strip():
            continue
        errs = _js_syntax_check(code, idx)
        issues.extend(errs)

    return issues


def _js_syntax_check(code: str, block_num: int) -> list[str]:
    """
    순수 Python으로 할 수 있는 JS 문법 검사.
    - 괄호/브레이스/대괄호 균형
    - 문자열/템플릿 리터럴 미종료
    - 일반적인 "Unexpected identifier" 패턴
    """
    errs = []
    label = f"<script 블록 #{block_num}>"

    # 1. 스택 기반 괄호 균형 검사 (문자열 내부 제외)
    balance_err = _check_bracket_balance(code, label)
    if balance_err:
        errs.append(balance_err)

    # 2. 미종료 템플릿 리터럴 (백틱)
    if _has_unclosed_template(code):
        errs.append(f"[JS 문법 오류] {label} — 미종료 템플릿 리터럴(`) 감지")

    # 3. 미종료 문자열
    unclosed = _has_unclosed_string(code)
    if unclosed:
        errs.append(f"[JS 문법 오류] {label} — 미종료 문자열({unclosed}) 감지")

    return errs


def _check_bracket_balance(code: str, label: str) -> str | None:
    """괄호 균형 검사. 문자열 내부는 건너뜀."""
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    in_str = None
    i = 0

    while i < len(code):
        ch = code[i]

        # 문자열 이스케이프
        if in_str and ch == "\\" and i + 1 < len(code):
            i += 2
            continue

        # 문자열 진입/탈출
        if ch in ('"', "'") and in_str is None:
            in_str = ch
            i += 1
            continue
        if ch == in_str:
            in_str = None
            i += 1
            continue
        if in_str:
            i += 1
            continue

        # 템플릿 리터럴은 단순 스킵 (중첩 복잡해서 별도 처리)
        if ch == "`":
            end = code.find("`", i + 1)
            i = end + 1 if end != -1 else len(code)
            continue

        # 한 줄 주석
        if ch == "/" and i + 1 < len(code) and code[i + 1] == "/":
            nl = code.find("\n", i)
            i = nl + 1 if nl != -1 else len(code)
            continue

        # 블록 주석
        if ch == "/" and i + 1 < len(code) and code[i + 1] == "*":
            end = code.find("*/", i + 2)
            i = end + 2 if end != -1 else len(code)
            continue

        if ch in ("(", "[", "{"):
            stack.append((ch, i))
        elif ch in (")", "]", "}"):
            if stack and stack[-1][0] == pairs[ch]:
                stack.pop()
            else:
                line = code[:i].count("\n") + 1
                return f"[JS 문법 오류] {label} — 라인 {line}: 예상치 못한 '{ch}' (짝 없음)"
        i += 1

    if stack:
        ch, pos = stack[-1]
        line = code[:pos].count("\n") + 1
        return f"[JS 문법 오류] {label} — 라인 {line}: '{ch}' 가 닫히지 않음"

    return None


def _has_unclosed_template(code: str) -> bool:
    """백틱 쌍이 맞는지 확인 (중첩/이스케이프 미지원, 단순 홀수 카운트)."""
    count = 0
    i = 0
    while i < len(code):
        if code[i] == "\\" and i + 1 < len(code):
            i += 2
            continue
        if code[i] == "`":
            count += 1
        i += 1
    return count % 2 != 0


def _has_unclosed_string(code: str) -> str | None:
    """미종료 문자열 감지. 닫히지 않은 따옴표 종류 반환."""
    for quote in ('"', "'"):
        count = 0
        i = 0
        while i < len(code):
            if code[i] == "\\" and i + 1 < len(code):
                i += 2
                continue
            if code[i] == quote:
                count += 1
            i += 1
        if count % 2 != 0:
            return quote
    return None


# ─── LaTeX 오염 검사 ─────────────────────────────────────────────────────────

# Python 문자열 처리 시 백슬래시가 오염되는 패턴:
#   \t → 0x09 (탭)   : \text, \theta, \tau, \top, \to, \times, \textbf ...
#   \n → 0x0a (개행)  : \nabla, \nu, \newline, \nonumber ...  (display math에선 허용)
#   \r → 0x0d (CR)   : \rho, \right, \rm ...
#   \f → 0x0c (FF)   : \frac, \forall, \phi ...
#   \b → 0x08 (BS)   : \beta, \bar, \begin ...

_CORRUPTION_PATTERNS = [
    # (정규식, 설명, 허용할 math 종류)
    (r"\x09[A-Za-z]",  r"탭(\t) + 문자 → \text·\theta·\tau·\times 등 오염 의심", "both"),
    (r"\x0d[A-Za-z]",  r"CR(\r) + 문자 → \rho·\right 등 오염 의심",             "both"),
    (r"\x0c[A-Za-z]",  r"FF(\f) + 문자 → \frac·\forall·\phi 등 오염 의심",      "both"),
    (r"\x08[A-Za-z]",  r"BS(\b) + 문자 → \beta·\bar·\begin 등 오염 의심",       "both"),
]

# math 구분자 (inline / display)
_MATH_BLOCK_RE = re.compile(
    r"(\\\(.*?\\\)"          # \( ... \)
    r"|\\\[.*?\\\]"          # \[ ... \]
    r"|\$\$.*?\$\$"          # $$ ... $$
    r"|\$[^\$\n]+?\$)",      # $ ... $ (inline, 개행 없음)
    re.DOTALL,
)


def check_latex(content: str) -> list[str]:
    issues = []

    # math 블록만 추출
    math_blocks = _MATH_BLOCK_RE.findall(content)
    if not math_blocks:
        return issues

    math_content = "\n".join(math_blocks)

    for pattern, description, _ in _CORRUPTION_PATTERNS:
        matches = list(re.finditer(pattern, math_content))
        if not matches:
            continue

        # 처음 3건만 보고
        for m in matches[:3]:
            start = max(0, m.start() - 25)
            end = min(len(math_content), m.end() + 25)
            ctx = repr(math_content[start:end])
            issues.append(
                f"[LaTeX 오염] {description}\n"
                f"  컨텍스트: {ctx}\n"
                f"  → 해당 수식의 백슬래시 명령어를 원문에서 다시 확인하고 수정하세요."
            )

        if len(matches) > 3:
            issues.append(
                f"[LaTeX 오염] 위 패턴이 추가로 {len(matches) - 3}곳 더 발견됨"
            )

    return issues


if __name__ == "__main__":
    main()
