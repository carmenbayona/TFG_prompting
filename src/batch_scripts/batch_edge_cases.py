import os
import json
from pathlib import Path
from dialog_generator import DialogGenerator
from dialog_evaluator import DialogEvaluator
import pandas as pd

# Configuración común
BACKEND = "groq"
PROMPT_DIR = "prompts_variants/edge_cases"
EVAL_PROMPT_PATH = "prompts/prompt_evaluate_strict_refined.txt"
RESULT_EXCEL_PATH = "results_excel/experiment6/results_edge_cases.xlsx"

# Diccionario modelo: carpeta
MODELS = {
    "llama3-8b-8192": "llama3_8b",
    "llama3-70b-8192": "llama3_70b"
}

# DataFrame resultados total
all_results = []

for model_name, folder_name in MODELS.items():
    print(f"\n🔵 Processing model: {model_name}")

    # Paths por modelo
    SPEC_DIR = f"experiments/{folder_name}/edge_cases/specs"
    OUTPUT_BASE_DIR = f"experiments/{folder_name}/edge_cases/outputs"
    OUTPUT_DIALOGS_DIR = os.path.join(OUTPUT_BASE_DIR, "dialogs")
    OUTPUT_EVALS_DIR = os.path.join(OUTPUT_BASE_DIR, "evaluations")

    # Crear carpetas si no existen
    Path(OUTPUT_DIALOGS_DIR).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_EVALS_DIR).mkdir(parents=True, exist_ok=True)

    # Inicializar generador y evaluador
    generator = DialogGenerator(
        backend=BACKEND,
        model_name=model_name
    )

    evaluator = DialogEvaluator(
        backend=BACKEND,
        model_name=model_name
    )

    # Listar specs
    spec_files = sorted([f for f in os.listdir(SPEC_DIR) if f.endswith(".json")])

    # Resultados por modelo
    model_results = []

    for version in ["v3", "v4"]:
        prompt_path = os.path.join(PROMPT_DIR, f"generate_dialog_{version}.txt")

        for spec_file in spec_files:
            spec_path = os.path.join(SPEC_DIR, spec_file)
            with open(spec_path, "r") as sf:
                spec_content = json.load(sf)
            spec_name = spec_file.replace(".json", "")

            for run in range(1, 4):
                print(f"⏳ Generating: {model_name}, {spec_name}, {version}, run {run}")

                # Generar diálogo
                dialog_text = generator.generate_dialog(
                    specification=json.dumps(spec_content, indent=2),
                    prompt_path=prompt_path
                )

                # Guardar diálogo .txt
                dialog_filename = f"{spec_name}_{version}_run{run}.txt"
                dialog_path = os.path.join(OUTPUT_DIALOGS_DIR, dialog_filename)
                with open(dialog_path, "w", encoding="utf-8") as out_f:
                    out_f.write(dialog_text.strip())

                print(f"✅ Saved dialog: {dialog_filename}")

                # Evaluar diálogo
                eval_output = evaluator.evaluate(
                    generated_dialog=dialog_text.strip(),
                    reference_dialog=None,
                    specification=json.dumps(spec_content, indent=2),
                    prompt_path=EVAL_PROMPT_PATH
                )

                # Guardar evaluación raw
                eval_filename = f"{spec_name}_{version}_run{run}_eval.json"
                eval_path = os.path.join(OUTPUT_EVALS_DIR, eval_filename)
                with open(eval_path, "w", encoding="utf-8") as f:
                    json.dump(eval_output, f, indent=2)

                print(f"✅ Evaluated: {eval_filename}")

                # Añadir fila a resultados
                model_results.append({
                    "model": model_name,
                    "spec_name": spec_name,
                    "version": version,
                    "run": run,
                    "fluency": eval_output.get("fluency"),
                    "coherence": eval_output.get("coherence"),
                    "realism": eval_output.get("realism"),
                    "fidelity_to_specification": eval_output.get("fidelity_to_specification"),
                    "engagement": eval_output.get("engagement"),
                    "originality": eval_output.get("originality"),
                    "comments": eval_output.get("comments"),
                    "dialog_text": dialog_text.strip()
                })

    # Añadir resultados de este modelo al total
    all_results.extend(model_results)

# Guardar Excel único
df = pd.DataFrame(all_results)
Path("results_excel").mkdir(parents=True, exist_ok=True)
df.to_excel(RESULT_EXCEL_PATH, index=False)
print(f"\n✅ All results saved to {RESULT_EXCEL_PATH}")
