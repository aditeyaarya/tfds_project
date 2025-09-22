from typing import List, Dict, Any

def merge_words_to_turns(words: List[Dict[str, Any]], gap: float = 0.6) -> List[Dict[str, Any]]:
    turns: List[Dict[str, Any]] = []
    if not words: return turns
    cur = None
    for w in words:
        spk = w.get("speaker") or "SPEAKER_00"
        ws = float(w.get("start", 0.0) or 0.0)
        we = float(w.get("end", ws) or ws)
        tx = (w.get("text") or w.get("word") or "").strip()
        if cur is None:
            cur = {"speaker": spk, "start": ws, "end": we, "text": (tx or "")}
            continue
        if spk != cur["speaker"] or ws - cur["end"] > gap:
            turns.append(cur)
            cur = {"speaker": spk, "start": ws, "end": we, "text": (tx or "")}
        else:
            cur["end"] = max(cur["end"], we)
            if tx:
                cur["text"] = (cur["text"] + " " + tx).strip()
    if cur: turns.append(cur)
    return turns

def turns_to_txt(turns: List[Dict[str, Any]]) -> str:
    def t(x): return f"{int(x//60):02d}:{x%60:05.2f}"
    return "\n".join(f"[{t(u['start'])}-{t(u['end'])}] {u['speaker']}: {u.get('text','')}" for u in turns)

def unique_speaker_count(words: List[Dict[str, Any]]) -> int:
    return len({(w.get("speaker") or "SPEAKER_00") for w in words})
