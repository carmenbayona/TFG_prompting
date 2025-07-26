import json
from pathlib import Path
import pandas as pd

# Base de resultados
BASE_DIR = Path("experiments")
RESULTS_DIR = Path("results_excel/experiment4")
RESULTS_DIR.mkdir(exist_ok=True)

# Recoger todos los archivos *_scores.json
score_files = list(BASE_DIR.rglob("*_scores.json"))

rows = []
for score_path in score_files:
    try:
        with open(score_path, "r", encoding="utf-8") as f:
            scores = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo {score_path.name}: {e}")
        continue

    parts = score_path.parts
    if len(parts) < 6:
        continue  # Estructura inesperada

    version = score_path.stem.replace("_scores", "")
    dialog_path = score_path.parent / f"{version}_dialog.txt"

    try:
        with open(dialog_path, "r", encoding="utf-8") as f:
            dialog_text = f.read()
    except:
        dialog_text = "[Missing]"

    row = {
        "Model": parts[1],            # llama3_8b o llama3_70b
        "Axis": parts[2],             # tone / rol / subplot
        "Spec Type": parts[3],        # humor / serious / etc
        "Prompt Version": version,
        "Generated Dialog": dialog_text
    }
    row.update(scores)
    rows.append(row)

# Guardar a Excel
df = pd.DataFrame(rows)
output_path = RESULTS_DIR / "ablation_all_scores_2.xlsx"
df.to_excel(output_path, index=False)

print(f"✅ Archivo generado con diálogos: {output_path}")
