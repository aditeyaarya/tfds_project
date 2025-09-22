from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .io_utils import as_segments
from .turns import merge_words_to_turns, unique_speaker_count

def run_pipeline(
    input_path: str,
    model_size: str,
    device: str,
    language: Optional[str],
    hf_token: str,
    diar_device: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Heavy pipeline with lazy imports so tests/CI don't need torch/whisperx at import time.
    Returns (words, turns).
    """
    import whisperx, torch
    from whisperx.diarize import DiarizationPipeline

    compute_type = "float16" if device == "cuda" else "float32"
    model = whisperx.load_model(model_size, device, compute_type=compute_type)
    lang_arg = None if not language or not language.strip() else language.strip()

    with torch.inference_mode():
        asr_result = model.transcribe(
            input_path,
            language=lang_arg,
            batch_size=16 if device == "cuda" else 1
        )
    segments = as_segments(asr_result)
    if not segments:
        raise RuntimeError("No segments returned by Whisper.")

    # Align
    align_model, metadata = whisperx.load_align_model(language_code=(lang_arg or asr_result.get("language") or "en"),
                                                      device=device)
    aligned = whisperx.align(segments, align_model, metadata, input_path, device, return_char_alignments=False)

    # Diarize
    diar_raw = DiarizationPipeline(use_auth_token=hf_token, device=diar_device)(input_path)

    # Assign speakers to words
    word_level = whisperx.assign_word_speakers(diar_raw, aligned)

    # Normalize words output
    words: Optional[List[Dict[str, Any]]] = None
    if isinstance(word_level, dict):
        for key in ("words","word_segments","segments","items","result"):
            cand = word_level.get(key)
            if isinstance(cand, list) and cand:
                words = cand; break
        if words is None:
            for v in word_level.values():
                if isinstance(v, list) and v:
                    words = v; break
    elif isinstance(word_level, list):
        words = word_level

    if not words:
        raise RuntimeError("Speaker assignment returned empty content.")
    if unique_speaker_count(words) < 2:
        raise RuntimeError("Diarization succeeded but <2 unique speakers after assignment (strict).")

    # Ensure each word has 'text'
    for w in words:
        if not (isinstance(w.get("text"), str) and w["text"].strip()):
            if isinstance(w.get("word"), str) and w["word"].strip():
                w["text"] = w["word"]

    turns = merge_words_to_turns(words, gap=0.6)
    return words, turns
