# Vapourizer

Async web crawler + content extractor. Vapourizer crawls documentation sites using `crawl4ai`, then streams each page into an LLM (via Pydantic AI + Anthropic) to extract concise, high–value markdown. Results are written incrementally to `out/` as a single markdown file.

## Features
- **Configurable crawling** using `BFSDeepCrawlStrategy` with URL patterns, allowed domains, and content-type filters (`util/constants.py`).
- **LLM-powered extraction** using `pydantic-ai` with Anthropic provider (`llm/agent.py`, `llm/prompts.py`).
- **Streaming output** to a timestamped markdown file (`util/file_writer.py`).
- **Simple entry point** in `main.py` with example target URL.

## Project Structure
- **`main.py`** – Entry point; runs a crawl and streams LLM-extracted output.
- **`crawlers/web_crawler.py`** – `WebCrawler` built on `crawl4ai` with deep crawling, filters, and utility helpers.
- **`llm/agent.py`** – Pydantic AI agent configuration; loads secrets from `/etc/secrets/*.json` and builds Anthropic client.
- **`llm/prompts.py`** – System prompt that guides extraction (markdown-focused).
- **`util/constants.py`** – Crawl filters: `URL_PATTERNS`, `ALLOWED_DOMAINS`, `ALLOWED_CONTENT_TYPES`.
- **`util/file_writer.py`** – Helpers to initialize and append to streaming markdown.
- **`out/`** – Generated output files (gitignored).

## Requirements
- Python 3.11+
- uv (Python package manager)
- Network access to your Anthropic-compatible endpoint

The project declares dependencies in `pyproject.toml` and pins them in `uv.lock`:
- `crawl4ai` (crawling)
- `pydantic-ai` (agent orchestration)

Note: The code imports `anthropic` and `httpx`. These are typically installed as transitive deps, but if you see `ImportError`, add them explicitly (see Troubleshooting).

## Setup

### 1) Create and activate a virtual environment (uv)
```bash
# Install uv if needed: https://docs.astral.sh/uv/
uv venv
source .venv/bin/activate  # macOS/Linux
```

### 2) Install dependencies
```bash
uv sync
```

If you are on a restricted network or private registry, `pyproject.toml` includes a configured index under `[tool.uv.index]`. Ensure your environment can reach it (credentials/proxy as required).

### 3) Configure LLM secrets (/etc/secrets)
The agent loads configuration from a JSON file on disk (see `llm/agent.py`). The module docstring references `/etc/secrets/vapourizer_llm.json`, while the current code’s `CONFIG_PATH` is `/etc/secrets/.json`. You have two options:

- Recommended: Create `/etc/secrets/vapourizer_llm.json` and update `CONFIG_PATH` in `llm/agent.py` to that path.
- Or, create the file at `/etc/secrets/.json` to match the current code as-is.

Required keys in the JSON:
```json
{
  "base_url": "https://api.anthropic.com",         
  "api_key": "sk-ant-...",                         
  "headers": { "x-custom-header": "value" },     
  "ca_certs_path": "/etc/ssl/certs/ca-bundle.crt" 
}
```
- **base_url**: Anthropic API base or your Anthropic-compatible gateway.
- **api_key**: Your Anthropic API key (or gateway key).
- **headers** (optional): Additional headers if your gateway requires them.
- **ca_certs_path** (optional): Path to CA bundle if corporate TLS interception is used.

Security hardening (optional):
```bash
sudo mkdir -p /etc/secrets
sudo sh -c 'umask 077 && cat > /etc/secrets/vapourizer_llm.json'
# paste JSON, then Ctrl+D
sudo chmod 600 /etc/secrets/vapourizer_llm.json
```

## Usage

Run the crawler with the example target URL from `main.py`:
```bash
uv run python main.py
```

You’ll see:
- A printed crawler configuration summary
- Per-page extraction logs
- Streaming markdown written to `out/<base>_<timestamp>.md`

### Change the target URL
Edit `main.py` and set `target_url`:
```python
target_url = "https://digitaltoolkit.livingdesign.walmart.com/develop/react/"
# or another docs site
```

### Tune crawl behavior
Edit `util/constants.py`:
- **`URL_PATTERNS`**: Only follow URLs that match these wildcard patterns.
- **`ALLOWED_DOMAINS`**: Only crawl these domains.
- **`ALLOWED_CONTENT_TYPES`**: Only keep specific content types (e.g., `text/html`).

Or change constructor args in `main.py` when creating `WebCrawler`:
```python
crawler = WebCrawler(
    max_depth=2,
    include_external=True,
    verbose=True,
)
```

## Output
Files are created under `out/` and look like:
```
out/walmart_design_toolkit_20241021_153000.md
```
Each crawled page is appended as a section with the LLM-extracted markdown.

## Troubleshooting
- **Config file not found**: The agent logs `Configuration file not found: /etc/secrets/.json`.
  - Ensure the JSON exists at the path referenced by `CONFIG_PATH` in `llm/agent.py`.
- **Missing config fields**: Error like `Missing required configuration fields: ['base_url', 'api_key']`.
  - Provide all required keys in the JSON file.
- **TLS/CA errors**: If your network uses a custom CA, set `ca_certs_path` to a valid bundle file.
- **ImportError: anthropic/httpx not found**:
  - Add explicitly and resync:
    ```bash
    uv add anthropic httpx
    uv sync
    ```
- **Large page errors during extraction**: You may see logs like “Error extracting information …”.
  - Reduce `max_depth`, narrow `URL_PATTERNS`, or filter pages more aggressively. You can also skip specific pages.

## Notes
- Hitting Anthropic (or a compatible gateway) incurs API costs—use filters to limit crawl scope.
- `out/` is gitignored (`.gitignore`).

## License
Not specified. Add a license if you plan to share or publish.

