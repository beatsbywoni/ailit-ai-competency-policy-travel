# corpus_inventory/

Per-document metadata for the AILIT_TRAVEL corpus.

| File | Scope | Status |
|---|---|---|
| `pilot_urls.csv` | Sprint 0 5-country pilot (KR, GB, SG, FI, US) | draft v0 — URLs need verification, ~6 docs marked TBD |
| `full_urls.csv` | Sprint 1 25-country full corpus | not yet created |

## Columns (pilot_urls.csv)

| Column | Description |
|---|---|
| `country` | English country name |
| `iso2` | ISO 3166-1 alpha-2 |
| `language` | ISO 639-1 of the document body |
| `doc_id` | Stable identifier, `{ISO2}-{NN}` |
| `document_title` | Native-language title (transliterated where needed) |
| `issuing_body` | Ministry / agency / parliament |
| `publication_date` | YYYY-MM[-DD] |
| `unesco_cohort` | `pre` / `post` relative to 2024-09 UNESCO Framework launch — drives RQ3 |
| `genre` | strategy / curriculum / guidance / report / legislation / teacher_pd / executive_order |
| `format` | pdf / html |
| `url` | Authoritative URL (use `TBD` if pending) |
| `notes` | Free-text, e.g. translation availability, AI-specific scope flag |

## 2026-05-29 URL 확정 (TBD 6건 + 보너스 1건)

| doc_id | 해결 결과 | URL |
|---|---|---|
| KR-04 | ✓ 확정 — "모두를 위한 AI 인재양성 방안" (2025-11-10) | https://www.moe.go.kr/boardCnts/viewRenew.do?boardID=294&boardSeq=104462 |
| KR-05 | + 추가 — "2026년 교육부 업무계획" (2025-12-12) | https://www.moe.go.kr/upload/filedown/2026_business_plan_press_release.pdf (직접 PDF) |
| GB-04 | ✓ 확정 — "Generative AI: product safety expectations" (2025-01-22) | https://www.gov.uk/government/publications/generative-ai-product-safety-expectations/generative-ai-product-safety-expectations |
| FI-01 | ⚠ 교체 — Finland AI Programme 4.0이 기업 중심이라 부적합. OPH AI Guide for Teachers로 대체 | https://www.oph.fi/sites/default/files/documents/AI_Guide_for_Teachers_Digital_Information_Literacy.pdf |
| FI-03 | ✓ 확정 — OPH "AI and ethics in education" 배경자료 | https://www.oph.fi/en/teemat-ja-kehittaminen/backround-material-ai-and-ethics-education |
| FI-04 | + 추가 — OKM Recommendations for AI 프로젝트 페이지 (2024) | https://okm.fi/en/project?tunnus=OKM021%3A00%2F2024 |
| US-03 | ✓ 확정 — EO 14277 (2025-04-23) | https://www.whitehouse.gov/presidential-actions/2025/04/advancing-artificial-intelligence-education-for-american-youth/ |
| US-04 | ✓ 확정 — DOE "Empowering Education Leaders" Toolkit (2024-10-24, **post-Sept 2024**) | https://tech.ed.gov/files/2024/10/ED-OET-AI-Toolkit-FINAL.pdf |

총 18 → **20**개 문서 (KR-05, FI-04 보너스 추가).

## Sprint 0 decision-gate prerequisite (갱신)

| Country | Verified | TBD | Cohort split (pre / post Sept 2024) |
|---|---|---|---|
| KR | 5 | 0 | 2 / 3 |
| GB | 4 | 0 | 2 / 2 |
| SG | 3 | 0 | 2 / 1 |
| FI | 4 | 0 | 2 / 2 |
| US | 4 | 0 | 2 / 2 |
| **Total** | **20** | **0** | **10 / 10** ✓ |

각국 ≥ 3 docs 기준 + 각국 ≥ 1 post-Sept 2024 docs 기준 모두 충족. RQ3 (temporal cohort) 가설을 통계적으로 시험할 수 있는 분포.

## 2026-05-29 (session 4) — 한국 boardSeq 페이지 404 대응

교육부 공식 boardSeq URL 4개(KR-01/02/03/04)가 모두 페이지 자체가 삭제·이동되어 다운로드 불가. 대체 출처로 교체:

| doc_id | 신규 URL | 출처 | 비고 |
|---|---|---|---|
| KR-01 | https://webst.edunet.net/AIDT/디지털%20기반%20교육혁신%20방안.pdf | EDUNET AIDT 미러 | 본문 PDF, 약 2MB 예상 |
| KR-02 | https://ezentextbook.co.kr/data/skin/respon_default/doc/2022_edu_pdf01.pdf | ezentextbook 미러 | 교육부 고시 제2022-33호 [별책 1] 초·중등학교 교육과정 총론 |
| KR-03 | https://eiec.kdi.re.kr/policy/callDownload.do?num=250346&filenum=2&dtime=20240503070237 | KDI EIEC 정책자료 | 디지털 기반 교육혁신 역량 강화 지원방안 (교실혁명 선도교사 사업) PDF |
| KR-04 | https://www.korea.kr/briefing/policyBriefingView.do?newsId=156727284 | 대한민국 정책브리핑 | 모두를 위한 AI 인재양성 방안 본문 HTML. 사용자 PNG도 `KR-04_pressrelease.png`로 백업 보관 |

⚠ **제3자 미러 사용 정당화**: KR-01, KR-02, KR-03 모두 공식 정부 사이트에서 동일 문서를 호스팅하던 URL이 사라졌으나 본문 내용 자체는 변하지 않음. 미러본은 텍스트 기반 분석을 위한 sentence-level 매칭에 영향 없음. manuscript §6.5에서 corpus harvest history를 transparently 기록.

KR-04 PNG: 본문이 이미지라 OCR 필요. 다만 korea.kr HTML 텍스트가 동일 내용이므로 OCR 불필요. 사용자 백업으로만 보관.

## 한국 정책문서 hwpx 처리 — 다음 세션 작업 (해소됨)

~~KR-01, KR-03, KR-04는 교육부 보도자료 페이지(boardSeq URL)에 첨부된 .hwpx 파일이 본문임.~~ → boardSeq 페이지 404 확인됨 (2026-05-29). 위 대체 URL로 해소.

hwpx 변환 스크립트 작성은 Sprint 1 본 분석에서 한국 추가 문서가 hwpx로 발견될 경우 작성 (`hwp5txt` 또는 `libreoffice --headless`).

## 다운로드 실패 대응

`02_harvest_pilot.sh`가 `[fail]` 표시한 항목 = 자동 다운로드 안 됐다는 뜻. 대응:

1. URL을 브라우저로 직접 열어 PDF/HWPX 받기
2. 받은 파일을 `data/corpus_pilot/raw/{doc_id}.{format}`로 저장 (정확한 파일명 사용)
3. 스크립트 재실행 시 자동으로 skip 처리됨

샌드박스 환경에서는 외부 다운로드 전체가 차단됨. 사용자 Mac에서는 대부분 성공할 것으로 예상.
