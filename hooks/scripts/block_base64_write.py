"""
PreToolUse hook: Write/Edit 툴로 Base64 이미지를 직접 삽입하려는 시도를 차단합니다.
inject_figure.py 스크립트를 사용하세요.
exit code 2 → 명령 실행 차단.
"""

import json
import re
import sys

# data:image/...;base64, 뒤에 실제 Base64 데이터가 100자 이상이면 차단
BASE64_RE = re.compile(r"data:[^;]+;base64,[A-Za-z0-9+/=]{100,}")


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_input = payload.get("tool_input", {})

    # Write: content 필드 / Edit: new_string 필드
    text = tool_input.get("content", "") or tool_input.get("new_string", "")

    if BASE64_RE.search(text):
        print(
            "[차단] Base64 이미지를 툴로 직접 삽입하면 컨텍스트가 오염됩니다.\n"
            "inject_figure.py 스크립트를 사용하세요:\n"
            "  python skills/j2p/scripts/inject_figure.py <image_path> <placeholder>",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
