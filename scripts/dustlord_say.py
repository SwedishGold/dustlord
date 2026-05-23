#!/usr/bin/env python3
"""Lord Dusk TTS -> local HTTP -> Google Nest Audio Cast.

English-only voice layer for the Roborock S6 MaxV "Dust Lord" persona.
The Roborock's own speaker is deliberately kept muted by dustlord_watch.py.
"""
import argparse
import hashlib
import json
import os
import random
import re
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

from dustlord_behavior import decide as behavior_decide, remember_manual_line

DUSTLORD_HOME = Path(os.environ.get('DUSTLORD_HOME', Path.home() / '.hermes' / 'dustlord'))
LIB = Path(os.environ.get('DUSTLORD_VOICE_LIBRARY', DUSTLORD_HOME / 'data' / 'lord-dusk-voice-library.json'))
AUDIO_DIR = Path(os.environ.get('DUSTLORD_AUDIO_DIR', '/tmp/dustlord_audio'))
STATE_FILE = AUDIO_DIR / 'lord_dusk_state.json'
SERVER_PID_FILE = AUDIO_DIR / 'http_server.pid'
EDGE_TTS = os.environ.get('DUSTLORD_EDGE_TTS', 'edge-tts')
CAST_HOST = os.environ.get('DUSTLORD_CAST_HOST', '127.0.0.1')
CAST_UUID = uuid.UUID(os.environ.get('DUSTLORD_CAST_UUID', '00000000-0000-0000-0000-000000000000'))
CAST_NAME = os.environ.get('DUSTLORD_CAST_NAME', 'Nest Audio')
CAST_MODEL = os.environ.get('DUSTLORD_CAST_MODEL', 'Nest Audio')
HTTP_PORT = int(os.environ.get('DUSTLORD_HTTP_PORT', '8767'))
DEFAULT_VOICE = os.environ.get('DUSTLORD_TTS_VOICE', 'en-GB-SoniaNeural')

# Simple Swedish-character/word guardrail. The library should already be English,
# but this prevents accidentally adding Swedish lines later.
SWEDISH_RE = re.compile(r'[åäöÅÄÖ]|\b(jag|och|inte|dockan|golvet|smulor|damm|tillbaka|laddning|städ)\b', re.I)


def mac_ip():
    for cmd in [['ipconfig', 'getifaddr', 'en0'], ['ipconfig', 'getifaddr', 'en1']]:
        try:
            out = subprocess.check_output(cmd, text=True, timeout=3).strip()
            if out:
                return out
        except Exception:
            pass
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    finally:
        s.close()


def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {'last_by_scenario': {}, 'recent_lines': []}


def save_state(state):
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def validate_english(text):
    if SWEDISH_RE.search(text):
        raise SystemExit(f'Refusing non-English Lord Dusk line: {text!r}')


def choose_line(scenario):
    lib = json.loads(LIB.read_text())
    lines = lib['scenarios'].get(scenario)
    if not lines:
        raise SystemExit(f'Unknown scenario: {scenario}. Available: {", ".join(sorted(lib["scenarios"]))}')
    for line in lines:
        validate_english(line)

    decision = behavior_decide(scenario, lines)
    if not decision.get('speak'):
        return None, decision
    return decision['line'], decision


def make_tts(text, voice=DEFAULT_VOICE):
    validate_english(text)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1((text + str(time.time())).encode()).hexdigest()[:10]
    out = AUDIO_DIR / f'lord_dusk_{digest}.mp3'
    cmd = [EDGE_TTS, '--voice', voice, '--text', text, '--write-media', str(out)]
    subprocess.check_call(cmd, timeout=60)
    return out


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def http_responds():
    import urllib.request
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{HTTP_PORT}/', timeout=1.5) as r:
            return r.status < 500
    except Exception:
        return False


def ensure_http_server():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    if SERVER_PID_FILE.exists():
        try:
            pid = int(SERVER_PID_FILE.read_text().strip())
            if pid_alive(pid) and http_responds():
                return pid
        except Exception:
            pass

    log = (AUDIO_DIR / 'http_server.log').open('ab')
    proc = subprocess.Popen(
        [sys.executable, '-m', 'http.server', str(HTTP_PORT), '--bind', '0.0.0.0'],
        cwd=str(AUDIO_DIR),
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    SERVER_PID_FILE.write_text(str(proc.pid))
    for _ in range(20):
        if http_responds():
            return proc.pid
        time.sleep(0.2)
    raise RuntimeError(f'HTTP server did not become ready on port {HTTP_PORT}')


def cast_mp3(path):
    import pychromecast
    ensure_http_server()
    host = (CAST_HOST, 8009, CAST_UUID, CAST_MODEL, CAST_NAME)
    url = f'http://{mac_ip()}:{HTTP_PORT}/{path.name}'
    cast = pychromecast.get_chromecast_from_host(host, tries=2, timeout=15)
    cast.wait(timeout=15)
    mc = cast.media_controller
    mc.play_media(url, 'audio/mp3', title='Lord Dusk')
    mc.block_until_active(timeout=15)
    time.sleep(1.0)
    print(json.dumps({
        'ok': True,
        'cast': cast.name,
        'url': url,
        'player_state': mc.status.player_state,
        'text_file': str(path),
    }, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scenario', default='manual_summon')
    ap.add_argument('--text')
    ap.add_argument('--voice', default=DEFAULT_VOICE)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--ensure-server', action='store_true')
    args = ap.parse_args()

    if args.ensure_server:
        pid = ensure_http_server()
        print(json.dumps({'ok': True, 'http_pid': pid, 'port': HTTP_PORT, 'dir': str(AUDIO_DIR)}))
        return

    if args.text:
        text = args.text
        decision = remember_manual_line(args.scenario, text)
    else:
        text, decision = choose_line(args.scenario)
    if not text:
        print(f"Lord Dusk remains silent [{args.scenario}]: {decision.get('reason')} mood={decision.get('mood')}", flush=True)
        return
    validate_english(text)
    meta = f" mood={decision.get('mood')} rarity={decision.get('rarity')}" if decision else ""
    print(f'Lord Dusk says [{args.scenario}]: {text}{meta}', flush=True)
    if args.dry_run:
        return
    path = make_tts(text, voice=args.voice)
    cast_mp3(path)


if __name__ == '__main__':
    main()
