"""Execute the notebook from a clean kernel and preserve a failed run for diagnosis."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import nbformat
from nbclient import NotebookClient

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['review', 'baseline', 'auto', 'full'], default='review')
parser.add_argument('--config', type=Path)
parser.add_argument('--timeout', type=int, default=3600, help='Per-cell timeout in seconds')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
(root / 'artifacts').mkdir(exist_ok=True)
path = root / 'NLP_Simone_Rossi.ipynb'
notebook = nbformat.read(path, as_version=4)
nbformat.validate(notebook)
os.environ['NLP_RUN_MODE'] = args.mode
os.environ['PYTHONHASHSEED'] = '42'
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ['MPLBACKEND'] = 'Agg'
if args.config:
    os.environ['NLP_CONFIG_PATH'] = str(args.config.resolve())
# Use the interpreter running this script, rather than an unrelated registered kernel.
with tempfile.TemporaryDirectory(prefix='nlp-jupyter-') as directory:
    kernel = Path(directory) / 'kernels' / 'nlp-audit'
    kernel.mkdir(parents=True)
    (kernel / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'NLP audit isolated execution', 'language': 'python'}))
    previous = os.environ.get('JUPYTER_PATH')
    os.environ['JUPYTER_PATH'] = directory + (os.pathsep + previous if previous else '')
    os.environ['IPYTHONDIR'] = str(Path(directory) / 'ipython')
    os.environ['JUPYTER_RUNTIME_DIR'] = str(Path(directory) / 'runtime')
    try:
        NotebookClient(notebook, timeout=args.timeout, kernel_name='nlp-audit',
                       resources={'metadata': {'path': str(root)}}).execute()
    except Exception:
        nbformat.write(notebook, root / 'artifacts' / 'failed_execution.ipynb')
        raise
    else:
        # Keep a portable generic kernel name after validation.
        notebook.metadata.kernelspec = {'name':'python3','display_name':'Python 3 (ipykernel)','language':'python'}
        nbformat.write(notebook, path)
        print(f'Executed {path.name} successfully in {args.mode} mode.')
