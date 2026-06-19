# 진로 LoRA 평가 — valid(문서주입 RAG포맷) 생성 → 35b-a3b 채점
import json, requests, time, statistics
from unsloth import FastLanguageModel

M="jinro_lora_unsloth"; N=149
OLLAMA="http://localhost:11434/api/generate"; JUDGE="qwen3.6:35b-a3b"
rows=[json.loads(l) for l in open("jinro_data/jinro_valid.jsonl")][:N]
print(f"[load] LoRA 로딩...", flush=True); t=time.time()
model,tok=FastLanguageModel.from_pretrained(M,max_seq_length=4096,dtype=None,load_in_4bit=False)
FastLanguageModel.for_inference(model)
print(f"[load] {time.time()-t:.0f}s 완료. N={len(rows)}", flush=True)

def wrap(m): return {"role":m["role"],"content":[{"type":"text","text":m["content"]}]}
results=[]
for i,r in enumerate(rows):
    msgs=r["messages"]
    conv=[wrap(m) for m in msgs if m["role"]!="assistant"]
    user=next(m["content"] for m in msgs if m["role"]=="user")
    enc=tok.apply_chat_template(conv,tokenize=True,add_generation_prompt=True,return_tensors="pt",return_dict=True,enable_thinking=False).to("cuda")
    out=model.generate(**enc,max_new_tokens=800,temperature=0.7,do_sample=True)
    ans=tok.decode(out[0][enc["input_ids"].shape[1]:],skip_special_tokens=True)
    jp=("아래 진로상담 AI 답변을 채점하라. [진로문서]에만 근거했는지(근거충실), 학생 프로필 맞춤인지(맞춤성), "
        "과장/합격보장 없는지(안전헷지) 각 1~5점. 문서에 없는 사실을 지어냈으면 hallucination=true.\n"
        f"[입력]\n{user}\n\n[AI답변]\n{ans}\n\n"
        'JSON만: {"근거충실":n,"맞춤성":n,"안전헷지":n,"hallucination":bool,"한줄평":"..."}')
    try:
        jr=requests.post(OLLAMA,json={"model":JUDGE,"prompt":jp,"think":False,"format":"json","stream":False,"options":{"num_predict":300}},timeout=240).json()
        sc=json.loads(jr["response"])
    except Exception as e:
        sc={"err":str(e)[:80]}
    results.append({"sid":r["sid"],"score":sc,"ans":ans[:500]})
    print(f"[{i+1}/{len(rows)}] {r['sid']}: {sc}", flush=True)

def avg(k):
    v=[x["score"].get(k) for x in results if isinstance(x["score"].get(k),(int,float))]
    return round(statistics.mean(v),2) if v else None
hall=sum(1 for x in results if x["score"].get("hallucination") is True)
print("="*50,flush=True)
print(f"SUMMARY N={len(results)} | 근거충실={avg('근거충실')} 맞춤성={avg('맞춤성')} 안전헷지={avg('안전헷지')} | 할루시네이션={hall}/{len(results)}",flush=True)
json.dump(results,open("dl_logs/eval_jinro_full_result.json","w"),ensure_ascii=False,indent=2)
print("[done] 결과: ~/dl_logs/eval_jinro_full_result.json",flush=True)
