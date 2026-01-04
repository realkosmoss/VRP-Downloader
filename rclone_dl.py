from rclone_fp import make_rclone

import logging
import json
import base64
import hashlib
import re
from pathlib import Path
from urllib.parse import urljoin

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "vrp-public.json"

def download(name: str):
    session = make_rclone()

    if not CONFIG_PATH.exists():
        logging.info("vrp-public.json not fucking found, fucking downloading it right now")
        _resp = session.get("https://vrpirates.wiki/downloads/vrp-public.json")
        _resp.raise_for_status()
        with CONFIG_PATH.open("wb") as f:
            f.write(_resp.content)
        config = _resp.json()
    else:
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            raise RuntimeError("Invalid vrp-public.json stupid fuck") from e
        
    base_url = config["baseUri"]
    encoded_password = config["password"]

    password = base64.b64decode(encoded_password).decode("utf-8").strip()

    md5 = hashlib.md5()
    md5.update((name + "\n").encode("utf-8"))
    hash_value = md5.hexdigest()

    index_url = f"{base_url}{hash_value}/"

    output_dir = SCRIPT_DIR / hash_value
    output_dir.mkdir(parents=True, exist_ok=True)

    r = session.get(index_url)
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
    if l_parts > 1:
        logging.info(f"Found {l_parts} fucking files")
    else:
        logging.info(f"Found {l_parts} fucking file")

    for filename in parts:
        file_url = urljoin(index_url, filename)
        output_path = output_dir / filename

        logging.info(f"Fucking downloading {filename}...")

        resp = session.get(file_url, stream=True)
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