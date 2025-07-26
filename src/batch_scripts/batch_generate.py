import os
import json
import time
from dialog_generator import DialogGenerator

# Model identifiers and base folder names
MODELS = {
    "llama3-8b-8192": "experiments/llama3_8b",
    "llama3-70b-8192": "experiments/llama3_70b"
}

# Experiment configurations
EXPERIMENTS = [
    {
        "name": "tone",
        "variants": ["tone_serious", "tone_humor"],
        "prompt_dir": "prompts_variants/tone/",
        "spec_prompt_per_variant": True
    },
    {
        "name": "rol",
        "variants": ["rol_student_professor", "rol_friends"],
        "prompt_dir": "prompts_variants/rol/",
        "spec_prompt_per_variant": True
    },
    {
        "name": "subplot",
        "variants": ["with_subplot", "without_subplot"],
        "prompt_dir": "prompts_variants/subplot/",
        "spec_prompt_per_variant": True
    }
]

REAL_DIALOG_DIR = "data/real_dialogs"
real_dialogs = sorted(f for f in os.listdir(REAL_DIALOG_DIR) if f.endswith(".txt"))

def ensure_dirs(path):
    for sub in ["specifications", "evaluated_dialogs", "specifications_failed"]:
        os.makedirs(os.path.join(path, sub), exist_ok=True)

def is_rate_limit_error(e):
    try:
        err = json.loads(str(e).replace("'", '"'))
        return err.get("error", {}).get("code") == "rate_limit_exceeded"
    except:
        return False

def extract_wait_time(e):
    try:
        err = json.loads(str(e).replace("'", '"'))
        msg = err["error"]["message"]
        for part in msg.split():
            if part.endswith("s") and "m" in part:
                mins, secs = part.replace("s", "").split("m")
                return int(mins) * 60 + float(secs)
        return 90
    except:
        return 90

for model_name, base_id in MODELS.items():
    for exp in EXPERIMENTS:
        for variant in exp["variants"]:
            base_dir = os.path.join(base_id, exp["name"], variant)
            ensure_dirs(base_dir)

            prompt_dialog_path = os.path.join(exp["prompt_dir"], f"prompt_generate_dialog_{variant}.txt")
            prompt_spec_path = os.path.join(
                exp["prompt_dir"],
                f"prompt_generate_specification_{variant}.txt" if exp.get("spec_prompt_per_variant") else exp["spec_prompt"]
            )

            generator = DialogGenerator(model_name=model_name, backend="groq")

            for idx, filename in enumerate(real_dialogs, start=1):
                if idx > 15:
                    break

                dialog_id = f"dialog_{idx:03d}"

                while True:
                    try:
                        with open(os.path.join(REAL_DIALOG_DIR, filename), "r") as f:
                            real_dialog = f.read()

                        spec, raw_output = generator.generate_specification(
                            real_dialog,
                            prompt_path=prompt_spec_path,
                            base_dir=base_dir,
                            dialog_id=dialog_id
                        )

                        if spec is None:
                            raise ValueError("❌ Spec generation failed due to JSON parsing error.")

                        spec_path = os.path.join(base_dir, "specifications", f"{dialog_id}_spec.json")
                        with open(spec_path, "w") as f:
                            json.dump(spec, f, indent=2)

                        dialog = generator.generate_dialog(spec, prompt_path=prompt_dialog_path)
                        dialog_path = os.path.join(base_dir, "generated_dialogs", f"{dialog_id}_gen.txt")
                        with open(dialog_path, "w") as f:
                            f.write(dialog.strip())

                        print(f"✅ {dialog_id}_gen.txt generated for {model_name} | {exp['name']} | {variant}")
                        break  # ✅ Éxito → salimos del while

                    except Exception as e:
                        if is_rate_limit_error(e):
                            wait_time = extract_wait_time(e)
                            print(f"⏳ Rate limit hit. Waiting {wait_time:.1f} seconds before retry...")
                            time.sleep(wait_time + 2)
                            continue  # 🔁 Volvemos a intentar después de esperar

                        else:
                            print(f"❌ Failed to generate {dialog_id} ({variant}): {e}")
                            fail_dir = os.path.join(base_dir, "specifications_failed")
                            os.makedirs(fail_dir, exist_ok=True)
                            fail_path = os.path.join(fail_dir, f"{dialog_id}_spec.txt")
                            if 'raw_output' in locals() and raw_output:
                                try:
                                    with open(fail_path, "w", encoding="utf-8") as f:
                                        f.write(raw_output.strip())
                                    print(f"📁 Raw output saved to: {fail_path}")
                                except Exception:
                                    print("⚠️ Could not save failed output.")
                            break  # ❌ Otro tipo de error → salimos del while
