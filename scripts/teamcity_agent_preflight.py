#!/usr/bin/env python3
import argparse
import sys
import time
from pathlib import Path
from typing import Any

import requests

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.main.api.specs.request_specs import RequestSpecs


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Authorize the requested number of CI TeamCity agents and wait until "
            "all are ready."
        )
    )
    parser.add_argument(
        "--count",
        required=True,
        type=int,
        choices=(1, 2, 3),
        help="Number of TeamCity agents to prepare.",
    )
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    expected_count = args.count

    deadline = time.monotonic() + args.timeout
    base_url = f"{RequestSpecs._server_url()}/app/rest"
    headers = RequestSpecs.admin_auth_spec(csrf=False)
    headers["Accept"] = "application/json"
    last_agents: list[dict[str, Any]] = []

    while time.monotonic() < deadline:
        response = requests.get(
            f"{base_url}/agents",
            params={
                "locator": "authorized:any,defaultFilter:false",
                "fields": "agent(id,name,authorized,connected,enabled)",
            },
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()
        last_agents = response.json().get("agent", [])
        candidates = sorted(
            (agent for agent in last_agents if agent.get("connected")),
            key=lambda item: (
                str(item.get("name") or ""),
                str(item.get("id") or ""),
            ),
        )[:expected_count]

        for agent in candidates:
            if agent.get("authorized"):
                continue
            authorize = requests.put(
                f"{base_url}/agents/id:{agent['id']}/authorized",
                data="true",
                headers={
                    **headers,
                    "Accept": "text/plain",
                    "Content-Type": "text/plain",
                },
                timeout=20,
            )
            authorize.raise_for_status()

        ready_agents = [
            agent
            for agent in candidates
            if agent.get("authorized")
            and agent.get("connected")
            and agent.get("enabled")
        ]
        if len(ready_agents) == expected_count:
            ready_names = sorted(
                str(agent.get("name") or agent.get("id")) for agent in ready_agents
            )
            print(
                "TeamCity agents are authorized, connected, and enabled: "
                f"{', '.join(ready_names)}."
            )
            return 0
        time.sleep(1)

    print(
        f"{expected_count} TeamCity agents did not become ready. "
        f"Last agents: {last_agents}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
