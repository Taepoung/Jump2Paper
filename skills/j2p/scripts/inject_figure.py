"""
이미지 파일을 Base64로 변환해 HTML의 placeholder에 주입합니다.
Base64 내용이 대화 내역에 남지 않습니다.

사용법:
    python skills/j2p/scripts/inject_figure.py <image_path> <placeholder> [target]

인자:
    image_path   주입할 이미지 파일 경로 (예: /tmp/fig_main-000.jpg)
    placeholder  HTML 내 치환할 placeholder (예: {{FIG_1_B64}})
    target       대상 HTML 파일 (기본값: paper.html)

예시:
    python skills/j2p/scripts/inject_figure.py /tmp/fig_main-000.jpg {{FIG_1_B64}}
    python skills/j2p/scripts/inject_figure.py /tmp/fig_main-001.jpg {{FIG_2_B64}} paper.html
"""

import base64
import sys


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    image_path = sys.argv[1]
    placeholder = sys.argv[2]
    target = sys.argv[3] if len(sys.argv) > 3 else "paper.html"

    img_b64 = base64.b64encode(open(image_path, "rb").read()).decode()
    content = open(target, encoding="utf-8").read().replace(placeholder, img_b64)
    open(target, "w", encoding="utf-8").write(content)


if __name__ == "__main__":
    main()
