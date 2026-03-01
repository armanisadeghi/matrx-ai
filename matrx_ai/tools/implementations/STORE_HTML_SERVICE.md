# store_html Tool — Service Investigation

## Summary

The `store_html` tool (and related `fetch_code` tool) is currently **broken** because the backend service it depends on is unreachable. This document describes the full technical picture for the engineers who own the HTML storage service.

---

## What the Tool Does

`store_html` takes an HTML string from the AI model and POSTs it to a dedicated microservice that stores it and returns a unique ID. The frontend can then use that ID to render the HTML in a viewer.

There is also a companion tool `fetch_code` that reads code from the local filesystem and returns it in various formats (it does **not** use this service — it is unrelated to the connectivity failure).

---

## The Broken Service

### Endpoint

```
POST http://d88ooscwwggkcwswg8gks4s8.matrxserver.com:3000/store-html
```

### Request payload

```json
{ "html": "<html>...</html>" }
```

### Expected response

```json
{ "id": "<some-identifier>" }
```

### Timeout

15 seconds (hardcoded in the tool implementation).

---

## Current Failure

**Error:** `ConnectTimeoutError` — the connection to `d88ooscwwggkcwswg8gks4s8.matrxserver.com:3000` times out every time.

### Connectivity investigation (as of Feb 21, 2026)

| Check | Result |
|-------|--------|
| DNS resolution | **Resolves** → `89.116.187.5` |
| Port 3000 (HTTP, the configured port) | **Unreachable** — connection times out |
| Port 443 (HTTPS) | **Reachable** (TLS handshake starts) but returns a TLS internal error |
| Port 80 (HTTP) | Not tested |

**Conclusion:** The DNS and host (`89.116.187.5`) are live (it's a Coolify server), but **nothing is listening on port 3000**. The container/service that serves the HTML storage API is either stopped, crashed, or was never deployed on this host.

---

## Code Locations

The service URL is hardcoded in **three places** — all must be updated if the URL changes:

| File | Line |
|------|------|
| `ai/tool_system/implementations/code.py` | 103 |
| `mcp_server/tools/code/web.py` | 9 |
| `matrix/ai_endpoints/tools/html_code_gen.py` | 12 |

Current hardcoded value in all three:
```python
api_url = "http://d88ooscwwggkcwswg8gks4s8.matrxserver.com:3000/store-html"
```

---

## What Needs to Be Fixed

### Option A — Restart / redeploy the existing service (if it still exists)

1. Log into the Coolify dashboard: `https://coolify.app.matrxserver.com`
2. Find the service deployed at `d88ooscwwggkcwswg8gks4s8.matrxserver.com`
3. Confirm the container is running and port 3000 is exposed/mapped correctly
4. If it was stopped, restart it

### Option B — The service no longer exists / needs to be rebuilt

The service needs to be redeployed. Based on the tool's API contract, the service must:

- Accept `POST /store-html` with JSON body `{ "html": "<string>" }`
- Return JSON `{ "id": "<identifier>" }` on success
- Be reachable at the URL (or a new URL that gets updated in all three code locations above)
- Recommend: expose via HTTPS through Coolify's reverse proxy rather than raw port 3000

### Option C — Move the URL to an environment variable (recommended regardless)

Rather than hardcoding the URL in three places, it should be read from an environment variable (e.g. `HTML_STORE_API_URL`). This makes future host changes a config change, not a code change.

---

## Related Tool

`fetch_code` (in the same `code.py` file) uses the local filesystem only — it is **not affected** by this connectivity failure.

`execute_python` and `execute_python_with_markers` run code in a subprocess — also **not affected**.
