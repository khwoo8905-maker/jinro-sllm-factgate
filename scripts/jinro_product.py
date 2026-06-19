# 진로상담 제품: 학생질문→커리어넷검색→LoRA생성→v4 의미게이트(강건파서+근거검증)→근거답변/정직폴백
import json, re, numpy as np, requests
from unsloth import FastLanguageModel
AD="jinro_lora_clean"; EMBED="http://localhost:8081/embed"; TH=0.82
DOCS=json.load(open("careernet_docs.json"))
DT=[d if isinstance(d,str) else (d.get("text") or json.dumps(d,ensure_ascii=False)) for d in DOCS]
VECS=np.load("careernet_vectors_kure.npy")
model,tok=FastLanguageModel.from_pretrained(AD,max_seq_length=4096,dtype=None,load_in_4bit=False)
FastLanguageModel.for_inference(model)
def embed(t): return np.array(requests.post(EMBED,json={"texts":t},timeout=60).json()["embeddings"])
def retrieve(q,k=6): qv=embed([q])[0]; return [DT[i] for i in np.argsort(-(VECS@qv))[:k]]
def norm(s): return re.sub(r"\s+","",s)
MAJ=re.compile(r"[가-힣A-Za-z]+(?:학과|학부|전공|계열|공학)")
BLK=re.compile(r"^\s*(#{2,}\s|\*{0,2}\d+[.)]\s|\*\*추천)")
def docmajors(docs):
    s=set()
    for d in docs:
        for m in MAJ.findall(d):
            if 2<=len(m)<=20: s.add(m)
    return sorted(s)
SYS="너는 한국 고등학생 진로·학과 상담 교사 보조 도구다. 제공된 [진로문서] 근거로만 참고 학과·진로 2~3개를 제시하고 각 근거를 든다. 과장·합격보장 금지."
FB="제공된 진로정보로는 확신할 학과를 특정하기 어렵습니다. 진로전담교사와 상담을 권합니다."
def consult(profile,q):
    docs=retrieve(profile+" "+q,6); ctx="\n".join(f"- {t[:300]}" for t in docs)
    user=f"[학생]\n{profile}\n질문: {q}\n\n[진로문서(근거로만 사용)]\n{ctx}"
    msgs=[{"role":"system","content":[{"type":"text","text":SYS}]},{"role":"user","content":[{"type":"text","text":user}]}]
    enc=tok.apply_chat_template(msgs,tokenize=True,add_generation_prompt=True,return_tensors="pt",return_dict=True,enable_thinking=False).to("cuda")
    raw=tok.decode(model.generate(**enc,max_new_tokens=600,temperature=0.7,do_sample=True)[0][enc["input_ids"].shape[1]:],skip_special_tokens=True)
    dm=docmajors(docs); dmn=[norm(x) for x in dm]; dmv=embed(dm) if dm else None; cache={}
    def gr(m):
        if any(norm(m) in d or d in norm(m) for d in dmn): return True
        if dmv is None: return False
        if m not in cache: cache[m]=float(np.max(dmv@embed([m])[0]))
        return cache[m]>=TH
    def recmajors(bl):
        t=[l for l in bl if BLK.match(l) or ("추천" in l and ("학과" in l or "전공" in l))]
        o=[]
        for l in t: o+=MAJ.findall(l)
        return list(dict.fromkeys(o))
    lines=raw.split("\n"); hdr=[i for i,l in enumerate(lines) if BLK.match(l)]
    if not hdr: return FB,0,[]
    b=hdr+[len(lines)]; kept=lines[:hdr[0]]; g=0; drop=[]
    for j in range(len(hdr)):
        blk=lines[b[j]:b[j+1]]; rms=recmajors(blk)
        if not rms: kept+=blk; continue
        if all(gr(m) for m in rms): kept+=blk; g+=1
        else: drop+=[m for m in rms if not gr(m)]
    return ("\n".join(kept).strip() if g>=1 else FB), g, drop
for prof,q in [("고3 남학생, 성적 상위, 흥미: 사회·상경, 성향: 리더십, 희망: 외교관","어떤 학과가 좋을까요?"),
               ("고2 남학생, 성적 중상위, 흥미: 공학·IT, 성향: 분석적, 희망: 인공지능 개발자","맞는 학과는?")]:
    a,g,d=consult(prof,q); print("="*60); print("[학생]",prof); print(f"[게이트] 근거블록 {g} / 제거 {d or 0}"); print(a[:420],flush=True)
print("[FINAL product ok]",flush=True)
