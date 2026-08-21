"""
Fan out a redeploy to every service in fleet.json — canary first, gating
the rest. Run by .github/workflows/propagate.yml on every push to main.

Zeabur has no deploy-trigger webhook feature (checked directly against
their Apollo Explorer schema — it's a requested feature, not shipped).
Redeploys go through their GraphQL API instead: a single account-wide
API token (ZEABUR_API_TOKEN) authenticates a `redeployService` mutation
per service, identified by serviceID + environmentID (not secrets —
just identifiers, safe to commit in fleet.json).
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

FLEET_FILE = os.path.join(os.path.dirname(__file__), "fleet.json")
ZEABUR_GRAPHQL_URL = "https://api.zeabur.com/graphql"

REDEPLOY_MUTATION = """
mutation Redeploy($serviceID: ObjectID!, $environmentID: ObjectID!) {
  redeployService(serviceID: $serviceID, environmentID: $environmentID)
}
"""


def api_token() -> str:
    token = os.environ.get("ZEABUR_API_TOKEN")
    if not token:
        print("MISSING secret ZEABUR_API_TOKEN — cannot call Zeabur's API at all. Failing.")
        sys.exit(1)
    return token


def trigger_redeploy(service: dict, token: str) -> None:
    payload = json.dumps({
        "query": REDEPLOY_MUTATION,
        "variables": {"serviceID": service["service_id"], "environmentID": service["environment_id"]},
    }).encode("utf-8")
    req = urllib.request.Request(
        ZEABUR_GRAPHQL_URL,
        method="POST",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())
    if body.get("errors"):
        raise RuntimeError(f"Zeabur API returned errors: {body['errors']}")
    if body.get("data", {}).get("redeployService") is not True:
        raise RuntimeError(f"Zeabur API did not confirm redeploy: {body}")
    print(f"  redeploy triggered for {service['name']}")


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

    token = api_token()
    canary = fleet["canary"]

    print(f"== Redeploying canary: {canary['name']} ==")
    try:
        trigger_redeploy(canary, token)
    except Exception as e:
        print(f"  FAILED to trigger canary redeploy: {e}")
        sys.exit(1)

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
        try:
            trigger_redeploy(service, token)
        except Exception as e:
            print(f"  FAILED to trigger {service['name']}: {e}")
            failures.append(service["name"])

    if failures:
        print(f"\nCompleted with failures: {failures}")
        sys.exit(1)

    print("\nFleet-wide redeploy triggered successfully.")


if __name__ == "__main__":
    main()
