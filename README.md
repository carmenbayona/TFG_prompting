# Synthetic Dialogue Generation with LLMs – TFG

This repository contains the implementation of the Bachelor’s Thesis (TFG) titled:

**"Design and implementation of a system for synthetic conversation generation using LLMs and prompt engineering techniques"**  
Author: Carmen Bayona Sánchez – ETSIT-UPM (2025)

## Project Description

This project presents a complete and modular pipeline to **generate**, **evaluate**, and **analyze** synthetic conversations using Large Language Models (LLaMA 3 8B / 70B via Groq), combining:

- Prompt engineering (zero-shot, few-shot, enriched, ablation, edge-cases)
- Automatic and human evaluation
- JSON parsing and repair
- Batch experiment automation
- Metrics visualization and export

The system is fully automated and includes repair mechanisms for failed generations, a clear folder structure for tracking results, and scripts for exporting scores to Excel and plots.

## ️ Folder Structure

```
├── data/                     # Real dialogues used as input
├── prompts/                 # Base prompts for generation and evaluation
├── prompts_variants/       # Variants by tone, role, subplot, ablation, edge cases
├── experiments/            # Results from each experiment, organized by model and variant
├── results_excel/          # Consolidated metrics and human scores in Excel
├── plots/                  # Figures generated from results (barplots, boxplots, heatmaps...)
├── src/
│   ├── core/               # Main classes (DialogGenerator, DialogEvaluator, repair tool)
│   ├── batch_scripts/      # Scripts for experiments: ablation, edge cases, etc.
│   ├── manual_verification/ # Tools for human evaluation and aggregation
│   └── export_tools/       # Excel exporters for batch results
├── run_batch_experiments.ipynb  # Notebook for launching the full pipeline
├── requirements.txt
├── README.md
└── keys.env                # API keys (not uploaded to repo)
```

##  How to Run

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Set up your API key**  
Create a `.env` file or use `keys.env` with your Groq API key (or load models locally with `llama-cpp`).

3. **Run the full pipeline**

Use the notebook:

```bash
jupyter notebook run_batch_experiments.ipynb
```

Or launch specific experiments via scripts (from `src/batch_scripts/`):

```bash
python src/batch_scripts/batch_ablation.py
python src/batch_scripts/batch_edge_cases.py
```

4. **Export results to Excel**

```bash
python src/export_tools/export_ablation_results_to_excel.py
```

##  Highlights

- Supports generation with Groq API or local LLaMA models via `llama-cpp`
- Built-in automatic repair of malformed JSONs
- Modular prompt design with semantic control (tone, role, subplots)
- Internal ablation studies for prompt components
- Reproducible experiment pipeline

##  License

This repository is part of a Bachelor’s Thesis project and is shared for academic purposes.


##  Overview of the 6 Experiments

1. **Experiment 1 – Initial Pipeline Validation**  
   Tests the full system (specification → generation → evaluation) using 100 real dialogs with both LLaMA 3 8B and 70B. Ensures technical correctness and baseline outputs.

2. **Experiment 2 – Prompt Style Impact**  
   Compares three prompt styles (Vanilla, Few-shot, No Imperfections) using both automatic and manual evaluations on 120 generated dialogs. Assesses how prompt structure affects quality.

3. **Experiment 3 – Semantic Variant Comparison**  
   Tests whether the model can follow semantic attributes like tone (humorous/serious), role (friends/professor–student), or presence of a subplot. Involves human verification and strict evaluation prompts.

4. **Experiment 4 – Prompt Ablation Study (V1–V4)**  
   Uses fixed specifications and compares the effect of different prompt formulations (zero-shot, with rules, few-shot, no imperfections). Analyzes trade-offs in fidelity vs. creativity.

5. **Experiment 5 – Internal Prompt Component Ablation (V5–V8)**  
   Removes specific components (instructions, examples, imperfections) from the base prompt to measure their individual impact. All outputs generated with LLaMA 3 8B.

6. **Experiment 6 – Edge Case Performance**  
   Challenges the system with extreme specifications (long dialogues, contradictory tone, hidden subplots). Evaluates robustness and failure patterns using both models and v3 and v4 prompt variants.

