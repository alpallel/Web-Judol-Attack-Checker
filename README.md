# judol-checker

[![Tests](https://github.com/alpallel/Web-Judol-Attack-Checker/workflows/Tests/badge.svg)](https://github.com/alpallel/Web-Judol-Attack-Checker/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Small tool to check all URLs listed in a sitemap.xml to see whether the page content contains the string "judol", "gacor", etc (case-insensitive). This is handy for detecting mass defacement or unexpected replacements.

## Files created
- `check_judol.py` — main script (Python 3). Parses sitemap, fetches pages concurrently, writes JSON report.
- `requirements.txt` — minimal dependency (`requests`).

## Quick start (Windows cmd.exe)

1. Open a cmd prompt and change to the folder containing your sitemap (or place `sitemap.xml` in the same folder as the script). Example if the files are in Downloads:

```cmd
cd %USERPROFILE%\Downloads
```

2. Create a venv and install requirements:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the checker (defaults assume `sitemap.xml` in current dir):

```cmd
python check_judol.py --sitemap sitemap.xml --output judol_report.json --concurrency 10 --timeout 10
```
### &emsp; Concurrency (default: 10)
  * Recommended: 5-20 depending on your use case
    - 5-10: Safe, conservative approach. Good for shared servers or respecting rate limits 
    - 10-20: Balanced speed vs. resource usage. Good for most scenarios 
    - 20+: Only if you have a powerful machine and the target servers can handle it
    - Avoid 100+: Will likely get rate-limited or IP-blocked by servers


### &emsp; Timeout (default: 10 seconds)
  * Recommended: 10-30 seconds
    - 5 seconds: Too short, may timeout on slow servers
    - 10 seconds: Good default (what you have). Catches most unresponsive servers
    - 15-20 seconds: Better for international servers or slower connections
    - 30+ seconds: Only if targeting very slow services

4. After completion you will see a summary on the console and a full report saved to `judol_report.json`.

## Output format

The `judol_report.json` contains:

- `sitemap` — the sitemap path used
- `count` — number of URLs checked
- `results` — list of objects for each URL with keys:
  - `url`, `ok` (bool), `status_code` (if ok), `has_judol` (bool), `exact_judol` (bool), `length` (body length), or `error` on failure.

## Notes & suggestions

- The script checks for the substrings: "judol", "gacor", "togel", and "maxwin" (case-insensitive).
- To add or change keywords, edit the tuple in `fetch_url()` function.
- Increase `--concurrency` for faster runs on large sitemaps (recommended: 10-20), but be mindful of target server load.
- Adjust `--timeout` if you get many timeouts on slow servers (recommended: 10-30 seconds).
- If you need HTTPS certificate or proxy options, the script can be extended to pass session settings.

## License

MIT License - see [LICENSE](LICENSE) for details.
