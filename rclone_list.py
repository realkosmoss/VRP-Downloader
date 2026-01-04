from rclone_fp import make_rclone

import json, logging, base64
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

CONFIG_PATH = SCRIPT_DIR / "vrp-public.json"

GAME_LIST = None
GAME_LIST_PATH = SCRIPT_DIR / "VRP-GameList.txt"
GAME_LIST_PATH_FALLBACK = SCRIPT_DIR / "meta" / "VRP-GameList.txt"

META_PATH = SCRIPT_DIR / "meta.7z"

def _fucking_update_shit():
    global GAME_LIST
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
        
    base_url: str = config["baseUri"]
    encoded_password = config["password"]
    password = base64.b64decode(encoded_password).decode("utf-8").strip()

    if GAME_LIST_PATH.exists():
        GAME_LIST = GAME_LIST_PATH.open("r", encoding="utf-8", errors="ignore").read().splitlines()
    elif GAME_LIST_PATH_FALLBACK.exists():
        GAME_LIST = GAME_LIST_PATH_FALLBACK.open("r", encoding="utf-8", errors="ignore").read().splitlines()
    else:
        if not META_PATH.exists():
            resp = session.get(base_url.rstrip("/") + "/meta.7z", stream=True)
            resp.raise_for_status()
            with META_PATH.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        raise FileNotFoundError(f"VRP-GameList.txt not found, fucking decrypt meta.7z using this fucking password: {password}")
    
if __name__ == "__main__":
    _fucking_update_shit()
    while True:
        foundfuckinggame = None
        shitassgame = input("Search for a game: ").strip()
        if not shitassgame:
            print("what? you really input nothing. you fucking serious?")
            break

        q = shitassgame.lower()
        for line in GAME_LIST:
            if not line:
                continue
            title, display, *_ = line.split(";")

            if title.lower() == q:
                foundfuckinggame = [display]
                break
            elif q in title.lower():
                if foundfuckinggame is None:
                    foundfuckinggame = []
                foundfuckinggame.append(display)

        if foundfuckinggame:
            for shitgame in foundfuckinggame:
                print("Found a fucking game:", shitgame)
            print("Just type the game name(s) into the downloader man")
        else:
            print("No fucking games found, what the fuck man")