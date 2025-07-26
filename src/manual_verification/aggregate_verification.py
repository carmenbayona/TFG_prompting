import pandas as pd
from pathlib import Path

EXPERIMENTS_DIR = Path("results_excel/experiment3")
OUTPUT_PATH = Path("verification_summary.xlsx")

summary_rows = []

for xlsx_path in sorted(EXPERIMENTS_DIR.glob("*.xlsx")):
    try:
        df = pd.read_excel(xlsx_path)
        total = len(df)

        # Extraer metadata desde el nombre del archivo
        filename = xlsx_path.stem  # ej: evaluation_semantics_tone_humor_8b
        parts = filename.split("_")

        # Validación básica por si algún archivo no cumple formato
        if len(parts) < 5:
            print(f"⚠️ Nombre de archivo no válido: {filename}")
            continue

        category = parts[2]  # tone / rol / subplot
        variant = parts[3]   # humor / serious / ...
        model = parts[-1]    # 8b / 70b

        # Contar ticks verdes por columna
        topic_ok = df["Topic "].value_counts().get("✔️", 0)
        subplot_ok = df["Subplot "].value_counts().get("✔️", 0)
        imperfections_ok = df["Imperfections "].value_counts().get("✔️", 0)
        overall_ok = df["Overall"].value_counts().get("✔️", 0)
        prompt_ok = df["Prompt Type"].value_counts().get("✔️", 0)

        row = {
            "Model": f"llama3_{model}",
            "Category": category,
            "Variant": variant,
            "Total Dialogs": total,
            "Topic (%)": round(100 * topic_ok / total, 1),
            "Subplot (%)": round(100 * subplot_ok / total, 1),
            "Imperfections (%)": round(100 * imperfections_ok / total, 1),
            "Prompt Type (%)": round(100 * prompt_ok / total, 1),
            "Overall (%)": round(100 * overall_ok / total, 1)
        }

        summary_rows.append(row)

    except Exception as e:
        print(f"⚠️ Error processing {xlsx_path.name}: {e}")

# Guardar resumen
if summary_rows:
    df_summary = pd.DataFrame(summary_rows)
    df_summary.sort_values(by=["Model", "Category", "Variant"], inplace=True)

    with pd.ExcelWriter(OUTPUT_PATH) as writer:
        df_summary.to_excel(writer, sheet_name="Per Variant", index=False)

    print(f"✅ Summary saved to {OUTPUT_PATH}")
    print(df_summary)
else:
    print("⚠️ No verification XLSX files found.")
