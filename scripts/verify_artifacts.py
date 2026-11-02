"""Verify saved-file integrity and independently reconstruct the reported test metrics."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import nbformat

parser = argparse.ArgumentParser()
parser.add_argument('--run', type=Path)
parser.add_argument('--require-all-files', action='store_true', help='Also require transformer tensors to be present locally.')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
run = args.run or Path(json.loads((root/'artifacts/latest_run.json').read_text())['path'])
if not run.is_absolute():
    run = root / run
manifest = json.loads((run/'manifest.json').read_text())
collection_path=run/'collection_status.json'
collection=json.loads(collection_path.read_text()) if collection_path.exists() else {}
remote_only=set(collection.get('remote_only_files',[]))
checked,not_local=0,[]
for name, digest in manifest['sha256'].items():
    if not (run/name).exists():
        assert name in remote_only and not args.require_all_files, f'Missing file: {name}'
        not_local.append(name)
        continue
    with (run/name).open('rb') as stream:
        checksum=hashlib.file_digest(stream,'sha256').hexdigest()
    assert checksum == digest, name
    checked+=1
splits = pd.read_csv(run/'split_manifest.csv')
assert splits.row_id.is_unique
assert splits.groupby('text_key').split.nunique().max() == 1
reported = pd.read_csv(run/'tables/test_metrics.csv').set_index('model')
for name, row in reported.iterrows():
    import re
    key = re.sub(r'[^a-z0-9]+', '_', name.lower())
    p = pd.read_csv(run/'predictions'/f'{key}.csv')
    assert p.row_id.is_unique and len(p) == row.test_n
    assert p.row_id.tolist() == splits.loc[splits.split=='test', 'row_id'].tolist()
    counts = pd.crosstab(p.label, p.prediction).reindex(index=[0,1,2], columns=[0,1,2], fill_value=0).to_numpy()
    f1 = np.divide(2*counts.diagonal(), counts.sum(0)+counts.sum(1), out=np.zeros(3,dtype=float), where=(counts.sum(0)+counts.sum(1))!=0).mean()
    accuracy = np.trace(counts)/counts.sum()
    risk_recall = counts[0,0]/counts[0].sum()
    assert np.isclose(f1,row.macro_f1) and np.isclose(accuracy,row.accuracy)
    assert np.isclose(risk_recall,row.risk_recall)
    assert np.isclose(row.accuracy,row.micro_f1)
    assert np.allclose(p[['p_risk','p_neutral','p_opportunity']].sum(1),1,atol=1e-5)
nb = nbformat.read(root/'NLP_Simone_Rossi.ipynb', as_version=4)
nbformat.validate(nb)
for cell in nb.cells:
    if cell.cell_type=='code':
        compile(cell.source,'notebook cell','exec')
        assert cell.execution_count is not None
        assert not any(o.output_type=='error' for o in cell.outputs)
figures = sum('image/png' in o.get('data',{}) for c in nb.cells for o in c.get('outputs',[]))
assert figures >= 8, 'Expected explanatory chart outputs are missing'
print(f'Verified {checked} retained file hashes, {len(reported)} prediction tables and {figures} embedded charts.')
if not_local:
    print(f'{len(not_local)} explicitly catalogued transformer tensor files are remote-only and were not locally checked; see collection_status.json.')
print(json.loads((run/'completion.json').read_text())['status'])
