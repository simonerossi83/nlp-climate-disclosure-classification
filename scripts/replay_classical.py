"""Reproduce the reported classical predictions using its retained fitted pipeline."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
parser=argparse.ArgumentParser()
parser.add_argument('--run',type=Path,required=True)
parser.add_argument('--refit',action='store_true',help='Refit on the saved training rows with the saved training-only vocabulary to eliminate frequency-cutoff ties.')
args=parser.parse_args()
model=joblib.load(args.run/'models/classical.joblib')
saved=pd.read_csv(args.run/'predictions/selected_classical.csv')
import re
def clean(text):return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',text)).strip()
if args.refit:
    from sklearn.base import clone
    splits=pd.read_csv(args.run/'split_manifest.csv')
    row_ids=splits.loc[splits.split=='train','row_id'].str.split(':').str[-1].astype(int)
    source=pd.read_parquet(next((args.run/'data').glob('train-*.parquet'))).iloc[row_ids]
    vocabulary=dict(model[0].vocabulary_)
    model=clone(model).set_params(vectorizer__vocabulary=vocabulary)
    model.fit(source.text.map(clean),source.label)
probs=model.predict_proba(saved.text.map(clean))
expected=saved[['p_risk','p_neutral','p_opportunity']].to_numpy()
assert np.array_equal(probs.argmax(1),saved.prediction.to_numpy()), 'Predictions differ'
assert np.allclose(probs,expected,rtol=1e-7,atol=1e-8), 'Probability values differ beyond numerical tolerance'
print(f'Replayed all {len(saved)} reported classical predictions; probabilities agree within tolerance.')
