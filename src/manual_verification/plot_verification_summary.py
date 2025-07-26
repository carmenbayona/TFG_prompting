import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Leer el resumen generado
SUMMARY_FILE = Path("verification_summary.xlsx")
df = pd.read_excel(SUMMARY_FILE)

# Carpeta donde guardar los plots
PLOTS_DIR = Path("plots/experiment3")
PLOTS_DIR.mkdir(exist_ok=True)

# Métricas que quieres visualizar
metrics = ["Topic (%)", "Subplot (%)", "Imperfections (%)", "Prompt Type (%)", "Overall (%)"]

for metric in metrics:
    plt.figure(figsize=(12, 6))
    for model in df["Model"].unique():
        subset = df[df["Model"] == model]
        x = subset["Variant"]
        y = subset[metric]
        plt.bar([f"{model}-{v}" for v in x], y, label=model)

    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 105)
    plt.title(f"{metric} by Variant and Model")
    plt.xlabel("Variant")
    plt.ylabel(metric)
    plt.legend()
    plt.tight_layout()

    out_path = PLOTS_DIR / f"plot_{metric.replace(' (%)','').replace(' ','_').lower()}.png"
    plt.savefig(out_path)
    print(f"✅ Saved plot: {out_path}")
    plt.close()
