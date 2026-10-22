import urllib.request
import urllib.parse
import json
import time

# Configurazione API CurseForge
API_KEY = "REDACTED_CURSEFORGE_API_KEY"
BASE_URL = "https://api.curseforge.com/v1"

# Mappatura delle categorie CurseForge (Minecraft gameId: 432)
CURSEFORGE_CATEGORIES = {
    421: "API and Library",
    414: "Player Transport",
    423: "Map and Information",
    424: "Cosmetic",
    436: "Food",
    6814: "Optimization/Performance",
    425: "Utility / Miscellaneous",
}

# Categorie che identificano mod strettamente Client-Only
STRICT_CLIENT_CATEGORIES = {
    423,   # Map and Information (Minimappe)
    6814,  # Optimization / Performance (Shaders, Sodium, Embeddium)
}

# Mod da testare
TEST_MODS = [
    "journeymap",
    "embeddium",
    "appleskin",
    "rubidium",
    "mouse-tweaks",
    "create",
    "applied-energistics-2",
    "jei",
    "waystones",
    "architectury-api"
]

def check_mod(mod_slug: str):
    params = urllib.parse.urlencode({
        'gameId': 432,
        'classId': 6,          # Solo Mods (esclude risorse e pacchetti)
        'sortField': 2,        # Ordina per download totali
        'sortOrder': 'desc',
        'searchFilter': mod_slug,
        'pageSize': 5
    })
    url = f"{BASE_URL}/mods/search?{params}"

    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'x-api-key': API_KEY
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            mods = data.get('data', [])

            if not mods:
                return {"status": "NOT_FOUND", "name": "Nessun risultato", "downloads": 0, "categories": []}

            # Cerca la mod corrispondente allo slug inserito, altrimenti prende la prima
            matched_mod = mods[0]
            clean_input = mod_slug.lower().replace("-", "")
            for m in mods:
                if clean_input in m.get('slug', '').replace("-", ""):
                    matched_mod = m
                    break

            cat_ids = [c.get('id') for c in matched_mod.get('categories', [])]
            
            # Identifica se client-only tramite le categorie specifiche
            is_client = any(cid in STRICT_CLIENT_CATEGORIES for cid in cat_ids)
            
            # Se la mod contiene categorie di libreria (421) o trasporto (414), non è client-only
            if 421 in cat_ids or 414 in cat_ids:
                is_client = False

            status = "CLIENT_ONLY" if is_client else "BOTH/SERVER"
            reasons = [CURSEFORGE_CATEGORIES.get(cid, str(cid)) for cid in cat_ids]

            return {
                "status": status,
                "name": matched_mod.get('name'),
                "slug": matched_mod.get('slug'),
                "downloads": matched_mod.get('downloadCount'),
                "categories": reasons
            }

    except Exception as e:
        return {"status": "ERR", "name": str(e), "downloads": 0, "categories": []}

if __name__ == "__main__":
    print(f"\n{'MOD CERCATA':<22} | {'ESITO':<12} | {'NOME RISULTATO':<25} | {'DOWNLOAD':<10} | CATEGORIE RILEVATE")
    print("-" * 105)

    for mod in TEST_MODS:
        res = check_mod(mod)
        status = res['status']
        name = str(res['name'])[:24]
        dl = f"{res['downloads']:,}"
        cats = ", ".join(res['categories'])

        print(f"{mod:<22} | {status:<12} | {name:<25} | {dl:<10} | {cats}")
        time.sleep(0.3)

    print("-" * 105 + "\n")