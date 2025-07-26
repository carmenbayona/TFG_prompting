import json
from pathlib import Path
import pandas as pd

# Directorios
BASE_DIR = Path("experiments")
RESULTS_DIR = Path("results_excel/experiment4")
RESULTS_DIR.mkdir(exist_ok=True)

# Recoger todos los *_scores_*.json dentro de "ablation_outputs"
score_files = []
for path in BASE_DIR.rglob("*_scores_*.json"):
    if path.parent.name == "ablation_outputs":
        score_files.append(path)

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

    # Ejemplo: v1_scores_02.json
    stem_parts = score_path.stem.split("_")
    if len(stem_parts) == 3:
        # v1_scores_02
        prefix = stem_parts[0]   # v1
        number = stem_parts[2]   # 02
        version_number = f"{prefix}_{number}"
        dialog_filename = f"{prefix}_dialog_{number}.txt"
    else:
        # fallback por si el nombre no tiene 3 partes
        version_number = score_path.stem.replace("_scores", "")
        dialog_filename = f"{version_number}_dialog.txt"

    dialog_path = score_path.parent / dialog_filename

    try:
        with open(dialog_path, "r", encoding="utf-8") as f:
            dialog_text = f.read()
    except FileNotFoundError:
        dialog_text = "[Missing]"

    row = {
        "Model": parts[1],            # llama3_8b o llama3_70b
        "Axis": parts[2],             # tone / rol / subplot
        "Spec Type": parts[3],        # humor / serious / etc
        "Prompt Version": version_number,
        "Generated Dialog": dialog_text.strip()
    }
    # Añadir solo las columnas de puntuación + comentario
    for key in ["fluency", "coherence", "realism", "fidelity_to_specification",
                "engagement", "originality", "comments"]:
        row[key] = scores.get(key, "")

    rows.append(row)

# Guardar Excel
df = pd.DataFrame(rows)

# Ordenar para que queden agrupados
df = df.sort_values(by=["Model", "Axis", "Spec Type", "Prompt Version"])

output_path = RESULTS_DIR / "ablation_all_scores_5x_per_type.xlsx"
df.to_excel(output_path, index=False)

print(f"\n✅ Archivo Excel generado con {len(df)} filas: {output_path}")
