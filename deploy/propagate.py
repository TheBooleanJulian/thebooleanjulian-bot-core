"""
Fan out a redeploy to every service in fleet.json — canary first, gating
the rest. Run by .github/workflows/propagate.yml on every push to main.

Looks up each service's Zeabur deploy-webhook URL from an env var named
after the `webhook_secret` field in fleet.json. Those env vars are set
explicitly in propagate.yml from `secrets.<NAME>` — deliberately not
`${{ toJSON(secrets) }}`, which dumps the entire secrets store into one
var and trips GitHub's automated "may be malicious" workflow scan on
every edit to this file. Adding a new fleet member means a fleet.json
entry, a repo secret, AND a matching env line in propagate.yml.
"""

import os
import sys
import time
import urllib.request
import urllib.error
import json

FLEET_FILE = os.path.join(os.path.dirname(__file__), "fleet.json")


def trigger_webhook(url: str) -> None:
    req = urllib.request.Request(url, method="POST", data=b"")
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"  webhook responded {resp.status}")


def check_health(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            if resp.status != 200:
                return False
            body = json.loads(resp.read())
            return body.get("status") == "ok"
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return False


def main():
    with open(FLEET_FILE) as f:
        fleet = json.load(f)

    canary = fleet["canary"]

    def secret_for(service: dict) -> str:
        name = service["webhook_secret"]
        value = os.environ.get(name)
        if not value:
            print(f"  MISSING secret {name} — skipping {service['name']}")
        return value

    print(f"== Redeploying canary: {canary['name']} ==")
    canary_url = secret_for(canary)
    if not canary_url:
        print("Canary has no webhook configured — cannot safely propagate. Failing.")
        sys.exit(1)
    trigger_webhook(canary_url)

    attempts = canary.get("health_poll_attempts", 10)
    interval = canary.get("health_poll_interval_seconds", 15)
    print(f"Polling {canary['health_url']} ({attempts} attempts, {interval}s apart)...")

    healthy = False
    for i in range(1, attempts + 1):
        time.sleep(interval)
        healthy = check_health(canary["health_url"])
        print(f"  attempt {i}/{attempts}: {'healthy' if healthy else 'not ready'}")
        if healthy:
            break

    if not healthy:
        print(f"\nCanary did not become healthy after {attempts * interval}s. "
              f"BLOCKING fleet-wide redeploy — bot-core's main branch likely has a "
              f"real problem. Nothing else was touched.")
        sys.exit(1)

    print("\nCanary is healthy. Fanning out to the fleet:")
    failures = []
    for service in fleet["fleet"]:
        print(f"== Redeploying {service['name']} ==")
        url = secret_for(service)
        if not url:
            failures.append(service["name"])
            continue
        try:
            trigger_webhook(url)
        except Exception as e:
            print(f"  FAILED to trigger {service['name']}: {e}")
            failures.append(service["name"])

    if failures:
        print(f"\nCompleted with failures: {failures}")
        sys.exit(1)

    print("\nFleet-wide redeploy triggered successfully.")


if __name__ == "__main__":
    main()
