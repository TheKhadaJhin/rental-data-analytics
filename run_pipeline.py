"""Run the complete synthetic rental analytics workflow."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def run(script_name: str) -> None:
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "src" / script_name)],
        cwd=PROJECT_ROOT,
        check=True,
    )


def main() -> None:
    run("generate_sample_data.py")
    run("load_data.py")
    run("run_analysis.py")
    print("Pipeline completed successfully. Open reports/ to review the results.")


if __name__ == "__main__":
    main()
