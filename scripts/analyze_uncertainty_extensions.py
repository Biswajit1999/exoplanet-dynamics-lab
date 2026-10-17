"""Emit reproducible synthetic uncertainty checks; not catalogue measurements."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from exodynamics.dynamics.uncertainty_extensions import example_summary  # noqa: E402


def main():
    result=example_summary()
    out=ROOT/'results'/'uncertainty_extensions'
    out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps({
        'provenance':'fixed-seed synthetic numerical validation; not a measured planetary system',
        'assumptions':'independent Gaussian errors for pair, local Gaussian delta method for Kepler',
        **result},indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
