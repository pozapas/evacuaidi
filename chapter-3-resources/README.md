# Chapter 3 resources

Supplementary materials for **"Causal-Knowledge-Guided AI for Evacuation Simulation: A
Framework for Standards-Compliant Input Generation"**, Transportation Research Part D:
Transport and Environment, manuscript TRD-D-26-02006.

Amir Rafe (Texas State University, Ingram School of Engineering) and Patrick A. Singleton
(Utah State University, Department of Civil and Environmental Engineering).

---

## What the paper does

The framework converts fire-safety regulations and engineering handbooks into the
parameter set an evacuation simulation needs: occupant load, walking speed,
pre-evacuation delay, and exit choice. It combines document parsing, a fine-tuned
Gemma 3 (4B) model, a Neo4j knowledge graph with graph-based retrieval, and a
causal-knowledge module that constrains inference of parameters the documents do not
state. The generated input file is executed in the Evacuationz simulator and compared
against an expert-configured baseline.

## Contents

| Item | Description |
|---|---|
| `Sources.csv` | The regulatory and handbook sources used for knowledge extraction |
| `Prompts.zip` | Structured prompt templates for causal-knowledge-guided parameter inference |
| `RAG_demo.mp4` | Demonstration of the retrieval system |
| `figures/` | Figures 2 and 9 of the paper at full resolution, for reading at magnification |
| `data/TRD-D-26-02006_supplementary_data.xlsx` | Every quantitative result behind the paper, with a data dictionary |
| `data/bm25_summary.csv`, `data/bm25_precision_recall_f1.csv` | The keyword-retrieval baseline reported in Table 10 |

### The supplementary workbook

Thirteen sheets, each documented in place, with an overview sheet and a data dictionary:

- **Evacuationz_TET** and **Evacuationz_Summary**: per-iteration total evacuation time for
  both scenarios (100 iterations each), summary statistics, exit usage shares, the
  congestion record, and the sensitivity sweeps.
- **Causal_Ablation**: all 42 blind expert ratings behind the with/without comparison,
  plus the cell means and the reliability statistics.
- **MOS_Framework_Outputs**: the per-expert ratings behind the agreement statistics.
- **Retrieval_Comparison**: F1 by question category for every system on the single fixed
  graph, including the dense, keyword, and no-retrieval baselines.
- **Stability**, **MultiHop**: the repeat-query proportions with Wilson intervals, and all
  30 held-out prompts with their reference sources and the per-model outcome grid.
- **FineTuning_Scores**, **Configuration**, **Dataset_QC**, **Expert_Panel**: absolute
  scores, the configuration as executed, corpus composition and audit, and the panel.

## Released artifacts on Hugging Face

| Artifact | Link |
|---|---|
| Fine-tuned model | https://huggingface.co/pozapas/gemma-3-evacuation |
| Q&A dataset | https://huggingface.co/datasets/pozapas/evacuation-safety-qa |

The model card reports the training configuration in full: LoRA rank 16 over a 4-bit
Gemma 3 (4B) base, one epoch over 20,968 examples, seed 42. The dataset card reports the
corpus composition and the 90/10 split.

## What is not released, and why

The case-study building geometry and the Evacuationz scenario files are not included. The
case study is a real university facility, and its floor geometry is not ours to publish.
Every result derived from those runs is released in full in the workbook, so the reported
numbers can be checked even though the geometry cannot be redistributed.

## Reproducing the figures

Figures 11 and 12 of the paper are generated directly from the Evacuationz sheets. The
plotting script and the figure style are given in the manuscript source package.

## Citation

```bibtex
@article{rafe2026causal,
  author  = {Rafe, Amir and Singleton, Patrick A.},
  title   = {Causal-Knowledge-Guided {AI} for Evacuation Simulation:
             A Framework for Standards-Compliant Input Generation},
  journal = {Transportation Research Part D: Transport and Environment},
  year    = {2026},
  note    = {Manuscript TRD-D-26-02006}
}
```

## Licence

CC BY-NC-SA 4.0, matching the released model and dataset.

## Contact

Amir Rafe, amir.rafe@txstate.edu
