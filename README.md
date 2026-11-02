# Climate disclosure classification

Open [NLP_Simone_Rossi.ipynb](NLP_Simone_Rossi.ipynb). It explains the task, the controlled model comparison, the missed quality target, five ranked error families, six explainability examples, class and slice performance gaps, stakeholder consequences, and technical/process safeguards.

The report's evidence is the controlled Colab run `20261102T152220909909Z_3d7d7c00a8`. Its primary comparison is classical macro F1 **0.6595** versus transformer seed 42 **0.7193**, with risk recall **0.8019 → 0.8585**. These values are reconstructed from the retained 320-row prediction files. The notebook explains why the observed score does not reach the proposed 0.80 gate and why human-led use is recommended. The threshold is a project assumption, not a universal safety standard.

## Reproduce this report without a GPU

Use Python 3.13 and an isolated environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_notebook.py --mode review
python scripts/verify_artifacts.py
```

Review mode executes the notebook from a clean kernel using the saved comparison's predictions, training histories, split IDs, selected classical pipeline, and recorded validation tables. It recomputes test metrics, bootstrap intervals, class/slice diagnostics, feature contributions, word-deletion sensitivity and figures. It does **not** train the transformer or make new transformer token-attribution claims. `NLP_REVIEW_RUN` selects a compatible saved run directory; the default is the controlled run named above.

`artifacts/latest_run.json` points to the generated evidence directory. Its `comparison_source.json` identifies the input experiment and its source-manifest hash. Its own `run_config.json`, environment snapshot and file checksums identify the review execution. Raw model-result records are kept separate from the report's additional diagnostics.

## Refit the reported classical model

```bash
python scripts/replay_classical.py --run artifacts/20261102T152220909909Z_3d7d7c00a8
python scripts/replay_classical.py --run artifacts/20261102T152220909909Z_3d7d7c00a8 --refit
```

The first command checks the retained fitted model against all reported predictions. The second refits using the recorded training rows and training-only vocabulary, avoiding a different selection among equally frequent words at the feature cutoff. Both routes have reproduced all 320 predictions and probability scores within numerical tolerance. Fixed seeds alone do not guarantee identical refits across platforms.

## Train an experiment on Colab

```bash
python -m pip install -r requirements-transformer.txt
python scripts/run_notebook.py --mode full
```

Full mode requires CUDA. The configuration fixes the data/model commits, 800/200 train/validation split, 320-row official test, three transformer seeds (42, 43, 44), maximum sequence length and other hyperparameters. Seed 42 is prespecified as the primary comparison; secondary seeds are not selected by their test score. Baseline mode fits classical candidates and skips transformer training. Optional POS profiling requires `requirements-pos.txt` and `NLP_RUN_POS=true`.

For VS Code, choose **Select Kernel → Colab → Auto Connect**, or create a GPU server. For browser Colab, upload the notebook, run its dependency bootstrap, restart if prompted, then Run all. [Google's extension instructions](https://marketplace.visualstudio.com/items?itemName=Google.colab). A standalone upload without the saved review directory trains/analyzes an experiment; the report's fixed numerical interpretations remain explicitly tied to the named controlled evidence run. Interpret a new experiment from its generated tables and decision, rather than assuming those fixed values apply.

## Explainability and evidence limits

The method is **exact logistic-regression class-contrast contributions plus word-deletion sensitivity**. It is applied to correct, incorrect, mixed-framing and heading-pair paragraphs. Its exact-margin assertions and full token/offset records are saved for inspection. Attention, LIME, SHAP and Integrated Gradients are not used. Transformer row-level changes and the heading-pair contrast are separate evidence; they do not reveal which transformer tokens internally caused a decision.

Protected demographic attributes and validated issuer/time grouping fields are absent. Class and wording-slice disparities are reported with support and limitations; they cannot establish demographic fairness. The five primary error families are exhaustive class-confusion counts; semantic mechanisms are hypotheses grounded in named examples. Proposed changes require development experiments and a fresh issuer/time holdout.

The transformer tensor files are not local. The saved source run's `collection_status.json` lists nine uncollected tensor/optimizer files and their expected hashes remain in its manifest. Their remote availability is unverified; a full GPU run regenerates them. Analytical review, saved prediction verification and classical explanations work with the retained local evidence. The artifact checker reports declared missing source-run tensors; `--require-all-files` enforces complete local retention when checking that source run.

## Data and intended use

[ClimateSentiment](https://huggingface.co/datasets/climatebert/climate_sentiment), by Bingler, Kraus, Leippold and Webersinke, contains labelled English corporate-disclosure paragraphs. The version-pinned source card and data checksums are in `data/`. Its labels are **risk, neutral and opportunity**. The source card specifies **CC-BY-NC-SA-4.0** and a contact for commercial use. The model classifies wording, not verified environmental performance, investment suitability or greenwashing.
