"""Minimal MCP server for ServiceNow (Table API) over REST.

Exposes two tools:
- search_incidents(correlation_id): finds existing incidents with that
  correlation_id, to avoid opening duplicate tickets.
- create_incident(...): creates a new incident.

Credentials read from env (SNOW_INSTANCE_URL, SNOW_USER, SNOW_PASSWORD),
loaded from .env if present. Never hardcoded.
"""
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mcp.server import MCPServer

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

INSTANCE_URL = os.environ["SNOW_INSTANCE_URL"].rstrip("/")
AUTH = (os.environ["SNOW_USER"], os.environ["SNOW_PASSWORD"])
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

mcp = MCPServer("servicenow")


@mcp.tool()
def search_incidents(correlation_id: str) -> list[dict]:
    """Searches existing incidents by correlation_id (to avoid duplicates)."""
    resp = httpx.get(
        f"{INSTANCE_URL}/api/now/table/incident",
        params={
            "sysparm_query": f"correlation_id={correlation_id}",
            "sysparm_fields": "number,sys_id,short_description,state",
        },
        auth=AUTH,
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["result"]


@mcp.tool()
def create_incident(
    short_description: str,
    description: str,
    correlation_id: str,
    category: str = "software",
    urgency: str = "3",
) -> dict:
    """Creates an incident in ServiceNow. category/urgency use ServiceNow's
    standard values (urgency: 1=high, 2=medium, 3=low)."""
    resp = httpx.post(
        f"{INSTANCE_URL}/api/now/table/incident",
        json={
            "short_description": short_description,
            "description": description,
            "correlation_id": correlation_id,
            "category": category,
            "urgency": urgency,
        },
        auth=AUTH,
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()["result"]
    return {"number": result["number"], "sys_id": result["sys_id"]}


if __name__ == "__main__":
    mcp.run()
