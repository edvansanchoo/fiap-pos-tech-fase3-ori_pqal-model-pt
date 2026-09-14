import json
import time
from pathlib import Path
from deep_translator import GoogleTranslator, MyMemoryTranslator

src = Path(r"C:\Users\edvan.sancho\OneDrive - Instituto de Pesquisas Eldorado\Documents\Estudos\pos\pqal_train.jsonl")
dst = Path(r"C:\Users\edvan.sancho\OneDrive - Instituto de Pesquisas Eldorado\Documents\Estudos\pos\pqal_train_pt-br.jsonl")

translators = [
    GoogleTranslator(source="en", target="pt"),
    MyMemoryTranslator(source="english us", target="portuguese brazil"),
    GoogleTranslator(source="auto", target="pt"),
]

start_from = 0
if dst.exists():
    with dst.open(encoding="utf-8") as f:
        start_from = sum(1 for _ in f)
    print(f"Retomando da entrada {start_from + 1}")


def translate_chunk(text):
    text = text.strip()
    if not text:
        return text
    text = text.replace("\ufffd", " ")
    last_error = None
    for tr in translators:
        for i in range(6):
            try:
                if len(text) <= 4500:
                    result = tr.translate(text)
                    if result and result.strip():
                        return result
                else:
                    parts = []
                    chunk = ""
                    for para in text.split("\n\n"):
                        if len(chunk) + len(para) + 2 <= 4500:
                            chunk = (chunk + "\n\n" + para) if chunk else para
                        else:
                            if chunk:
                                parts.append(translate_chunk(chunk))
                                time.sleep(0.15)
                            chunk = para
                    if chunk:
                        parts.append(translate_chunk(chunk))
                    return "\n\n".join(parts)
            except Exception as exc:
                last_error = exc
                time.sleep(min(20, 2 * (i + 1)))
    raise RuntimeError(f"Falha ao traduzir: {text[:120]}... ({last_error})")


with src.open(encoding="utf-8") as fin, dst.open("a", encoding="utf-8") as fout:
    for idx, line in enumerate(fin, 1):
        if idx <= start_from:
            continue
        obj = json.loads(line)
        inp = obj["input"]
        if "Pergunta: " in inp and "\n\nContexto:\n" in inp:
            q, ctx = inp.split("Pergunta: ", 1)[1].split("\n\nContexto:\n", 1)
            q_pt = translate_chunk(q)
            ctx_pt = translate_chunk(ctx)
            inp_pt = f"Pergunta: {q_pt}\n\nContexto:\n{ctx_pt}"
        else:
            inp_pt = translate_chunk(inp)

        out = obj["output"]
        if out.startswith("Resposta: ") and "\n\n" in out:
            ans, just = out.split("\n\n", 1)
            just_pt = translate_chunk(just)
            out_pt = f"{ans}\n\n{just_pt}"
        else:
            out_pt = translate_chunk(out)

        new_obj = {
            "instruction": obj["instruction"],
            "input": inp_pt,
            "output": out_pt,
        }
        fout.write(json.dumps(new_obj, ensure_ascii=False) + "\n")
        fout.flush()
        if idx % 25 == 0:
            print(f"Traduzidos: {idx}")
        time.sleep(0.1)

print("Concluido:", idx)
