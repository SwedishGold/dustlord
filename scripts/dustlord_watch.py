#!/usr/bin/env python3
"""Robust Lord Dusk watcher for Roborock S6 MaxV.

- Forces robot internal speaker volume to 0.
- Watches cleaning/returning/docked/error/battery transitions.
- Uses cooldowns and anti-repeat via dustlord_say.py.
- Suppresses non-critical chatter during quiet hours.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

DUSTLORD_HOME = Path(os.environ.get('DUSTLORD_HOME', Path.home() / '.hermes' / 'dustlord'))
RPC = [
    os.environ.get('DUSTLORD_RPC_PY', sys.executable),
    os.environ.get('DUSTLORD_RPC_SCRIPT', '/tmp/roborock_local_rpc.py'),
    'command',
]
SAY = [
    os.environ.get('DUSTLORD_CAST_PY', sys.executable),
    os.environ.get('DUSTLORD_SAY_SCRIPT', str(DUSTLORD_HOME / 'scripts' / 'dustlord_say.py')),
]
AUDIO_DIR = Path(os.environ.get('DUSTLORD_AUDIO_DIR', '/tmp/dustlord_audio'))
LOG = AUDIO_DIR / 'watch.log'
STATE_FILE = AUDIO_DIR / 'watch_state.json'

DEFAULT_COOLDOWNS = {
    'clean_start': 60,
    'cleaning_progress': 20 * 60,
    'returning': 60,
    'docked': 60,
    'error': 5 * 60,
    'battery_low': 30 * 60,
    'failed_docking': 10 * 60,
}


def log(msg):
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    line = time.strftime('%Y-%m-%d %H:%M:%S ') + msg
    print(line, flush=True)
    with LOG.open('a') as f:
        f.write(line + '\n')


def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {'last_trigger_ts': {}, 'last_status': None}


def save_state(state):
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def rpc(cmd, params=None):
    full = RPC + [cmd]
    if params is not None:
        full += ['--params', json.dumps(params, separators=(',', ':'))]
    out = subprocess.check_output(full, text=True, timeout=30)
    data = json.loads(out)
    if isinstance(data, list) and data:
        return data[0]
    return data


def ensure_muted():
    try:
        vol = rpc('get_sound_volume')
        if isinstance(vol, list) and vol:
            vol = vol[0]
        if int(vol) != 0:
            log(f'robot speaker volume={vol}; muting to 0')
            rpc('change_sound_volume', [0])
        return True
    except Exception as e:
        log(f'WARN mute check failed: {type(e).__name__}: {e}')
        return False


def say(scenario, text=None, dry_run=False):
    cmd = SAY + ['--scenario', scenario]
    if text:
        cmd += ['--text', text]
    if dry_run:
        cmd += ['--dry-run']
    out = subprocess.check_output(cmd, text=True, timeout=90)
    log('say output: ' + out.strip().replace('\n', ' | '))


def is_quiet_hour(quiet_start, quiet_end):
    hour = datetime.now().hour
    if quiet_start == quiet_end:
        return False
    if quiet_start < quiet_end:
        return quiet_start <= hour < quiet_end
    return hour >= quiet_start or hour < quiet_end


def can_trigger(pstate, scenario, cooldown):
    now = time.time()
    last = float(pstate.setdefault('last_trigger_ts', {}).get(scenario, 0))
    if now - last < cooldown:
        return False
    pstate['last_trigger_ts'][scenario] = now
    save_state(pstate)
    return True


def trigger(pstate, scenario, cooldowns, dry_run=False):
    if not can_trigger(pstate, scenario, cooldowns.get(scenario, 60)):
        log(f'skip {scenario}: cooldown')
        return False
    try:
        say(scenario, dry_run=dry_run)
        return True
    except Exception as e:
        log(f'ERROR say {scenario} failed: {type(e).__name__}: {e}')
        return False


def summarize(st):
    return {
        'state': int(st.get('state', -1)),
        'battery': int(st.get('battery', 0)),
        'clean_time': int(st.get('clean_time', 0)),
        'clean_area': int(st.get('clean_area', 0)),
        'error_code': int(st.get('error_code', 0)),
        'in_cleaning': int(st.get('in_cleaning', 0)),
        'in_returning': int(st.get('in_returning', 0)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--duration', type=int, default=0, help='Seconds to run; 0 = forever')
    ap.add_argument('--interval', type=float, default=10.0)
    ap.add_argument('--progress-minutes', type=float, default=20.0)
    ap.add_argument('--quiet-start', type=int, default=22)
    ap.add_argument('--quiet-end', type=int, default=7)
    ap.add_argument('--battery-low', type=int, default=20)
    ap.add_argument('--mute-every', type=int, default=30, help='Mute check every N polls')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    cooldowns = dict(DEFAULT_COOLDOWNS)
    cooldowns['cleaning_progress'] = int(args.progress_minutes * 60)

    # Ensure the HTTP server is ready and the robot does not speak with its own voice.
    try:
        subprocess.check_output(SAY + ['--ensure-server'], text=True, timeout=20)
    except Exception as e:
        log(f'WARN HTTP server ensure failed: {type(e).__name__}: {e}')
    ensure_muted()

    pstate = load_state()
    start = time.time()
    prev = summarize(rpc('get_status'))
    pstate['last_status'] = prev
    save_state(pstate)
    duration_label = 'forever' if args.duration == 0 else f'{args.duration}s'
    log(f'start watch duration={duration_label} interval={args.interval}s initial={prev}')

    polls = 0
    returning_since = None
    while args.duration == 0 or time.time() - start < args.duration:
        polls += 1
        try:
            if args.mute_every and polls % args.mute_every == 0:
                ensure_muted()
            st = summarize(rpc('get_status'))
        except Exception as e:
            log(f'ERROR status poll failed: {type(e).__name__}: {e}')
            time.sleep(args.interval)
            continue

        quiet = is_quiet_hour(args.quiet_start, args.quiet_end)
        log(f'poll state={st["state"]} cleaning={st["in_cleaning"]} returning={st["in_returning"]} err={st["error_code"]} battery={st["battery"]} quiet={int(quiet)}')

        if st['error_code']:
            trigger(pstate, 'error', cooldowns, dry_run=args.dry_run)
        elif st['battery'] and st['battery'] <= args.battery_low and st['state'] != 8:
            trigger(pstate, 'battery_low', cooldowns, dry_run=args.dry_run)
        elif st['in_cleaning'] == 1 and prev['in_cleaning'] == 0:
            trigger(pstate, 'clean_start', cooldowns, dry_run=args.dry_run)
        elif st['in_cleaning'] == 1 and not quiet:
            trigger(pstate, 'cleaning_progress', cooldowns, dry_run=args.dry_run)
        elif st['in_returning'] == 1 and prev['in_returning'] == 0:
            returning_since = time.time()
            trigger(pstate, 'returning', cooldowns, dry_run=args.dry_run)
        elif st['in_returning'] == 1:
            if returning_since is None:
                returning_since = time.time()
            if time.time() - returning_since > 8 * 60:
                trigger(pstate, 'failed_docking', cooldowns, dry_run=args.dry_run)
        elif st['state'] == 8 and prev['state'] != 8:
            returning_since = None
            trigger(pstate, 'docked', cooldowns, dry_run=args.dry_run)

        pstate['last_status'] = st
        save_state(pstate)
        prev = st
        time.sleep(args.interval)

    log('watch done')


if __name__ == '__main__':
    main()
