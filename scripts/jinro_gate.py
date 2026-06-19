# 진로 팩트게이트 v2 — 답변 추천학과가 [진로문서] 블록에 실제 있나 (문서만, strict)
import json, re
def norm(s): return re.sub(r"\s+","",s)
def docctx(msgs):  # 문서 블록만 (희망/프로필 제외)
    for m in msgs:
        if m["role"]!="assistant":
            i=m["content"].find("[진로문서")
            if i>=0: return norm(m["content"][i:])
    return norm(" ".join(m["content"] for m in msgs if m["role"]!="assistant"))
def recs(a):
    out=[]
    for ln in a.splitlines():
        m=re.match(r"\s*(?:#+\s*)?\*{0,2}\d+[.)]\s*\*{0,2}([^\n(*]+)", ln)
        if m: out.append(m.group(1).strip())
    return out
def toks(rec):
    t=[]
    for p in re.split(r"[/·,()\[\]]| 또는 | 및 | 등 ", rec):
        t+=re.findall(r"[가-힣A-Za-z]+(?:학과|학부|전공|사이언스|공학|디자인|학)", p.strip())
    return [x for x in t if len(x)>=2]
def judge(msgs):
    a=next((m["content"] for m in msgs if m["role"]=="assistant"),"")
    ctx=docctx(msgs); bad=[]
    for rec in recs(a)[:6]:
        tk=toks(rec)
        if tk and not any(norm(x) in ctx for x in tk): bad.append(rec[:30])
    return (len(bad)==0, bad)
for tag,src,dst in [("train","jinro_data/jinro_train.jsonl","jinro_data/jinro_train_clean.jsonl"),
                    ("valid","jinro_data/jinro_valid.jsonl","jinro_data/jinro_valid_clean.jsonl")]:
    rows=[json.loads(l) for l in open(src) if l.strip()]
    clean=[]; dirty=[]
    for r in rows:
        if not any(m["role"]=="assistant" for m in r["messages"]): continue
        ok,bad=judge(r["messages"]); (clean if ok else dirty).append((r,bad))
    with open(dst,"w") as f:
        for r,_ in clean:
            f.write(json.dumps({k:r[k] for k in ("sid","level","messages") if k in r},ensure_ascii=False)+"\n")
    n=len(clean)+len(dirty)
    print(f"=== {tag} N={n} → clean {len(clean)} ({100*len(clean)/n:.1f}%) / dirty {len(dirty)} → {dst}")
