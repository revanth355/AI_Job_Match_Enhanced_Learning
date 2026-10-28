"""Portable progress backups: no resume text or shared server-side user database."""
import hashlib
import json
from .plans import build_daily_plan

VERSION = 1


def plan_key(plan):
    content = {k: v for k, v in plan.items() if k not in ('completed_days', 'note')}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def export_progress(plan):
    return json.dumps({'version': VERSION, 'plan_key': plan_key(plan),
                       'requested_days': plan['requested_days'], 'minutes_per_day': plan['minutes_per_day'],
                       'levels': plan.get('levels', {}), 'completed_days': plan['completed_days']}, indent=2)


def import_progress(raw, learning_plan):
    if len(raw) > 100000:
        raise ValueError('Progress file is too large (maximum 100 KB).')
    try:
        data = json.loads(raw)
        if not isinstance(data, dict) or data.get('version') != VERSION:
            raise ValueError('Unsupported progress file version.')
        days, minutes = data['requested_days'], data['minutes_per_day']
        levels, completed = data['levels'], data['completed_days']
        if type(days) is not int or type(minutes) is not int or not isinstance(levels, dict):
            raise ValueError('Invalid study settings.')
        plan = build_daily_plan(learning_plan, days, minutes, levels)
        if data['plan_key'] != plan_key(plan):
            raise ValueError('This backup belongs to a different plan or curriculum. Use the same resume/JD gaps, priorities and study settings.')
        if not isinstance(completed, list) or len(completed) != len(set(completed)) or any(type(d) is not int or not 1 <= d <= plan['total_days'] for d in completed):
            raise ValueError('Invalid completed days.')
        plan['completed_days'] = sorted(completed)
        return plan
    except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError('Invalid progress JSON. Choose a backup downloaded by this app.') from exc
