"""Canary-first fan-out of a bot-core commit to every bot on Cloudflare Workers (deploy/workers-fleet.json).

For each repo: clone the listed branch, install its deps plus thebooleanjulian-bot-core at exactly
BOT_CORE_SHA, run its tests, `wrangler deploy --var BOT_CORE_SHA:<sha>`, then poll its /healthz until it
reports that sha with status "pass". The canary goes first; if it fails, nothing else is touched.

Env: CLOUDFLARE_API_TOKEN (Workers edit), BOT_CORE_SHA (defaults to GITHUB_SHA),
     FLEET_GITHUB_TOKEN (read access to private bot repos; optional for public ones).
Stdlib only, like propagate.py.
"""
import json, os, shutil, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORE_REPO = "TheBooleanJulian/thebooleanjulian-bot-core"


def run(cmd, cwd, env):
    print(f"    $ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=cwd, env=env)
    if r.returncode:
        raise RuntimeError(f"`{cmd[0]} {cmd[1] if len(cmd) > 1 else ''}` exited {r.returncode}")


def wait_healthy(url, sha, attempts=12, interval=10):
    for i in range(attempts):
        try:
            with urllib.request.urlopen(url + ("&" if "?" in url else "?") + f"t={time.time()}", timeout=15) as r:
                body = json.load(r)
            got = body.get("bot_core", {}).get("sha")
            if got == sha and body.get("status") == "pass":
                return True
            print(f"    health: status={body.get('status')} sha={str(got)[:7]} (want {sha[:7]})", flush=True)
        except Exception as e:  # 5xx while the new version rolls out is normal for a few seconds
            print(f"    health: {e}", flush=True)
        time.sleep(interval)
    return False


def deploy(entry, sha, account_id, gh_token):
    name, repo, branch = entry["name"], entry["repo"], entry.get("branch", "main")
    print(f"\n== {name} ({repo}@{branch})", flush=True)
    work = Path(tempfile.mkdtemp(prefix=f"{name}-"))
    try:
        auth = f"x-access-token:{gh_token}@" if gh_token else ""
        env = dict(os.environ, CLOUDFLARE_ACCOUNT_ID=account_id)
        run(["git", "clone", "--depth", "1", "--branch", branch, f"https://{auth}github.com/{repo}.git", str(work)], ROOT, env)
        run(["npm", "ci" if (work / "package-lock.json").exists() else "install", "--no-audit", "--no-fund"], work, env)
        run(["npm", "install", "--no-save", "--no-audit", "--no-fund", f"github:{CORE_REPO}#{sha}"], work, env)
        run(["npm", "test", "--if-present"], work, env)
        run(["npx", "--yes", "wrangler@4", "deploy", "--var", f"BOT_CORE_SHA:{sha}"], work, env)
        if entry.get("health_url") and not wait_healthy(entry["health_url"], sha):
            raise RuntimeError("did not report a healthy /healthz with the new bot-core sha")
        print(f"   {name}: ok", flush=True)
        return True
    except Exception as e:
        print(f"   {name}: FAILED: {e}", flush=True)
        return False
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    if not os.environ.get("CLOUDFLARE_API_TOKEN"):
        sys.exit("CLOUDFLARE_API_TOKEN is not set (see .github/workflows/propagate-workers.yml)")
    sha = os.environ.get("BOT_CORE_SHA") or os.environ.get("GITHUB_SHA")
    if not sha:
        sys.exit("BOT_CORE_SHA / GITHUB_SHA not set")
    cfg = json.loads((ROOT / "workers-fleet.json").read_text(encoding="utf-8"))
    gh = os.environ.get("FLEET_GITHUB_TOKEN", "")

    if not deploy(cfg["canary"], sha, cfg["account_id"], gh):
        sys.exit("canary failed: fan-out blocked, no fleet bot was touched")
    failed = [e["name"] for e in cfg.get("fleet", []) if not deploy(e, sha, cfg["account_id"], gh)]
    if failed:
        sys.exit(f"fan-out finished with failures: {', '.join(failed)}")
    print("\nfan-out complete")


if __name__ == "__main__":
    main()
