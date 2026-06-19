---
license: cc-by-4.0
language:
- ko
task_categories:
- text-generation
tags:
- korean
- education
- career-counseling
- 진로상담
- synthetic
- persona
size_categories:
- 100K<n<1M
---

# 한국 중·고등학생 진로상담 페르소나 (Korean Student Career-Counseling Personas)

진로상담(career counseling) sLLM 학습·평가용 **합성 학생 페르소나** 200,000명. 실제 학생 데이터 없음(100% 합성).

> 일반 인구 페르소나(예: NVIDIA Nemotron Persona Korea)와 달리, **진로상담 도메인에 특화**된 8개 축으로 설계되었습니다.

## 규모 (정직 표기)
- **총 200,000명** / **고유 속성조합 104,223개**
- 같은 속성조합이 여러 명 존재 = 인구 표본 성격 (각 인물 고유 sid)

## 스키마
| 필드 | 값 |
|------|-----|
| grade | 중1~고3 (6) |
| score_tier | 최상위~하위 (6, 정규형 분포) |
| interest | 공학·IT, 자연과학, 의약·보건, 인문·어학, 사회·상경, 교육, 예술·디자인, 체육, 미디어·콘텐츠, 미정 (10) |
| career_stage | 진로탐색 전 / 탐색 중 / 결정 임박 / 혼란·갈등 (4) |
| concern | 적성·성적불일치·부모이견·학과선택·직업정보부족·입시전략·재능의심·진로변경 (8) |
| region | 대도시 / 중소도시 / 읍면지역 (3) |
| special | 없음·경제적어려움·가정환경변화·건강·다문화·학교부적응·영재성 (7) |
| sex, sid | 성별 / 고유 합성 ID |

## 현실성 (조건부 샘플링)
독립 랜덤이 아니라 상관관계를 부여했습니다:
- **career_stage = f(grade)**: 중1 진로탐색전 60% → 고3 결정임박 54%
- **concern = f(career_stage)**: 단계별 고민 가중 (탐색전→적성/정보, 임박→입시/학과)
- score_tier 정규형(중간 두꺼움), region 50/35/15, special 없음 58%

## 의도된 용도
- 진로상담 sLLM SFT/평가용 **학생 입력 페르소나** 생성
- 동반 자료: 진로 sLLM + 팩트게이트 케이스스터디(할루시네이션 38%→0%)

## 한계 (Limitations)
- 100% 합성 — 실제 학생 분포·개인정보 아님
- interest는 균등 샘플(성적-관심 stereotype 회피 위해 상관 미부여)
- **진로상담 특화** → 일반 인구 대표성 아님 (Nemotron Persona Korea의 보완재)
- 이름 필드 의도적 제외(프라이버시)

## 생성 방식 / License
- 순수 조합 샘플링(LLM 미사용), seed 고정 재현 가능. 스크립트 동봉(gen_personas_v3.py).
- **CC BY 4.0**
