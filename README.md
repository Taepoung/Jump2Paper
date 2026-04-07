# Jump2Paper

<p align="center">
  Turn academic papers into interactive, explanation-first HTML pages.
</p>

<p align="center">
  학술 논문을 설명 중심의 인터랙티브 HTML 페이지로 바꾸는 워크플로우 모음입니다.
</p>

<p align="center">
  <img alt="version" src="https://img.shields.io/badge/version-2.1.0-111111?style=flat-square">
  <img alt="type" src="https://img.shields.io/badge/type-Claude%20skill%20%2B%20hooks-2f6fed?style=flat-square">
  <img alt="focus" src="https://img.shields.io/badge/focus-paper%20to%20web-0a7f5a?style=flat-square">
</p>

---

## Overview | 개요

**Jump2Paper** is a repository for converting academic papers into polished, readable HTML experiences instead of plain summaries. It bundles a reusable `j2p` skill, helper scripts, and Claude hooks that enforce safer HTML editing workflows.

**Jump2Paper**는 논문을 단순 요약이 아니라 읽기 쉬운 HTML 경험으로 바꾸기 위한 저장소입니다. 재사용 가능한 `j2p` 스킬, 보조 스크립트, 그리고 HTML 작성 실수를 줄이는 Claude hook이 함께 들어 있습니다.

## Why This Repo | 이 저장소의 목적

| English | 한국어 |
|---|---|
| Convert papers into story-driven HTML pages | 논문을 스토리 중심의 HTML 페이지로 변환 |
| Reuse structured components and design references | 구조화된 컴포넌트와 디자인 가이드를 재사용 |
| Guard against common HTML editing mistakes | HTML 작성 중 자주 나는 실수를 방지 |
| Support PDF parsing and figure injection workflows | PDF 파싱과 figure 주입 작업 흐름 지원 |

## Repository Structure | 저장소 구조

```text
.
|-- .claude-plugin/
|   `-- plugin.json
|-- hooks/
|   |-- hooks.json
|   `-- scripts/
|       |-- block_base64_write.py
|       |-- block_html_redirect.py
|       `-- check_output.py
`-- skills/
    `-- j2p/
        |-- SKILL.md
        |-- assets/
        |   `-- components.html
        |-- references/
        |   `-- design_system.md
        `-- scripts/
            |-- insert_component.py
            |-- inject_figure.py
            `-- parse_pdf.py
```

## Core Parts | 핵심 구성

### `skills/j2p`

**EN**
- Defines the end-to-end workflow for turning a paper into an interactive HTML page.
- `SKILL.md` contains the main writing rules, structure guidance, and storytelling principles.
- `assets/components.html` provides reusable page components.
- `references/design_system.md` acts as the design and interaction reference.

**KO**
- 논문을 인터랙티브 HTML 페이지로 바꾸는 전체 작업 흐름을 정의합니다.
- `SKILL.md`에는 작성 규칙, 구조 가이드, 스토리텔링 원칙이 들어 있습니다.
- `assets/components.html`은 재사용 가능한 페이지 컴포넌트를 제공합니다.
- `references/design_system.md`는 디자인 및 인터랙션 기준 문서 역할을 합니다.

### `skills/j2p/scripts`

| Script | Purpose |
|---|---|
| `parse_pdf.py` | Extract body text, appendix text, and figures from a PDF |
| `insert_component.py` | Insert predefined component blocks into the HTML page |
| `inject_figure.py` | Inject Base64 figure data into placeholders safely |

### `hooks`

**EN**
- `block_html_redirect.py` blocks unsafe shell-based HTML appends such as `cat >>` and `echo >>`.
- `block_base64_write.py` blocks direct Base64 image pasting during file edits.
- `check_output.py` validates generated `.html` files for common issues.

**KO**
- `block_html_redirect.py`는 `cat >>`, `echo >>` 같은 위험한 방식의 HTML 덧붙이기를 막습니다.
- `block_base64_write.py`는 파일 편집 중 Base64 이미지를 직접 붙여 넣는 작업을 막습니다.
- `check_output.py`는 생성된 `.html` 파일의 대표적인 문제를 검사합니다.

## Validation Checks | 자동 검사 항목

`check_output.py` currently looks for:

- JavaScript syntax issues
- LaTeX corruption patterns
- Duplicate `id` attributes
- Local file references inside HTML

현재 `check_output.py`는 다음 문제를 검사합니다.

- JavaScript 문법 오류
- LaTeX 손상 패턴
- 중복된 `id` 속성
- HTML 내부의 로컬 파일 참조

## Typical Workflow | 기본 사용 흐름

```text
Paper PDF / LaTeX
        |
        v
   j2p skill guidance
        |
        v
  HTML scaffold + components
        |
        v
 figure placeholders + injection
        |
        v
   hook-based validation
        |
        v
   final paper HTML page
```

1. Read `skills/j2p/SKILL.md`.
2. Start from the HTML scaffold and reusable components.
3. Parse the paper if the source is a PDF.
4. Insert figure placeholders.
5. Inject figures with `inject_figure.py`.
6. Let the hooks validate the output.

1. `skills/j2p/SKILL.md`를 읽습니다.
2. HTML 골격과 재사용 컴포넌트로 작업을 시작합니다.
3. 입력이 PDF라면 먼저 파싱합니다.
4. figure placeholder를 넣습니다.
5. `inject_figure.py`로 figure를 주입합니다.
6. hook으로 결과물을 검사합니다.

## Safety Notes | 주의사항

- Do not paste large Base64 image blobs directly into edited HTML.
- Do not append HTML via shell redirection.
- Prefer the provided scripts for figure insertion and structured updates.
- Treat `SKILL.md` and `design_system.md` as the main source of truth.

- 큰 Base64 이미지 데이터를 HTML에 직접 붙여 넣지 마세요.
- 셸 리다이렉션으로 HTML 끝에 내용을 덧붙이지 마세요.
- figure 삽입과 구조화된 수정은 제공된 스크립트를 우선 사용하세요.
- `SKILL.md`와 `design_system.md`를 가장 중요한 기준 문서로 보세요.

## Plugin Info | 플러그인 정보

| Field | Value |
|---|---|
| Name | `jump2paper` |
| Version | `2.1.0` |
| Author | `Tim_Yoon` |
| Description | `When you want to jump into the paper, Just use it!` |

## Best Fit | 이런 경우에 적합함

**EN**
- You want a paper turned into a shareable web page.
- You need a repeatable workflow for paper-to-HTML conversion.
- You want guardrails while editing generated HTML.

**KO**
- 논문을 공유 가능한 웹 페이지로 바꾸고 싶을 때
- paper-to-HTML 변환 과정을 반복 가능한 형태로 정리하고 싶을 때
- 생성된 HTML을 수정할 때 안전장치가 필요할 때

## Status | 상태

This repository is closer to a reusable skill-and-hook package than to a standalone application project.

이 저장소는 독립 실행형 앱이라기보다 재사용 가능한 스킬 및 훅 패키지에 가깝습니다.
