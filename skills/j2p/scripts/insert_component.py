"""
components.html의 특정 행 범위를 paper.html의 지정 줄에 삽입합니다.
컴포넌트 내용이 stdout에 출력되지 않으므로 컨텍스트 오염이 없습니다.

사용법:
    python skills/j2p/scripts/insert_component.py <start> <end> <insert_after> [target]

인자:
    start        components.html 시작 행 (1-indexed)
    end          components.html 끝 행 (1-indexed, 포함)
    insert_after target 파일의 몇 번째 줄 뒤에 삽입할지 (1-indexed)
    target       삽입 대상 파일 (기본값: paper.html)

예시:
    python skills/j2p/scripts/insert_component.py 793 821 42
    python skills/j2p/scripts/insert_component.py 793 821 42 paper.html
"""

import sys

COMPONENTS = "skills/j2p/assets/components.html"

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    start = int(sys.argv[1])
    end = int(sys.argv[2])
    insert_after = int(sys.argv[3])
    target = sys.argv[4] if len(sys.argv) > 4 else "paper.html"

    comp_lines = open(COMPONENTS, encoding="utf-8").readlines()
    component = "".join(comp_lines[start - 1 : end]).replace("\x00", "")

    lines = open(target, encoding="utf-8").readlines()
    lines.insert(insert_after, component)
    open(target, "w", encoding="utf-8").write("".join(lines))

if __name__ == "__main__":
    main()
