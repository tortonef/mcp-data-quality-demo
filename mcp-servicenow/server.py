"""MCP server minimale per ServiceNow (Table API) via REST.

Espone due tool:
- search_incidents(correlation_id): trova incident esistenti con quel
  correlation_id, per evitare di aprire ticket duplicati.
- create_incident(...): crea un nuovo incident.

Credenziali lette da env (SNOW_INSTANCE_URL, SNOW_USER, SNOW_PASSWORD),
caricate da .env se presente. Mai hardcoded.
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
    """Cerca incident esistenti per correlation_id (per evitare duplicati)."""
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
    """Crea un incident in ServiceNow. category/urgency usano i valori standard
    ServiceNow (urgency: 1=alta, 2=media, 3=bassa)."""
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
