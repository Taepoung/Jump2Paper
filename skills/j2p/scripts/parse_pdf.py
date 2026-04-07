"""
PDF 파일을 파싱하고 본문 / Appendix로 분리합니다.
이미지도 본문용 / Appendix용으로 분리 추출합니다.

사용법:
    python skills/j2p/scripts/parse_pdf.py [filename]

인자:
    filename  파일명을 지정하면 현재 디렉토리에서 찾습니다.
              생략하면 앱 업로드 경로(/mnt/user-data/uploads/)에서 찾습니다.

출력:
    /tmp/paper_main.txt       — 본문 (References/Bibliography 이전)
    /tmp/paper_appendix.txt   — Appendix (없으면 빈 파일)
    /tmp/fig_main-*.jpg       — 본문 Figure crop 이미지
    /tmp/fig_appendix-*.jpg   — Appendix Figure crop 이미지 (Appendix 없으면 생성 안 함)
    stdout: PDF 경로, Appendix 시작 페이지
"""

import glob
import re
import subprocess
import sys

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pymupdf"], check=True)

import fitz

REF_PATTERN = re.compile(
    r"^\s*("
    r"References|REFERENCES"
    r"|Bibliography|BIBLIOGRAPHY|Bibliographie|BIBLIOGRAPHIE"
    r"|Works\s+Cited|WORKS\s+CITED"
    r"|Literature|LITERATURE"
    r")\s*$",
    re.MULTILINE,
)

APP_PATTERN = re.compile(
    r"^\s*("
    r"Appendix|APPENDIX|Appendices|APPENDICES"
    r"|Supplementary|SUPPLEMENTARY"
    r"|Supplement|SUPPLEMENT"
    r"|[A-Z]\.\s+[A-Z][a-z]"
    r")\b",
    re.MULTILINE,
)


def find_pdf(filename: str) -> str:
    if filename:
        return filename
    matches = glob.glob("/mnt/user-data/uploads/*.pdf")
    return matches[0] if matches else ""


def split_text(text: str) -> tuple[str, str]:
    app_match = APP_PATTERN.search(text)
    search_end = app_match.start() if app_match else len(text)
    appendix = text[app_match.start():].strip() if app_match else ""

    ref_matches = list(REF_PATTERN.finditer(text, 0, search_end))
    ref_match = ref_matches[-1] if ref_matches else None
    main = text[:ref_match.start()].rstrip() if ref_match else text[:search_end].rstrip()

    return main, appendix


def find_appendix_page(raw_text: str) -> int | None:
    """Appendix 시작 페이지 번호 반환 (1-indexed). 없으면 None."""
    pages = raw_text.split("\f")
    for i, page in enumerate(pages, 1):
        if APP_PATTERN.search(page):
            return i
    return None


def extract_figures(doc: fitz.Document, first_page: int, last_page: int, prefix: str) -> int:
    """
    페이지 범위에서 이미지 블록을 crop하여 저장.
    반환값: 저장된 Figure 수 (0이면 해당 범위에 이미지 없음)
    """
    count = 0
    for page_num in range(first_page - 1, last_page):  # fitz는 0-indexed
        page = doc[page_num]
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 1:  # 1 = 이미지 블록
                continue
            r = block["bbox"]
            # 여백 5pt 추가 후 페이지 범위로 클리핑
            rect = fitz.Rect(r[0] - 5, r[1] - 5, r[2] + 5, r[3] + 5) & page.rect
            pix = page.get_pixmap(dpi=150, clip=rect)
            pix.save(f"{prefix}-{count + 1:03d}.jpg")
            count += 1
    return count


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else ""
    pdf = find_pdf(filename)

    if not pdf:
        print("ERROR: PDF 파일을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    print(pdf)

    subprocess.run(["pdftotext", "-layout", pdf, "/tmp/paper_raw.txt"], check=True)

    raw = open("/tmp/paper_raw.txt", encoding="utf-8", errors="replace").read()
    main_text, appendix_text = split_text(raw)

    open("/tmp/paper_main.txt", "w", encoding="utf-8").write(main_text)
    open("/tmp/paper_appendix.txt", "w", encoding="utf-8").write(appendix_text)

    app_page = find_appendix_page(raw)

    doc = fitz.open(pdf)
    total_pages = len(doc)

    if app_page:
        main_count = extract_figures(doc, 1, app_page - 1, "/tmp/fig_main")
        app_count = extract_figures(doc, app_page, total_pages, "/tmp/fig_appendix")
        print(f"Appendix 시작 페이지: {app_page}")
        print(f"Figure 추출 — 본문: {main_count}개 / Appendix: {app_count}개")
    else:
        main_count = extract_figures(doc, 1, total_pages, "/tmp/fig_main")
        print(f"Appendix 없음 — 전체 Figure {main_count}개를 fig_main으로 추출")

    doc.close()

    has_appendix = "있음" if appendix_text else "없음"
    print(f"분리 완료 — 본문: {len(main_text)}자 / Appendix: {has_appendix}")


if __name__ == "__main__":
    main()
