#!/usr/bin/env python3
import argparse
import sys
import time
from typing import Any

import requests

from src.main.api.constants.teamcity import TeamCityAgentLocator, TeamCityLocator
from src.main.api.specs.request_specs import RequestSpecs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Authorize CI TeamCity agents and wait until all are connected."
    )
    parser.add_argument(
        "--name",
        required=True,
        action="append",
        help="Expected TeamCity agent name. Repeat for multiple agents.",
    )
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    expected_names = set(args.name)

    deadline = time.monotonic() + args.timeout
    base_url = f"{RequestSpecs._server_url()}/app/rest"
    headers = RequestSpecs.admin_auth_spec(csrf=False)
    headers["Accept"] = "application/json"
    last_agents: list[dict[str, Any]] = []

    while time.monotonic() < deadline:
        response = requests.get(
            f"{base_url}/agents",
            params={
                "locator": TeamCityAgentLocator.ALL_AUTHORIZATION_STATES,
                "fields": "agent(id,name,authorized,connected,enabled)",
            },
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()
        last_agents = response.json().get("agent", [])
        agents_by_name = {
            item.get("name"): item
            for item in last_agents
            if item.get("name") in expected_names
        }

        for agent in agents_by_name.values():
            if agent.get("authorized"):
                continue
            authorize = requests.put(
                f"{base_url}/agents/{TeamCityLocator.ID.build(agent['id'])}/authorized",
                data="true",
                headers={
                    **headers,
                    "Accept": "text/plain",
                    "Content-Type": "text/plain",
                },
                timeout=20,
            )
            authorize.raise_for_status()

        ready_names = {
            name
            for name, agent in agents_by_name.items()
            if agent.get("authorized")
            and agent.get("connected")
            and agent.get("enabled")
        }
        if ready_names == expected_names:
            print(
                "TeamCity agents are authorized, connected, and enabled: "
                f"{', '.join(sorted(ready_names))}."
            )
            return 0
        time.sleep(1)

    print(
        f"TeamCity agents {sorted(expected_names)!r} did not become ready. "
        f"Last agents: {last_agents}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
