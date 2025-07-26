import os
import json
import pandas as pd
from pathlib import Path

EXPERIMENTS_DIR = Path("experiments")
OUTPUT_FILENAME = "verification_manual_template.xlsx"
MAX_DIALOGS = 5  # Solo 5 diálogos por variante

def process_variant(variant_path):
    gen_dir = variant_path / "generated_dialogs"
    spec_dir = variant_path / "specifications"
    output = []

    dialog_files = sorted(gen_dir.glob("dialog_*_gen.txt"))[:MAX_DIALOGS]

    for gen_file in dialog_files:
        dialog_id = gen_file.stem.replace("_gen", "")
        try:
            dialog_text = gen_file.read_text().strip()
            spec_path = spec_dir / f"{dialog_id}_spec.json"
            spec_json = json.loads(spec_path.read_text()) if spec_path.exists() else {}

            row = {
                "Dialog ID": dialog_id,
                "Generated Dialog": dialog_text,
                "Specification": json.dumps(spec_json, indent=2),
                "Topic": "",
                "Subplot": "",
                "Imperfections": "",
                "Prompt Type":"",
                "Overall": ""
            }

            output.append(row)

        except Exception as e:
            print(f"❌ Error processing {dialog_id}: {e}")

    return output

def main():
    for model_dir in EXPERIMENTS_DIR.glob("llama3_*"):
        for category in model_dir.glob("*"):
            for variant in category.glob("*"):
                print(f"📄 Generating editable .xlsx for manual eval: {variant.relative_to(EXPERIMENTS_DIR)}")
                results = process_variant(variant)
                if results:
                    df = pd.DataFrame(results)
                    out_path = variant / OUTPUT_FILENAME
                    df.to_excel(out_path, index=False)
                    print(f"✅ Saved: {out_path}")
                else:
                    print("⚠️ No dialogs found in this variant.")

if __name__ == "__main__":
    main()
