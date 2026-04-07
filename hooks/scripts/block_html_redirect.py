"""
PreToolUse hook: cat >> / echo >> 로 HTML 파일에 직접 추가하는 명령을 차단합니다.
exit code 2 → 명령 실행 차단.
"""

import json
import re
import sys

PATTERN = re.compile(r"(cat|echo)\s+.*>>\s*\S+\.html", re.IGNORECASE)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    command = payload.get("tool_input", {}).get("command", "")

    if PATTERN.search(command):
        print(
            "[차단] cat >> / echo >> 로 HTML에 직접 추가하면 </body>, </html> 바깥에 내용이 붙어 파일이 깨집니다.\n"
            "Edit 툴 또는 Python 스크립트를 사용하세요.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
