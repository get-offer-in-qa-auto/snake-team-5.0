#!/usr/bin/env python3
import argparse
import sys
import time

import requests

from src.main.api.specs.request_specs import RequestSpecs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Authorize the CI TeamCity agent and wait until it is connected."
    )
    parser.add_argument("--name", required=True, help="Expected TeamCity agent name")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    deadline = time.monotonic() + args.timeout
    base_url = f"{RequestSpecs._server_url()}/app/rest"
    headers = RequestSpecs.admin_auth_spec(csrf=False)
    headers["Accept"] = "application/json"
    last_agents: object = None

    while time.monotonic() < deadline:
        response = requests.get(
            f"{base_url}/agents",
            params={"locator": "authorized:any,defaultFilter:false"},
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()
        last_agents = response.json().get("agent", [])
        agent = next(
            (item for item in last_agents if item.get("name") == args.name), None
        )
        if agent is None:
            time.sleep(1)
            continue

        agent_id = agent["id"]
        if not agent.get("authorized"):
            authorize = requests.put(
                f"{base_url}/agents/id:{agent_id}/authorized",
                data="true",
                headers={
                    **headers,
                    "Accept": "text/plain",
                    "Content-Type": "text/plain",
                },
                timeout=20,
            )
            authorize.raise_for_status()
            time.sleep(1)
            continue

        if agent.get("connected") and agent.get("enabled"):
            print(
                f"TeamCity agent {args.name!r} is authorized, connected, and enabled."
            )
            return 0
        time.sleep(1)

    print(
        f"TeamCity agent {args.name!r} did not become ready. Last agents: {last_agents}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
