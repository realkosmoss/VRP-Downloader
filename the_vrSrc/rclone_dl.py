from rclone_fp import make_rclone

import logging
import json
import base64
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "vrp-public.json"

API_BASE = "https://vrsrc.fyi"

def download(name: str):
    session = make_rclone()

    # Load config
    if not CONFIG_PATH.exists():
        logging.error("vrp-public.json not found")
        return

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        raise RuntimeError("Invalid vrp-public.json") from e

    base_url = config["baseUri"]
    encoded_password = config["password"]
    password = base64.b64decode(encoded_password).decode("utf-8").strip()

    # Search game via vrsrc.fyi API to get the folderhash
    logging.info(f"Searching for '{name}'...")
    import urllib.parse
    search_url = f"{API_BASE}/api/games/search?q={urllib.parse.quote(name)}&limit=20"
    r = session.get(search_url, timeout=15)
    r.raise_for_status()
    data = r.json()
    games = data.get("data", data if isinstance(data, list) else [])

    if not games:
        raise RuntimeError(f"No games found for '{name}'")

    # Filter to games with a folderhash, prefer latest version
    candidates = [g for g in games if g.get("folderhash")]
    if not candidates:
        raise RuntimeError(f"No downloadable versions found for '{name}'")

    # Pick the one with highest versioncode
    candidates.sort(key=lambda g: int(g.get("versioncode") or 0), reverse=True)
    game = candidates[0]
    folderhash = game["folderhash"]
    display_name = game.get("friendlyname") or game.get("gamename") or game.get("packagename", name)
    logging.info(f"Found: {display_name} (v{game.get('versioncode', '?')})")
    logging.info(f"Folder hash: {folderhash}")

    index_url = f"{base_url}{folderhash}/"
    output_dir = SCRIPT_DIR / folderhash
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch directory listing from CDN
    logging.info(f"Fetching {index_url}...")
    r = session.get(index_url, timeout=15)
    r.raise_for_status()

    files = re.findall(r'href="([^"]+)"', r.text)
    parts = []

    for f in files:
        if f.endswith(".7z") or ".7z." in f:
            parts.append(f)
    parts.sort()

    if not parts:
        raise RuntimeError("No fucking parts found")

    l_parts = len(parts)
    logging.info(f"Found {l_parts} fucking file{'s' if l_parts > 1 else ''}")

    for filename in parts:
        file_url = urljoin(index_url, filename)
        output_path = output_dir / filename

        logging.info(f"Fucking downloading {filename}...")

        resp = session.get(file_url, stream=True, timeout=300)
        resp.raise_for_status()
        with output_path.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    logging.info(f"Done. Decrypt using this fucking password: {password}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    rl = input("Release: ")
    download(rl)