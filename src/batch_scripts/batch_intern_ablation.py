import time
import json
import pandas as pd
from pathlib import Path
from dialog_generator import DialogGenerator
from dialog_evaluator import DialogEvaluator

# Configuración
MODEL = "llama3-8b-8192"
MODEL_KEY = "llama3_8b"
BACKEND = "groq"

BASE_PROMPT_DIR = Path("prompts_variants") / "tone" / "ablation_study"
OUTPUT_DIR = Path("experiments") / MODEL_KEY / "tone" / "tone_humor" / "ablation_outputs_v5_v8"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EVAL_PROMPT = Path("prompts") / "prompt_evaluate_strict_refined.txt"
VARIANTS = {
    "v5_no_instructions": "humor_v5.txt",
    "v6_no_example": "humor_v6.txt",
    "v7_no_imperfections": "humor_v7.txt",
    "v8_minimal_prompt": "humor_v8.txt"
}
N_DIALOGS = 5

SPEC ={
  "topic": "Booking a surprise trip",
  "turns": 8,
  "participants": ["P1", "P2"],
  "tone": {
    "P1": "cheerful",
    "P2": "playfully suspicious"
  },
  "goals": {
    "P1": "convince P2 to pack without giving away the destination",
    "P2": "figure out what's going on without spoiling the surprise"
  },
  "subplots": [
    "P2 keeps guessing increasingly absurd locations (like Antarctica or a llama farm)",
    "P1 drops small, vague hints that only confuse P2 more"
  ],
  "imperfections": [
    "P1 accidentally reveals one tiny detail about the weather there",
    "P2 jokes about past surprise plans that went hilariously wrong"
  ]
}

generator = DialogGenerator(model_name=MODEL, backend=BACKEND)
evaluator = DialogEvaluator(model_name=MODEL, backend=BACKEND)

records = []

for variant, prompt_file in VARIANTS.items():
    print(f"\n🔁 Running: {variant}")
    prompt_path = BASE_PROMPT_DIR / prompt_file

    for i in range(1, N_DIALOGS + 1):
        try:
            dialog = generator.generate_dialog(SPEC, prompt_path=str(prompt_path))
            dialog_filename = f"{variant}_dialog_{i:02}.txt"
            dialog_path = OUTPUT_DIR / dialog_filename
            dialog_path.write_text(dialog)

            scores = evaluator.evaluate(dialog, prompt_path=str(EVAL_PROMPT))
            scores["Variant"] = f"{variant}_{i:02}"
            scores["Dialog"] = dialog
            scores["Specification"] = json.dumps(SPEC, indent=2)

            # Guardar también los JSON individualmente
            score_path = OUTPUT_DIR / f"{variant}_scores_{i:02}.json"
            with open(score_path, "w") as f:
                json.dump(scores, f, indent=2)

            records.append(scores)
            print(f"✅ Saved {dialog_filename} + scores")
            time.sleep(1.5)
        except Exception as e:
            print(f"❌ Error on {variant} [{i}]: {e}")

# Crear Excel final
if records:
    df = pd.DataFrame(records)
    cols = ["Variant", "Dialog", "Specification"] + [c for c in df.columns if c not in ["Variant", "Dialog", "Specification"]]
    df = df[cols]

    excel_dir = Path("results_excel/experiment5")
    excel_dir.mkdir(exist_ok=True)
    excel_path = excel_dir / "ablation_v5_v8_results.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"\n Excel created at: {excel_path}")
else:
    print("\n⚠️ No dialogs were generated or evaluated.")
