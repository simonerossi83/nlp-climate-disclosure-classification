The selected classical system gets **71.2%** of the **320** test paragraphs correct. Its balanced score (macro F1) is **0.660**, compared with **0.225** for always choosing the most common training label. It finds **80.2%** of labelled risk paragraphs.

The most frequent classical disagreement is **opportunity → neutral** (29 paragraphs). The saved examples show what needs analyst attention. Agreement with these labels is a useful test, but cannot establish accuracy on new companies or years.

The validation-selected review policy retains **0.0%** and sends **100.0%** to people. No threshold met all validation gates, so the policy correctly requires review for every paragraph.

The prespecified transformer seed changes balanced score by **+0.060** (95% paired interval **+0.006 to +0.114**). Interpret this alongside the corrected/new-error examples and hardware costs.
