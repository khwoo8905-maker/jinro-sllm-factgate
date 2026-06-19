# v3: 조건부 빈도 유지(현실적 marginal) + 인물별 고유 sid(속성 dedup 안함) + name제거
import json, random, hashlib
from collections import Counter
random.seed(42)
ax=json.load(open("persona_schema.json"))["axes"]
STAGE={"중1":{"진로탐색 전":6,"탐색 중":3,"혼란·갈등":1,"결정 임박":0},
 "중2":{"진로탐색 전":5,"탐색 중":4,"혼란·갈등":1,"결정 임박":0},
 "중3":{"진로탐색 전":3,"탐색 중":5,"혼란·갈등":2,"결정 임박":1},
 "고1":{"진로탐색 전":2,"탐색 중":5,"혼란·갈등":2,"결정 임박":1},
 "고2":{"진로탐색 전":1,"탐색 중":4,"혼란·갈등":2,"결정 임박":3},
 "고3":{"진로탐색 전":0,"탐색 중":2,"혼란·갈등":3,"결정 임박":6}}
CONCERN={"진로탐색 전":{"적성을 모르겠음":4,"직업 정보 부족":3,"재능에 대한 의심":2,"학과 선택 고민":1,"성적과 목표 불일치":1,"부모와 의견 차이":1,"입시 전략 막막":1,"진로 변경 고민":1},
 "탐색 중":{"학과 선택 고민":3,"직업 정보 부족":3,"적성을 모르겠음":2,"성적과 목표 불일치":2,"부모와 의견 차이":2,"재능에 대한 의심":2,"입시 전략 막막":1,"진로 변경 고민":1},
 "결정 임박":{"입시 전략 막막":4,"성적과 목표 불일치":3,"학과 선택 고민":3,"부모와 의견 차이":2,"직업 정보 부족":1,"적성을 모르겠음":1,"재능에 대한 의심":1,"진로 변경 고민":1},
 "혼란·갈등":{"진로 변경 고민":4,"부모와 의견 차이":3,"재능에 대한 의심":3,"적성을 모르겠음":2,"성적과 목표 불일치":2,"학과 선택 고민":1,"직업 정보 부족":1,"입시 전략 막막":1}}
# 성적 분포(정규형: 중간 두꺼움), 지역/특수 현실 가중
SCORE={"최상위":7,"상위":18,"중상위":25,"중위":25,"중하위":18,"하위":7}
REGION={"대도시":50,"중소도시":35,"읍면지역":15}
SPECIAL={"없음":58,"경제적 어려움":12,"가정환경 변화":8,"학교 부적응":7,"건강 이슈":6,"다문화 배경":5,"영재성":4}
def wp(d): ks=list(d); return random.choices(ks,weights=[d[k] for k in ks])[0]
N=200000; out=[]; combos=set()
for i in range(N):
    g=random.choice(ax["grade"]); cs=wp(STAGE[g]); cn=wp(CONCERN[cs])
    p={"sid":"SYN"+hashlib.md5(str(i).encode()).hexdigest()[:10].upper(),
       "grade":g,"score_tier":wp(SCORE),"interest":random.choice(ax["interest"]),
       "career_stage":cs,"concern":cn,"region":wp(REGION),"special":wp(SPECIAL),"sex":random.choice(["남","여"])}
    out.append(p)
    combos.add(tuple(p[k] for k in ("grade","score_tier","interest","career_stage","concern","region","special","sex")))
with open("personas_v3.jsonl","w") as f:
    for p in out: f.write(json.dumps(p,ensure_ascii=False)+"\n")
print(f"=== personas_v3.jsonl: 총 {len(out):,}명 / 고유 속성조합 {len(combos):,}개 (name제거) ===")
print()
print("[현실성] grade x career_stage (%)")
gc={g:Counter() for g in ax["grade"]}
for p in out: gc[p["grade"]][p["career_stage"]]+=1
print("       "+" ".join(f"{c[:5]:>7}" for c in ax["career_stage"]))
for g in ax["grade"]:
    t=sum(gc[g].values()); print(f"{g:>4} | "+" ".join(f"{100*gc[g][c]/t:6.0f}" for c in ax["career_stage"]))
print()
def dist(key,order): return {k:round(100*sum(1 for p in out if p[key]==k)/len(out)) for k in order}
print("[score_tier %]", dist("score_tier",ax["score_tier"]))
print("[region %]    ", dist("region",list(REGION)))
print("[special %]   ", dist("special",list(SPECIAL)))
