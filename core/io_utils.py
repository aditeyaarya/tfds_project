from pathlib import Path
from typing import Any, Dict, List
import json

def save_tmp(file) -> str:
    tmp = Path(".streamlit_tmp"); tmp.mkdir(exist_ok=True)
    p = tmp / file.name
    with open(p, "wb") as f: f.write(file.getbuffer())
    return str(p)

def save_three_outputs_locally(out_dir: Path, json_bytes: bytes, csv_bytes: bytes, txt_str: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "words.json").write_bytes(json_bytes)
    (out_dir / "turns.csv").write_bytes(csv_bytes)
    (out_dir / "transcript.txt").write_text(txt_str, encoding="utf-8")

def as_segments(obj: Any) -> List[Dict[str, Any]]:
    if obj is None: return []
    if isinstance(obj, list): return obj
    if isinstance(obj, dict):
        for k in ("segments","items","result"):
            v = obj.get(k)
            if isinstance(v, list): return v
    return []
