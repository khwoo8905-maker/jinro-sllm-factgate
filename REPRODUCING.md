# 재현 안내

이 저장소는 케이스스터디에서 설명한 방법을 재현하기 위한 코드와 합성 데이터를 담고 있습니다.

## 포함된 것

- `scripts/` — 합성 페르소나 생성(`gen_personas_v3.py`, `persona_schema.json`), 평가 하네스(`eval_jinro_full.py`), 게이트 비교(`gate_eval3.py`), 추천-단위 팩트 게이트와 추론 파이프라인(`jinro_gate.py`, `jinro_product.py`)
- `data/personas_v3.jsonl` — 합성 학생 진로 페르소나 200,000건 (생성기로 재생성 가능)
- `data/DATASET_CARD.md` — 데이터셋 설명

## 직접 준비해야 하는 것 (저장소에 포함하지 않음)

- **진로 근거 문서·임베딩**: `careernet_docs.json`, `careernet_vectors_kure.npy`. 커리어넷 자료의 이용 약관에 따라 직접 확보해야 합니다.
- **임베딩 서버**: 스크립트는 KURE-v1 임베딩을 `http://localhost:8081/embed` 에서 제공한다고 가정합니다.
- **언어모델·어댑터**: Qwen3.5-4B 등 베이스 모델. LoRA 어댑터 가중치는 포함하지 않습니다.

## 참고

스크립트의 파일 경로와 서버 주소는 원 개발 환경을 기준으로 하며, 사용 환경에 맞게 조정이 필요합니다. 평가 수치는 합성 데이터 50건 기준이며 실제 학생 검증 전입니다(README의 한계 참조).
