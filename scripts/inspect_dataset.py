"""
MSMARCO-XI Dataset Inspection Script — HH Goa 2026 Task 2
Loads a tiny streaming sample from ai4bharat/MSMARCO-XI and prints dataset schema,
sample fields, passage counts, and selected flags without downloading the full dataset.
"""

import sys
import json
import pyarrow.parquet as pq
from urllib.request import urlopen, Request

HF_BASE_URL = "https://huggingface.co/datasets/ai4bharat/MSMARCO-XI/resolve/main"

def inspect_via_pyarrow(config="hin", split="validation"):
    """Download and inspect small sample of parquet file directly via PyArrow."""
    file_path = f"{split}/{config}val.parquet" if split == "validation" else f"{split}/{config}train.parquet"
    url = f"{HF_BASE_URL}/{file_path}"
    print(f"  Fetching streaming schema for: {url}\n")

    try:
        # Fetch parquet file header via HTTP
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as response:
            # Read first 5MB for header + initial batch
            content = response.read(5 * 1024 * 1024)

        import io
        buffer = io.BytesIO(content)
        parquet_file = pq.ParquetFile(buffer)

        print("  ┌────────────────────────────────────────────────────────┐")
        print("  │            MSMARCO-XI DATASET INSPECTION               │")
        print("  └────────────────────────────────────────────────────────┘\n")
        print(f"  Dataset       : ai4bharat/MSMARCO-XI")
        print(f"  Configuration : {config}")
        print(f"  Split         : {split}")
        print(f"  Parquet File  : {file_path}")
        print(f"  Num Row Groups: {parquet_file.num_row_groups}")

        schema = parquet_file.schema
        print("\n  Column Names & Types:")
        for name in schema.names:
            print(f"    - {name}")

        # Read first row group
        table = parquet_file.read_row_group(0)
        pydict = table.to_pydict()

        print(f"\n  Inspecting Record #0:")
        keys = pydict.keys()
        for k in keys:
            val = pydict[k][0]
            if isinstance(val, list) and len(val) > 3:
                print(f"    - {k:25s}: List of {len(val)} items (Sample: {str(val[:2])}...)")
            elif isinstance(val, dict):
                print(f"    - {k:25s}: Dict with keys {list(val.keys())}")
            else:
                sval = str(val)
                if len(sval) > 100: sval = sval[:97] + "..."
                print(f"    - {k:25s}: {sval}")

        # Passage and selection details
        passages = pydict.get("passages", [{}])[0]
        if isinstance(passages, dict):
            eng_passages = passages.get("English_passages", [])
            trans_passages = passages.get("Translated_passages", [])
            is_selected = passages.get("is_selected", [])

            print(f"\n  Passage Breakdown (Record #0):")
            print(f"    - English passages count   : {len(eng_passages)}")
            print(f"    - Translated passages count: {len(trans_passages)}")
            print(f"    - Selected flags          : {is_selected}")

        print("\n  [V] Inspection completed successfully without full download.")
        return True

    except Exception as e:
        print(f"  [X] Error inspecting parquet: {e}")
        return False

if __name__ == "__main__":
    config = sys.argv[1] if len(sys.argv) > 1 else "hin"
    split = sys.argv[2] if len(sys.argv) > 2 else "validation"
    inspect_via_pyarrow(config, split)
