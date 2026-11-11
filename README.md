# Demo: agente MCP per data quality (DB → ServiceNow)

Dimostra come un agente (Claude) possa usare due MCP server — uno su un
database SQLite, uno custom su ServiceNow — per rilevare problemi di data
quality e aprire ticket automaticamente, senza alcun codice di
orchestrazione: l'intelligenza è nell'agente, i server MCP sono solo
"mani e occhi".

## Setup

1. Crea il database demo (dati intenzionalmente "sporchi"):

   ```bash
   python data/seed_db.py
   ```

2. Configura le credenziali ServiceNow (istanza PID):

   ```bash
   cp .env.example .env
   # poi edita .env con SNOW_INSTANCE_URL, SNOW_USER, SNOW_PASSWORD reali
   ```

3. Installa le dipendenze del server ServiceNow:

   ```bash
   pip install mcp httpx python-dotenv
   ```

   Il server SQLite (`mcp-server-sqlite`) viene eseguito al volo con `uvx`
   (serve [uv](https://docs.astral.sh/uv/) installato), nessuna installazione
   manuale necessaria. `.mcp.json` lo lancia con `--with "mcp<2"` perché il
   package non è compatibile con l'SDK `mcp` 2.x (API `FastMCP` rimossa).

   Su Windows, se `pip install uv` non mette `uvx` nel PATH, usa il percorso
   assoluto di `uvx.exe` (es. `...\Python\Python312\Scripts\uvx.exe`) come
   `command` in `.mcp.json` al posto di `"uvx"`.

4. Apri questa cartella in Claude Code (o Claude Desktop): i due server
   MCP in `.mcp.json` vengono caricati automaticamente.

## Demo

Chiedi all'agente, ad esempio:

> Analizza la qualità dei dati nel database e apri i ticket necessari in
> ServiceNow, evitando duplicati.

L'agente:
1. interroga `customers`/`orders` via il tool `sqlite` per i 4 controlli
   descritti in [CLAUDE.md](CLAUDE.md) (completezza, duplicati,
   formato/validità, integrità referenziale);
2. per ogni anomalia trovata, chiama `search_incidents` sul server
   `servicenow` per verificare che non esista già un ticket con lo stesso
   `correlation_id`;
3. se non esiste, chiama `create_incident` per aprirlo.

Ripetendo lo stesso prompt una seconda volta, l'agente non deve creare
ticket duplicati (grazie al controllo `search_incidents` +
`correlation_id`) — buon modo per mostrare l'idempotenza del flusso.

## Risultato

I 4 ticket aperti automaticamente dall'agente, uno per categoria di anomalia:

![Lista incident creati dall'agente](screenshots/incident_list.jpg)

Dettaglio di un incident, con la descrizione generata dall'agente:

![Dettaglio di un incident](screenshots/incident_detail.jpg)

## Struttura

- `data/seed_db.py` — genera `data/crm.db` con dati sporchi.
- `mcp-servicenow/server.py` — MCP server custom per la Table API di
  ServiceNow (`search_incidents`, `create_incident`).
- `.mcp.json` — registra i due MCP server (`sqlite`, `servicenow`).
- `CLAUDE.md` — regole di data quality che l'agente applica.
