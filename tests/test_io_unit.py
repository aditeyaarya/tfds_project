from pathlib import Path
from core.io_utils import as_segments, save_three_outputs_locally
import json

def test_as_segments_various_shapes():
    assert as_segments({"segments":[{"text":"a"}]})[0]["text"] == "a"
    assert as_segments({"items":[{"text":"b"}]})[0]["text"] == "b"
    assert as_segments([{"text":"c"}])[0]["text"] == "c"
    assert as_segments(None) == []

def test_save_three_outputs_locally(tmp_path: Path):
    out = tmp_path / "out"
    jb = json.dumps([{"k":1}]).encode("utf-8")
    cb = b"speaker,start,end,text\nSPEAKER_00,0,1,Hi\n"
    ts = "sample"
    save_three_outputs_locally(out, jb, cb, ts)

    assert (out/"words.json").exists()
    assert (out/"turns.csv").exists()
    assert (out/"transcript.txt").read_text("utf-8") == "sample"
