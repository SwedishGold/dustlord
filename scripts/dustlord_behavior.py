#!/usr/bin/env python3
"""Lord Dusk Behavior Engine v0.3.

Adds character behavior on top of the voice library:
- mood derived from scenario
- persistent mission/event memory
- rarity-weighted line selection
- safe silence for low-value chatter
- nemesis counters for recurring problems

This module never moves the robot. It only chooses/records speech behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any

AUDIO_DIR = Path(os.environ.get('DUSTLORD_AUDIO_DIR', '/tmp/dustlord_audio'))
STATE_FILE = Path(os.environ.get('DUSTLORD_BEHAVIOR_STATE_FILE', AUDIO_DIR / 'lord_dusk_behavior_state.json'))

MOOD_BY_SCENARIO = {
    'manual_summon': 'attentive',
    'clean_start': 'ritual',
    'cleaning_progress': 'hunter',
    'room_change': 'hunter',
    'obstacle': 'annoyed',
    'stuck': 'wounded_pride',
    'error': 'wounded_pride',
    'returning': 'homeward',
    'docked': 'victorious',
    'clean_complete': 'victorious',
    'battery_low': 'hungry_for_volts',
    'bin_full_or_dirty': 'burdened',
    'failed_docking': 'lost_priest',
    'night_quiet': 'night_whisper',
    'victory': 'victorious',
    'pet_or_child_safe': 'gentle_guardian',
}

IMPORTANT_SCENARIOS = {
    'manual_summon', 'clean_start', 'returning', 'docked', 'clean_complete',
    'error', 'stuck', 'battery_low', 'failed_docking', 'pet_or_child_safe'
}
PROBLEM_SCENARIOS = {'obstacle', 'stuck', 'error', 'failed_docking', 'bin_full_or_dirty'}
MISSION_START = {'clean_start'}
MISSION_END = {'docked', 'clean_complete'}

RARITY_WEIGHTS = {
    'common': 72,
    'rare': 23,
    'legendary': 5,
}

DEFAULT_STATE = {
    'version': '0.3',
    'mood': 'dormant',
    'event_counts': {},
    'scenario_counts': {},
    'nemesis': {},
    'last_by_scenario': {},
    'recent_lines': [],
    'recent_events': [],
    'missions': [],
    'current_mission': None,
    'silence': {
        'last_spoken_ts': 0,
        'suppressed_count': 0,
    },
}


def now_ts() -> float:
    return time.time()


def iso(ts: float | None = None) -> str:
    return datetime.fromtimestamp(ts or now_ts()).isoformat(timespec='seconds')


def load_state() -> dict[str, Any]:
    try:
        data = json.loads(STATE_FILE.read_text())
    except Exception:
        data = {}
    state = json.loads(json.dumps(DEFAULT_STATE))
    merge_dict(state, data)
    return state


def merge_dict(dst: dict[str, Any], src: dict[str, Any]) -> None:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            merge_dict(dst[k], v)
        else:
            dst[k] = v


def save_state(state: dict[str, Any]) -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))


def stable_bucket(text: str) -> int:
    return int(hashlib.sha1(text.encode('utf-8')).hexdigest()[:8], 16) % 100


def line_rarity(line: str) -> str:
    bucket = stable_bucket(line)
    if bucket >= 96:
        return 'legendary'
    if bucket >= 76:
        return 'rare'
    return 'common'


def mood_for(scenario: str, quiet: bool = False) -> str:
    if quiet and scenario not in IMPORTANT_SCENARIOS:
        return 'night_whisper'
    return MOOD_BY_SCENARIO.get(scenario, 'dormant')


def is_quiet_hour() -> bool:
    hour = datetime.now().hour
    return hour >= 22 or hour < 7


def weighted_pick(lines: list[str], state: dict[str, Any], scenario: str) -> tuple[str, str]:
    last = state.get('last_by_scenario', {}).get(scenario)
    recent = set(state.get('recent_lines', [])[-18:])
    candidates = [x for x in lines if x != last and x not in recent]
    if not candidates:
        candidates = [x for x in lines if x != last] or list(lines)

    weighted: list[str] = []
    for line in candidates:
        rarity = line_rarity(line)
        weighted.extend([line] * RARITY_WEIGHTS[rarity])
    chosen = random.choice(weighted or candidates)
    return chosen, line_rarity(chosen)


def should_silence(state: dict[str, Any], scenario: str, *, force: bool = False) -> tuple[bool, str]:
    if force or scenario in IMPORTANT_SCENARIOS:
        return False, 'important_or_forced'
    quiet = is_quiet_hour()
    elapsed = now_ts() - float(state.get('silence', {}).get('last_spoken_ts', 0) or 0)
    # Low-value chatter should not be too frequent. Watcher also has cooldowns;
    # this is character intelligence rather than safety-critical throttling.
    if quiet and scenario not in {'night_quiet', 'error', 'stuck', 'battery_low'}:
        return True, 'quiet_hour'
    if scenario == 'cleaning_progress' and elapsed < 15 * 60:
        return True, 'recently_spoke'
    if scenario in {'room_change', 'obstacle'} and elapsed < 3 * 60:
        return True, 'too_chatty'
    return False, 'speak'


def start_mission(state: dict[str, Any], scenario: str) -> None:
    if scenario not in MISSION_START:
        return
    if state.get('current_mission') and not state['current_mission'].get('ended_at'):
        return
    state['current_mission'] = {
        'started_at': iso(),
        'events': [],
        'result': 'in_progress',
    }


def finish_mission(state: dict[str, Any], scenario: str) -> None:
    if scenario not in MISSION_END:
        return
    mission = state.get('current_mission') or {'started_at': None, 'events': []}
    mission['ended_at'] = iso()
    mission['result'] = 'victory' if scenario in {'docked', 'clean_complete'} else scenario
    mission['event_count'] = len(mission.get('events', []))
    missions = state.setdefault('missions', [])
    missions.append(mission)
    state['missions'] = missions[-20:]
    state['current_mission'] = None


def record_event(state: dict[str, Any], scenario: str, line: str | None, rarity: str | None, spoken: bool, reason: str) -> None:
    ts = now_ts()
    state['mood'] = mood_for(scenario, is_quiet_hour())
    state.setdefault('event_counts', {})[scenario] = int(state.setdefault('event_counts', {}).get(scenario, 0)) + 1
    state.setdefault('scenario_counts', {})[scenario] = int(state.setdefault('scenario_counts', {}).get(scenario, 0)) + 1

    if scenario in PROBLEM_SCENARIOS:
        state.setdefault('nemesis', {})[scenario] = int(state.setdefault('nemesis', {}).get(scenario, 0)) + 1

    start_mission(state, scenario)
    if state.get('current_mission') is not None:
        state['current_mission'].setdefault('events', []).append({'ts': iso(ts), 'scenario': scenario, 'spoken': spoken})
        state['current_mission']['events'] = state['current_mission']['events'][-50:]

    event = {'ts': iso(ts), 'scenario': scenario, 'mood': state['mood'], 'spoken': spoken, 'reason': reason}
    if line:
        event['line'] = line
    if rarity:
        event['rarity'] = rarity
    state.setdefault('recent_events', []).append(event)
    state['recent_events'] = state['recent_events'][-50:]

    if spoken and line:
        state.setdefault('last_by_scenario', {})[scenario] = line
        state.setdefault('recent_lines', []).append(line)
        state['recent_lines'] = state['recent_lines'][-50:]
        state.setdefault('silence', {})['last_spoken_ts'] = ts
    else:
        state.setdefault('silence', {})['suppressed_count'] = int(state.setdefault('silence', {}).get('suppressed_count', 0)) + 1

    finish_mission(state, scenario)


def decide(scenario: str, lines: list[str], *, force: bool = False) -> dict[str, Any]:
    state = load_state()
    silent, reason = should_silence(state, scenario, force=force)
    if silent:
        record_event(state, scenario, None, None, False, reason)
        save_state(state)
        return {
            'speak': False,
            'scenario': scenario,
            'mood': state.get('mood'),
            'reason': reason,
            'state_file': str(STATE_FILE),
        }
    line, rarity = weighted_pick(lines, state, scenario)
    record_event(state, scenario, line, rarity, True, reason)
    save_state(state)
    return {
        'speak': True,
        'scenario': scenario,
        'line': line,
        'rarity': rarity,
        'mood': state.get('mood'),
        'reason': reason,
        'state_file': str(STATE_FILE),
    }


def remember_manual_line(scenario: str, line: str) -> dict[str, Any]:
    state = load_state()
    rarity = line_rarity(line)
    record_event(state, scenario, line, rarity, True, 'manual_text')
    save_state(state)
    return {'scenario': scenario, 'line': line, 'rarity': rarity, 'mood': state.get('mood'), 'speak': True}


def status() -> dict[str, Any]:
    state = load_state()
    return {
        'ok': True,
        'version': state.get('version'),
        'mood': state.get('mood'),
        'event_counts': state.get('event_counts', {}),
        'nemesis': state.get('nemesis', {}),
        'current_mission': state.get('current_mission'),
        'last_mission': (state.get('missions') or [None])[-1],
        'recent_events': state.get('recent_events', [])[-10:],
        'silence': state.get('silence', {}),
        'state_file': str(STATE_FILE),
    }


def report_text() -> str:
    s = status()
    nemesis = s.get('nemesis') or {}
    nemesis_line = 'none yet' if not nemesis else ', '.join(f'{k}×{v}' for k, v in sorted(nemesis.items(), key=lambda kv: (-kv[1], kv[0])))
    last = s.get('last_mission') or {}
    lines = [
        'Lord Dusk Behavior Report',
        f"Mood: {s.get('mood')}",
        f"Nemesis: {nemesis_line}",
        f"Suppressed chatter: {s.get('silence', {}).get('suppressed_count', 0)}",
    ]
    if last:
        lines.append(f"Last mission: {last.get('result')} from {last.get('started_at')} to {last.get('ended_at')} events={last.get('event_count')}")
    return '\n'.join(lines)


def reset() -> dict[str, Any]:
    save_state(json.loads(json.dumps(DEFAULT_STATE)))
    return {'ok': True, 'reset': str(STATE_FILE)}


def main() -> int:
    ap = argparse.ArgumentParser(description='Lord Dusk Behavior Engine v0.3')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('status')
    sub.add_parser('report')
    sub.add_parser('reset')
    p = sub.add_parser('decide')
    p.add_argument('scenario')
    p.add_argument('lines_json')
    p.add_argument('--force', action='store_true')
    args = ap.parse_args()

    if args.cmd == 'status':
        print(json.dumps(status(), ensure_ascii=False, indent=2))
    elif args.cmd == 'report':
        print(report_text())
    elif args.cmd == 'reset':
        print(json.dumps(reset(), ensure_ascii=False, indent=2))
    elif args.cmd == 'decide':
        print(json.dumps(decide(args.scenario, json.loads(args.lines_json), force=args.force), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
