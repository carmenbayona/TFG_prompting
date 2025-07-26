import json
from pathlib import Path
from dialog_generator import DialogGenerator
from dialog_evaluator import DialogEvaluator

# Ejes y tipos
EXPERIMENTS = {
    "tone": ["humor", "serious"],
    "rol": ["friends", "student_professor"],
    "subplot": ["with_subplot", "without_subplot"]
}

MODELS = {
    "llama3_8b": "llama3-8b-8192",
    "llama3_70b": "llama3-70b-8192"
}

PROMPT_BASE_DIR = Path("prompts_variants")
OUTPUT_BASE_DIR = Path("experiments")
STRICT_EVAL_PROMPT = Path("prompts") / "prompt_evaluate_strict_refined.txt"

# Especificaciones de ejemplo
SPEC_EXAMPLES = {
    "tone": {
        "humor": {
            "topic": "Booking a surprise trip",
            "turns": 8,
            "participants": 2,
            "tone": {"P1": "enthusiastic", "P2": "suspicious"},
            "goals": {
                "P1": "convince P2 to pack a bag without asking too many questions",
                "P2": "understand what's going on and get more info"
            },
            "subplots": [
                "P1 struggles to keep the destination secret",
                "P2 thinks it's a prank or a kidnapping"
            ],
            "imperfections": [
                "P1 slips a hint by accident",
                "P2 repeats questions and gets more paranoid"
            ]
        },
        "serious": {
            "topic": "Discussing exam results",
            "turns": 6,
            "participants": 2,
            "tone": {"P1": "worried", "P2": "calm"},
            "goals": {
                "P1": "understand why they failed",
                "P2": "comfort and support P1"
            },
            "subplots": ["They talk about repeating the course"],
            "imperfections": ["P1 interrupts P2", "P1 changes topic out of stress"]
        }
    },
    "rol": {
        "friends": {
            "topic": "Planning a weekend trip",
            "turns": 6,
            "participants": 2,
            "tone": {"P1": "excited", "P2": "skeptical"},
            "goals": {
                "P1": "convince P2 to join",
                "P2": "get more information before agreeing"
            },
            "subplots": ["P2 has a family commitment"],
            "imperfections": ["P2 changes their mind mid-dialog"]
        },
        "student_professor": {
            "topic": "Asking for deadline extension",
            "turns": 6,
            "participants": 2,
            "tone": {"P1": "nervous", "P2": "firm"},
            "goals": {
                "P1": "get an extension",
                "P2": "decide based on reasoning"
            },
            "subplots": ["P1 mentions personal problems"],
            "imperfections": ["P1 stutters", "P2 asks to clarify"]
        }
    },
    "subplot": {
        "with_subplot": {
            "topic": "Returning a borrowed item",
            "turns": 6,
            "participants": 2,
            "tone": {"P1": "apologetic", "P2": "annoyed"},
            "goals": {
                "P1": "return the item and apologize",
                "P2": "express disappointment"
            },
            "subplots": ["P2 brings up a previous similar incident"],
            "imperfections": ["P1 gives excuses", "P2 repeats themselves"]
        },
        "without_subplot": {
            "topic": "Ordering lunch",
            "turns": 4,
            "participants": 2,
            "tone": {"P1": "hungry", "P2": "indecisive"},
            "goals": {
                "P1": "decide quickly",
                "P2": "ask for recommendations"
            },
            "subplots": [],
            "imperfections": ["P2 changes mind mid-line"]
        }
    }
}

# Lanzador principal
for model_key, model_name in MODELS.items():
    generator = DialogGenerator(backend="groq", model_name=model_name)
    evaluator = DialogEvaluator(model_name=model_name, backend="groq")

    for axis, spec_types in EXPERIMENTS.items():
        for spec_type in spec_types:
            specification = SPEC_EXAMPLES[axis][spec_type]

            if axis == "tone":
                spec_folder = f"tone_{spec_type}"
            elif axis == "rol":
                spec_folder = f"rol_{spec_type}"
            else:
                spec_folder = spec_type

            for version in ["v1", "v2", "v3", "v4"]:
                print(f"\n Model: {model_key} | Axis: {axis} | Spec: {spec_type} | Version: {version}")

                prompt_path = PROMPT_BASE_DIR / axis / "ablation_study" / f"{spec_type}_{version}.txt"
                dialog = generator.generate_dialog(specification, prompt_path=str(prompt_path))

                output_dir = OUTPUT_BASE_DIR / model_key / axis / spec_folder / "ablation_outputs"
                output_dir.mkdir(parents=True, exist_ok=True)

                dialog_path = output_dir / f"{version}_dialog.txt"
                with open(dialog_path, "w", encoding="utf-8") as f:
                    f.write(dialog)

                # Evaluación estricta
                scores = evaluator.evaluate(dialog, prompt_path=str(STRICT_EVAL_PROMPT))
                print(f"📊 Scores: {scores}")

                score_path = output_dir / f"{version}_scores.json"
                with open(score_path, "w") as f:
                    json.dump(scores, f, indent=2)
