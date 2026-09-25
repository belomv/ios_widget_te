#!/usr/bin/env python3
"""Прототип эксперимента A: вход в Training Endurance и тренировки на 7 дней.

Только стандартная библиотека. Учётные данные и токен лежат в secrets/ (в .gitignore):

    secrets/te.env           TE_EMAIL=...  и  TE_PASSWORD=...
    secrets/te-session.json  создаётся скриптом: session_token + expires_at

Запуск:
    python3 tools/te-probe/te_probe.py            # 7 дней начиная с сегодня
    python3 tools/te-probe/te_probe.py --days 14 --json
    python3 tools/te-probe/te_probe.py --login    # принудительно войти заново
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://app.trainingendurance.com"
KRATOS = BASE + "/kratos"
GRAPHQL = BASE + "/graphql"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SECRETS = os.path.join(ROOT, "secrets")
ENV_FILE = os.path.join(SECRETS, "te.env")
SESSION_FILE = os.path.join(SECRETS, "te-session.json")

ME_QUERY = "query getMe { userInfo { id email role permissions { __typename } } }"

CALENDAR_QUERY = """
query calendarItems($request: CalendarItemsRequest!) {
  calendarItems(p: $request) {
    records {
      id
      date
      sort
      type
      data {
        __typename
        ... on Workout {
          name
          workoutType
          manualDone
          description
          plan { duration distance ess }
          fact { duration distance ess }
        }
        ... on Rest { name }
        ... on Event { name type }
      }
    }
  }
}
"""


def http_json(url, payload=None, headers=None, method=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(body)
        except ValueError:
            return e.code, {"raw": body[:500]}


def read_env():
    env = {}
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    env.update({k: v for k, v in os.environ.items() if k.startswith("TE_")})
    return env


def login(email, password):
    """Нативный (API) поток Ory Kratos: без cookies и CSRF, в ответ приходит session_token."""
    status, flow = http_json(KRATOS + "/self-service/login/api")
    if status != 200:
        sys.exit(f"login flow: HTTP {status}: {flow}")
    status, res = http_json(
        flow["ui"]["action"],
        {"method": "password", "identifier": email, "password": password},
    )
    if status != 200 or "session_token" not in res:
        msgs = [m.get("text") for m in (res.get("ui", {}).get("messages") or [])]
        for n in res.get("ui", {}).get("nodes", []):
            msgs += [m.get("text") for m in n.get("messages") or []]
        sys.exit(f"login failed: HTTP {status}: {msgs or res.get('error') or res}")
    sess = {
        "session_token": res["session_token"],
        "expires_at": res["session"].get("expires_at"),
        "authenticated_at": res["session"].get("authenticated_at"),
    }
    os.makedirs(SECRETS, exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump(sess, f)
    os.chmod(SESSION_FILE, 0o600)
    return sess


def whoami(token):
    return http_json(KRATOS + "/sessions/whoami", headers={"X-Session-Token": token})


def gql(token, query, variables=None):
    status, res = http_json(
        GRAPHQL,
        {"query": query, "variables": variables or {}},
        headers={"Authorization": "Bearer " + token},
    )
    if status != 200 or res.get("errors"):
        sys.exit(f"graphql: HTTP {status}: {res.get('errors') or res}")
    return res["data"]


def get_token(force_login):
    env = read_env()
    if env.get("TE_SESSION_TOKEN"):
        return env["TE_SESSION_TOKEN"]
    if not force_login and os.path.exists(SESSION_FILE):
        token = json.load(open(SESSION_FILE))["session_token"]
        status, _ = whoami(token)
        if status == 200:
            return token
        print(f"# saved session is not valid (whoami HTTP {status}), logging in again", file=sys.stderr)
    if not env.get("TE_EMAIL") or not env.get("TE_PASSWORD"):
        sys.exit(f"нет учётных данных: создай {ENV_FILE} с TE_EMAIL=... и TE_PASSWORD=...")
    return login(env["TE_EMAIL"], env["TE_PASSWORD"])["session_token"]


def fmt_duration(sec):
    if not sec:
        return ""
    h, m = divmod(round(sec / 60), 60)
    return f"{h}:{m:02d}" if h else f"{m} мин"


def fmt_distance(m):
    return f"{m / 1000:.1f} км" if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--start", help="YYYY-MM-DD, по умолчанию сегодня")
    ap.add_argument("--login", action="store_true", help="войти заново, даже если токен сохранён")
    ap.add_argument("--json", action="store_true", help="напечатать сырой ответ")
    args = ap.parse_args()

    token = get_token(args.login)
    status, sess = whoami(token)
    me = gql(token, ME_QUERY)["userInfo"]
    print(f"# user {me['id']} role={me['role']} session expires_at={sess.get('expires_at')}", file=sys.stderr)

    start = dt.date.fromisoformat(args.start) if args.start else dt.date.today()
    dates = [(start + dt.timedelta(days=i)).isoformat() for i in range(args.days)]
    data = gql(token, CALENDAR_QUERY, {"request": {"userID": me["id"], "dates": dates}})
    records = sorted(data["calendarItems"]["records"], key=lambda r: (r["date"], r["sort"]))

    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return
    for r in records:
        d = r["data"] or {}
        if r["type"] == "WORKOUT":
            plan, fact = d.get("plan") or {}, d.get("fact") or {}
            done = "✓" if (d.get("manualDone") or fact.get("duration")) else " "
            print(f"{r['date']} {done} {d.get('workoutType', ''):8} {d.get('name', '')!s:40} "
                  f"план {fmt_duration(plan.get('duration')):>7} {fmt_distance(plan.get('distance')):>8}  "
                  f"факт {fmt_duration(fact.get('duration')):>7} {fmt_distance(fact.get('distance')):>8}")
        else:
            print(f"{r['date']}   {r['type']:8} {d.get('name', '')}")
    if not records:
        print("(нет записей в календаре на эти даты)")


if __name__ == "__main__":
    main()
