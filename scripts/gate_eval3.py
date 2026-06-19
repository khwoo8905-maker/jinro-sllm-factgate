import json, re, numpy as np, requests
EMBED="http://localhost:8081/embed"; TH=0.82
data=json.load(open("dl_logs/gen50.json"))
def embed(t): return np.array(requests.post(EMBED,json={"texts":t},timeout=60).json()["embeddings"])
def norm(s): return re.sub(r"\s+","",s)
MAJ=re.compile(r"[가-힣A-Za-z]+(?:학과|학부|전공|계열|공학)")
BLK=re.compile(r"^\s*(#{2,}\s|\*{0,2}\d+[.)]\s|\*\*추천)")
def docmajors(docs):
    s=set()
    for d in docs:
        for m in MAJ.findall(d):
            if 2<=len(m)<=20: s.add(m)
    return sorted(s)
def recmajors(bl):
    t=[l for l in bl if BLK.match(l) or ("추천" in l and ("학과" in l or "전공" in l))]
    o=[]
    for l in t: o+=MAJ.findall(l)
    return list(dict.fromkeys(o))
blk_tot=blk_drop=ans_drop=fb=use=0
for it in data:
    docs=it["docs"]; dm=docmajors(docs); dmn=[norm(x) for x in dm]; dmv=embed(dm) if dm else None; cache={}
    def gr(m):
        if any(norm(m) in d or d in norm(m) for d in dmn): return True
        if dmv is None: return False
        if m not in cache: cache[m]=float(np.max(dmv@embed([m])[0]))
        return cache[m]>=TH
    lines=it["raw"].split("\n"); hdr=[i for i,l in enumerate(lines) if BLK.match(l)]; b=hdr+[len(lines)]
    if not hdr: fb+=1; continue
    g=0; dropped=0
    for j in range(len(hdr)):
        rms=recmajors(lines[b[j]:b[j+1]])
        if not rms: continue
        blk_tot+=1
        if all(gr(m) for m in rms): g+=1
        else: blk_drop+=1; dropped+=1
    if dropped: ans_drop+=1
    if g==0: fb+=1
    else: use+=1
print(f"추천 블록 총 {blk_tot} / 문서밖이라 드롭 {blk_drop} ({100*blk_drop/blk_tot:.0f}%)")
print(f"드롭이 일어난 답변 {ans_drop}/50 = {100*ans_drop/50:.0f}%  (게이트가 실제 일한 비율)")
print(f"폴백 {fb}/50 | 유효 {use}/50")
