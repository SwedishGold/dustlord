import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "data" / "lord-dusk-voice-library.json"


def test_voice_library_valid_json():
    data = json.loads(LIB.read_text())
    assert "scenarios" in data
    assert isinstance(data["scenarios"], dict)
    assert data["scenarios"]


def test_voice_lines_are_nonempty_englishish():
    data = json.loads(LIB.read_text())
    bad = []
    for scenario, lines in data["scenarios"].items():
        assert lines, scenario
        for line in lines:
            assert isinstance(line, str)
            assert line.strip()
            if re.search(r"[åäöÅÄÖ]|\b(jag|och|inte|städ|smulor)\b", line, re.I):
                bad.append((scenario, line))
    assert not bad
