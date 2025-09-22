from core.turns import merge_words_to_turns, turns_to_txt, unique_speaker_count

def test_unique_speaker_count():
    words = [{"speaker":"SPEAKER_00"}, {"speaker":"SPEAKER_01"}, {"speaker":None}]
    assert unique_speaker_count(words) == 2  # None treated as SPEAKER_00

def test_merge_words_to_turns_gap_merge():
    words = [
        {"speaker":"SPEAKER_00","start":0.0,"end":0.5,"text":"Hello"},
        {"speaker":"SPEAKER_00","start":0.7,"end":1.0,"text":"world"},
        {"speaker":"SPEAKER_01","start":1.2,"end":2.0,"text":"Hi"},
        {"speaker":"SPEAKER_01","start":3.0,"end":3.5,"text":"again"},
    ]
    turns = merge_words_to_turns(words, gap=0.6)
    assert len(turns) == 3
    assert turns[0]["speaker"] == "SPEAKER_00" and "Hello" in turns[0]["text"]
    assert turns[1]["speaker"] == "SPEAKER_01"
    assert turns[2]["start"] == 3.0 and turns[2]["end"] == 3.5

def test_turns_to_txt_format():
    turns = [
        {"speaker":"SPEAKER_00","start":0.0,"end":1.23,"text":"Hello"},
        {"speaker":"SPEAKER_01","start":65.0,"end":70.5,"text":"Hi there"},
    ]
    txt = turns_to_txt(turns)
    lines = txt.splitlines()
    assert lines[0].startswith("[00:00.00-00:01.23] SPEAKER_00: Hello")
    assert lines[1].startswith("[01:05.00-01:10.50] SPEAKER_01: Hi there")
