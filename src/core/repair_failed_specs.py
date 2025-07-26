import os
import json
import re
from pathlib import Path

BASE = Path("experiments")  # Carpeta base

def try_repair(text):
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object found in text")
        block = text[start:end + 1]

        block = block.replace("“", '"').replace("”", '"').replace("’", "'")
        block = block.replace('\\"', '"').replace("\n", " ").strip()
        block = re.sub(r'\s+', ' ', block)
        block = re.sub(r'^[^{]*', '', block)
        block = re.sub(r'([{,]\s*)(\w+)\s*:', r'\1"\2":', block)

        if '"P1":' in block and '"P2":' in block and '"goals":' not in block:
            match_p1 = re.search(r'"P1"\s*:\s*"[^"]+"', block)
            match_p2 = re.search(r'"P2"\s*:\s*"[^"]+"', block)
            if match_p1 and match_p2:
                goals_block = f'"goals": {{ {match_p1.group()}, {match_p2.group()} }}'
                block = re.sub(match_p1.group(), '', block)
                block = re.sub(match_p2.group(), '', block)
                block = block.replace('"tone":', f'{goals_block}, "tone":')

        block = re.sub(r'(":[^,{}\[\]]+")(\s*"[\w_]+")', r'\1,\2', block)
        block = re.sub(r'"}\s*"', '"}, "', block)
        block = re.sub(r'("P2"\s*:\s*"[^"]+)"\s*(subplots)', r'\1, "\2"', block)
        block = re.sub(r'"(\w+)"\s*:\s*"([^"]+)"([^":{},\[\]]+)"', r'"\1": "\2\3"', block)
        block = re.sub(r'"(\w+):\s*"', r'"\1": "', block)
        block = re.sub(r",\s*([}\]])", r"\1", block)
        block = re.sub(r"\[\s*,", "[", block)
        block = re.sub(r",\s*]", "]", block)

        if block.count("{") > block.count("}"):
            block += "}" * (block.count("{") - block.count("}"))
        if block.count("[") > block.count("]"):
            block += "]" * (block.count("[") - block.count("]"))

        return json.loads(block)

    except Exception as e:
        print(f"❌ Reparación fallida:\n{block}\n---\n{e}")
        return None

# === Detectar carpetas con errores ===
folders_with_failures = BASE.glob("llama3_*/*/*/specifications_failed")

for failed_dir in folders_with_failures:
    print(f"\n🔍 Reparando: {failed_dir}")
    fixed_dir = failed_dir.parent / "specifications"
    fixed_dir.mkdir(exist_ok=True)

    total, success, failures = 0, 0, []

    for filename in os.listdir(failed_dir):
        if filename.endswith("_spec.txt"):
            total += 1
            path = failed_dir / filename
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            repaired = try_repair(content)
            if repaired:
                dialog_id = filename.split("_")[1]
                output_filename = f"dialog_{dialog_id}_spec.json"
                output_path = fixed_dir / output_filename
                with open(output_path, "w", encoding="utf-8") as out:
                    json.dump(repaired, out, indent=2)
                print(f"✅ Reparado: {output_filename}")
                success += 1
            else:
                failures.append(filename)

    print(f"➡️ Total: {total} | ✅ Éxitos: {success} | ❌ Fallos: {len(failures)}")
    if failures:
        print("🗂️ Archivos no reparados:")
        for f in failures:
            print(" -", f)
