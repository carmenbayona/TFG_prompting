import os
import json
import pandas as pd
from pathlib import Path
from dialog_evaluator import DialogEvaluator

# === Base paths ===
BASE = Path.cwd()
EXPERIMENTS_DIR = BASE / "experiments"
PROMPT_EVAL = BASE / "prompts" / "prompt_evaluate_strict.txt"

# === Model folders and fixed model names ===
MODELS = {
    "llama3_8b": "llama3-8b-8192",
    "llama3_70b": "llama3-70b-8192"
}

print(f" Model folders found: {list(MODELS.keys())}")

for folder_name, model_name in MODELS.items():
    model_path = EXPERIMENTS_DIR / folder_name
    if not model_path.exists():
        print(f" Skipping missing model folder: {model_path}")
        continue

    print(f"\n Evaluating model: {model_name}")

    evaluator = DialogEvaluator(model_name=model_name, backend="groq")

    for category_dir in sorted(model_path.glob("*")):  # tone, rol, subplot
        if not category_dir.is_dir():
            continue
        print(f"📁 Category: {category_dir.name}")

        for variant_dir in sorted(category_dir.glob("*")):  # tone_humor, rol_friends...
            if not variant_dir.is_dir():
                continue

            print(f"\n Evaluating variant: {variant_dir.relative_to(BASE)}")

            # Crear subcarpetas si no existen
            for subfolder in ["generated_dialogs", "specifications", "evaluated_dialogs", "specifications_failed"]:
                os.makedirs(variant_dir / subfolder, exist_ok=True)

            gen_dir = variant_dir / "generated_dialogs"
            spec_dir = variant_dir / "specifications"
            eval_dir = variant_dir / "evaluated_dialogs"

            print(f" Checking generated dialogs in: {gen_dir}")
            dialog_files = list(gen_dir.glob("dialog_*_gen.txt"))
            print(f" Dialog files found: {len(dialog_files)}")

            rows = []

            for gen_file in dialog_files:
                dialog_id = gen_file.stem.replace("_gen", "")
                try:
                    generated_dialog = gen_file.read_text().strip()
                    spec_path = spec_dir / f"{dialog_id}_spec.json"
                    spec_json = json.loads(spec_path.read_text()) if spec_path.exists() else {}

                    eval_result = evaluator.evaluate(
                        generated_dialog=generated_dialog,
                        specification=spec_json,
                        reference_dialog="",
                        prompt_path=PROMPT_EVAL
                    )

                    eval_json_path = eval_dir / f"{dialog_id}_eval.json"
                    with open(eval_json_path, "w", encoding="utf-8") as f:
                        json.dump(eval_result, f, indent=2)

                    row = {
                        "ID": dialog_id,
                        "Generated Dialog": generated_dialog,
                        "Specification": json.dumps(spec_json, indent=2),
                        "Fluency (auto)": eval_result.get("fluency", ""),
                        "Coherence (auto)": eval_result.get("coherence", ""),
                        "Realism (auto)": eval_result.get("realism", ""),
                        "Fidelity (auto)": eval_result.get("fidelity_to_specification", ""),
                        "Engagement (auto)": eval_result.get("engagement", ""),
                        "Originality (auto)": eval_result.get("originality", ""),
                        "Comments": eval_result.get("comments", "") 
                    }
                    rows.append(row)

                except Exception as e:
                    print(f"❌ Error evaluating {dialog_id}: {e}")

            if rows:
                df = pd.DataFrame(rows)
                out_xlsx = eval_dir / f"evaluation_full_{folder_name}_{variant_dir.name}.xlsx"

                df.to_excel(out_xlsx, index=False)
                print(f"✅ Saved Excel to: {out_xlsx}")
            else:
                print("⚠️ No dialogs evaluated in this variant.")

print(f"\n Evaluación finalizada.")
