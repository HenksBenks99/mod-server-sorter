#!/usr/bin/env python3
"""
ForgeModSearch - Mod Separation Tool v3.3.0
Analisi Statica + Modrinth API (Tier 1) + Fallback CurseForge API v1 (Tier 2) + Cache locale
"""

import os
import sys
import shutil
import zipfile
import json
import urllib.parse
import urllib.request
import re
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    import tomllib
except ImportError:
    print("Errore: tomllib non disponibile. Installa Python 3.11+ o usa pip install tomli")
    sys.exit(1)


# ============================================================================
# CONFIGURAZIONE GENERALE E API
# ============================================================================

CACHE_FILE = "cf_cache.json"

# Modrinth
MODRINTH_BASE_URL = "https://api.modrinth.com/v2/project"
MODRINTH_HEADERS = {
    'User-Agent': 'ForgeModSearch/3.3.0 (Riccardo.GitHub.Tool)',
}

# CurseForge API
CURSEFORGE_API_KEY = "REDACTED_CURSEFORGE_API_KEY"
CURSEFORGE_BASE_URL = "https://api.curseforge.com/v1"
CURSEFORGE_GAME_ID = 432   # Minecraft
CURSEFORGE_CLASS_ID = 6   # Solo Mod

# Mappatura e filtri categorie CurseForge
CURSEFORGE_CATEGORIES = {
    421: "API and Library",
    414: "Player Transport",
    423: "Map and Information",
    424: "Cosmetic",
    436: "Food",
    6814: "Optimization/Performance",
    425: "Utility / Miscellaneous",
}

# Categorie CurseForge che identificano mod strettamente Client-Only
CURSEFORGE_STRICT_CLIENT_CATS = {
    423,   # Map and Information (Minimappe)
    6814,  # Optimization / Performance (Shaders, Sodium, Embeddium)
}


# ============================================================================
# BLACKLIST E WHITELIST
# ============================================================================

LIBRARY_DEPENDENCIES = {
    "kotlinforforge", "geckolib", "polytone", "modmenu", "architectury",
    "cloth-config", "balm", "puzzleslib", "resourcefullib", "cristellib"
}

CLIENT_ONLY_BLACKLIST = {
    "sodium", "rubidium", "iris", "embeddium", "embed", "ophiurei",
    "oculus", "turbo", "turbo-api", "optifine",
    "journeymap", "xaerominimap", "xaeroworldmap",
    "appleskin", "inventorytweaks", "mousewheelie", "controlling",
    "ferritecore", "animatica", "cameraoverhaul", "distant-horizons", "dynamic-fps",
    "enhanced-boss-bars", "entity-model-features", "entity-texture-features",
    "fallingleaves", "flerovium", "held-item-tooltips", "holdmyitems",
    "modelfix", "mouse-tweaks", "presence-footsteps",
    "sodium-dynamic-lights", "sodium-options-api", "sound-physics-remastered",
    "sounds", "immerse-ui", "better-advancements", "better-ping-display",
    "betteradvancements", "betterpingdisplay", "distanthorizons", "dynamicfps",
    "enhancedbossbars", "entitymodelfeatures", "entitytexturefeatures",
    "immediatelyfast", "immersiveui", "mousetweaks", "presencefootsteps",
    "sodiumdynamiclights", "sodiumoptionsapi", "soundphysicsremastered",
}

CLIENT_WORDS_IN_SERVER_MODS = {
    "balm", "architectury", "cloth-config", "modmenu",
}

# Mod che pur avendo client_side=required o tag UI sono essenziali/compatibili con Server
BOTH_WHITELIST = {
    "jei", "rei", "emi", "jade", "entity_model_features", "entity_texture_features",
    "fallingleaves", "helditemtooltips", "holdmyitems", "mouse-tweaks", "mousetweaks",
    "presencefootsteps", "soundphysicsremastered", "sounds", "immerse-ui",
    "betterpingdisplay", "inventorytweaks", "mousewheelie", "controlling",
    "ferritecore", "distant-horizons", "dynamicfps", "tconjei", "searchables",
    "stackrefill", "fabric-api", "architectury", "balm", "cloth-config",
    "modmenu", "kotlinforforge", "geckolib", "polytone", "yet-another-config-lib-v3",
    "puzzleslib", "let-s-do", "handcrafted", "cristellib", "mdm", "resourcefullib",
    "moonlight", "octolib", "obscure-api", "player-animation-lib-forge",
    "playeranimatorapi", "tinkersinnovation", "mimimod", "tinkerbettercombat",
    "tinkersjewelry", "tinkersdelight", "create-tinkers-compat", "create-ore-excavation",
    "create-struct-arise", "create-questing", "create-connected", "create-deco",
    "create-numismatics", "create-addition", "tconstruct", "mantle", "l2library",
    "ldlib", "decorative-blocks", "delightful", "does-it-tick", "dynamic-trees",
    "dynamic-trees-plus", "immersive-weathering", "iter-rpg", "waystones", "create"
}


# ============================================================================
# GESTIONE CACHE LOCALE (cf_cache.json)
# ============================================================================

def load_cache() -> dict:
    cache_path = Path(__file__).parent / CACHE_FILE
    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def update_cache(slug: str, data: dict):
    cache_path = Path(__file__).parent / CACHE_FILE
    try:
        cache = load_cache()
        cache[slug] = data
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"    [WARN] Errore salvataggio cache: {e}")


# ============================================================================
# FUNZIONI DI ANALISI STATICA
# ============================================================================

def clean_mod_slug(filename: str) -> str:
    """Estrae uno slug pulito dal nome del file .jar."""
    name = filename.replace('.jar', '')
    name = re.sub(r'[-_+](forge|fabric|neoforge).*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[-_+]v?\d+(\.\d+)*.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\+build\.\d+', '', name)
    name = re.sub(r'\+mc\.\d+\.\d+', '', name)
    name = re.sub(r'[^a-zA-Z0-9\-_]', '', name)
    name = re.sub(r'[-_]+', '-', name).strip('-')
    return name.lower().strip()

def classify_mod_by_name(mod_id: str) -> str:
    mod_id_lower = mod_id.lower()
    for lib in LIBRARY_DEPENDENCIES:
        if lib in mod_id_lower:
            return "BOTH"
    for keyword in CLIENT_ONLY_BLACKLIST:
        if keyword in mod_id_lower:
            for exception in CLIENT_WORDS_IN_SERVER_MODS:
                if exception in mod_id_lower:
                    return "BOTH"
            return "CLIENT_ONLY"
    return "UNKNOWN"

def parse_fabric_mod_json(zip_path: Path) -> Optional[str]:
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            with z.open('fabric.mod.json') as f:
                data = json.load(f)
            env = data.get('environment', '')
            if env in ('client', 'server', 'both'):
                return env
            entrypoints = data.get('entrypoints', {})
            if 'client' in entrypoints and 'server' not in entrypoints:
                return 'client'
            elif 'server' in entrypoints and 'client' not in entrypoints:
                return 'server'
            elif 'client' in entrypoints and 'server' in entrypoints:
                return 'both'
            return 'both'
    except Exception:
        return None

def parse_toml_mods(zip_path: Path) -> Optional[str]:
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            toml_path = 'META-INF/mods.toml'
            if toml_path not in z.namelist():
                toml_path = 'META-INF/neoforge.mods.toml'
            if toml_path not in z.namelist():
                return None
            with z.open(toml_path) as f:
                content = f.read().decode('utf-8')
                toml_data = tomllib.loads(content)
            mod = toml_data.get('mod', {})
            display_name = mod.get('displayTest', '').lower()
            if display_name:
                return display_name
            mixin_config = mod.get('mixinConfig', {})
            mixin_sided = mixin_config.get('serverSidedProvider', None)
            if mixin_sided:
                side = mixin_sided.get('name', '').lower()
                if side in ('client', 'server'):
                    return side
            return 'both'
    except Exception:
        return None

def analyze_mod_jar(jar_path: Path) -> dict:
    result = {
        'path': str(jar_path),
        'name': jar_path.stem,
        'status': 'UNKNOWN',
        'reason': 'Nessuna info statica',
        'confidence': 0.0,
        'display_test': None,
        'config_file': None,
    }
    mod_id_lower = result['name'].lower()
    
    # 1. Dipendenze note
    for lib in LIBRARY_DEPENDENCIES:
        if lib in mod_id_lower:
            result['status'] = 'BOTH'
            result['reason'] = f'Libreria essenziale/dipendenza: {lib}'
            result['confidence'] = 0.98
            return result
    
    # 2. Controllo file interni
    config_patterns = ['fabric.mod.json', 'META-INF/mods.toml', 'META-INF/neoforge.mods.toml']
    found_config = None
    for pattern in config_patterns:
        try:
            with zipfile.ZipFile(jar_path, 'r') as z:
                if pattern in z.namelist():
                    found_config = pattern
                    break
        except Exception:
            continue
    
    if found_config:
        result['config_file'] = found_config
        if found_config == 'fabric.mod.json':
            env = parse_fabric_mod_json(jar_path)
            if env == 'client':
                result['status'] = 'CLIENT_ONLY'
                result['reason'] = 'fabric.mod.json: environment="client"'
                result['confidence'] = 0.95
            elif env == 'server':
                result['status'] = 'SERVER_ONLY'
                result['reason'] = 'fabric.mod.json: environment="server"'
                result['confidence'] = 0.95
            elif env == 'both':
                result['status'] = 'BOTH'
                result['reason'] = 'fabric.mod.json: environment="both"'
                result['confidence'] = 0.90
        else:
            for keyword in CLIENT_ONLY_BLACKLIST:
                if keyword in mod_id_lower:
                    result['status'] = 'CLIENT_ONLY'
                    result['reason'] = f'Blacklist locale: {keyword}'
                    result['confidence'] = 0.95
                    return result
            env = parse_toml_mods(jar_path)
            if env == 'client':
                result['status'] = 'CLIENT_ONLY'
                result['reason'] = 'TOML: displayTest/serverSided="client"'
                result['confidence'] = 0.85
            elif env == 'server':
                result['status'] = 'SERVER_ONLY'
                result['reason'] = 'TOML: displayTest/serverSided="server"'
                result['confidence'] = 0.85
            elif env == 'both':
                result['status'] = 'BOTH'
                result['reason'] = 'TOML: displayTest="both"'
                result['confidence'] = 0.80
                result['display_test'] = 'both'
    
    if result['status'] == 'UNKNOWN':
        res_by_name = classify_mod_by_name(result['name'])
        if res_by_name != 'UNKNOWN':
            result['status'] = res_by_name
            result['reason'] = f'Rilevamento per parola chiave: {res_by_name}'
            result['confidence'] = 0.60
            
    return result


# ============================================================================
# API MODRINTH (TIER 1)
# ============================================================================

def search_modrinth(slug: str) -> dict:
    try:
        url = f"{MODRINTH_BASE_URL}/{slug}"
        req = urllib.request.Request(url, headers=MODRINTH_HEADERS, method='GET')
        with urllib.request.urlopen(req, timeout=8) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"    [WARN] Errore HTTP Modrinth {e.code}: {e.reason}")
    except Exception as e:
        print(f"    [WARN] Modrinth non raggiungibile: {e}")
    return {}

def classify_modrinth(mod_data: dict) -> tuple:
    title = mod_data.get('title', '') or mod_data.get('name', '')
    slug = mod_data.get('slug', '')
    client_side = mod_data.get('client_side', '')
    server_side = mod_data.get('server_side', '')

    mod_lower = title.lower()
    if mod_lower in BOTH_WHITELIST or slug.lower() in BOTH_WHITELIST:
        return 'BOTH', f'WHITELIST: {title}', 0.98

    if client_side in ('required', 'optional') and server_side == 'unsupported':
        return 'CLIENT_ONLY', f'Modrinth: client={client_side}, server={server_side}', 0.95
    elif client_side == 'unsupported' and server_side in ('required', 'optional'):
        return 'SERVER_ONLY', f'Modrinth: client={client_side}, server={server_side}', 0.95
    elif client_side != 'unsupported' and server_side != 'unsupported':
        return 'BOTH', f'Modrinth: supporta client e server', 0.95

    return 'UNKNOWN', 'Modrinth: dati non conclusivi', 0.0


# ============================================================================
# API CURSEFORGE (TIER 2 - FALLBACK)
# ============================================================================

def search_curseforge(slug: str) -> dict:
    try:
        params = urllib.parse.urlencode({
            'gameId': CURSEFORGE_GAME_ID,
            'classId': CURSEFORGE_CLASS_ID,
            'sortField': 2,        # Ordina per popolarità
            'sortOrder': 'desc',
            'searchFilter': slug,
            'pageSize': 5
        })
        url = f"{CURSEFORGE_BASE_URL}/mods/search?{params}"
        req = urllib.request.Request(url, headers={
            'Accept': 'application/json',
            'x-api-key': CURSEFORGE_API_KEY
        })
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
            mods = data.get('data', [])
            if not mods:
                return {}
            # Match dello slug più affine
            matched_mod = mods[0]
            clean_input = slug.lower().replace("-", "")
            for m in mods:
                if clean_input in m.get('slug', '').replace("-", ""):
                    matched_mod = m
                    break
            return matched_mod
    except Exception as e:
        print(f"    [WARN] Errore CurseForge API: {e}")
        return {}

def classify_curseforge(cf_mod: dict) -> tuple:
    name = cf_mod.get('name', '')
    slug = cf_mod.get('slug', '')
    cat_ids = [c.get('id') for c in cf_mod.get('categories', [])]

    if name.lower() in BOTH_WHITELIST or slug.lower() in BOTH_WHITELIST:
        return 'BOTH', f'WHITELIST: {name}', 0.98

    # Se include esplicitamente "API and Library" (421) o "Player Transport" (414) è BOTH
    if 421 in cat_ids or 414 in cat_ids:
        return 'BOTH', f'CurseForge: Libreria/Trasporto verificato ({name})', 0.92

    # Controllo categorie Client-Only
    if any(cid in CURSEFORGE_STRICT_CLIENT_CATS for cid in cat_ids):
        detected = [CURSEFORGE_CATEGORIES.get(cid, str(cid)) for cid in cat_ids if cid in CURSEFORGE_STRICT_CLIENT_CATS]
        return 'CLIENT_ONLY', f'CurseForge Client Cat: {", ".join(detected)}', 0.92

    return 'BOTH', f'CurseForge Verificata ({name})', 0.85


# ============================================================================
# PIPELINE UNIFICATA CON CACHE E DECISION ENGINE
# ============================================================================

def analyze_mod(jar_path: Path, cache: dict) -> dict:
    print(f"\n  [{jar_path.name}]")
    result = analyze_mod_jar(jar_path)
    
    print(f"    [STATICA] {result['status']} ({result['confidence']*100:.0f}%) -> {result['reason']}")
    
    # Verifica Online necessaria se UNKNOWN o con confidenza inferiore a 0.90 (es. displayTest="both")
    if result['status'] == 'UNKNOWN' or result['confidence'] < 0.90:
        slug = clean_mod_slug(jar_path.name)
        if not slug:
            return result
        
        # 1. Verifica Cache
        if slug in cache:
            c_entry = cache[slug]
            print(f"    [CACHE] Dati caricati per '{slug}' (Fonte: {c_entry.get('source', '').upper()})")
            result['status'] = c_entry['status']
            result['reason'] = c_entry['reason']
            result['confidence'] = c_entry['confidence']
            result['source'] = c_entry.get('source', 'cache')
            return result

        # 2. Tier 1: Modrinth
        print(f"    [ONLINE] Interrogo Modrinth per: '{slug}'...")
        modrinth_data = search_modrinth(slug)
        if modrinth_data:
            st, rs, conf = classify_modrinth(modrinth_data)
            if st != 'UNKNOWN':
                result.update({'status': st, 'reason': rs, 'confidence': conf, 'source': 'modrinth'})
                update_cache(slug, {'status': st, 'reason': rs, 'confidence': conf, 'source': 'modrinth'})
                print(f"    [MODRINTH] {st} ({conf*100:.0f}%) - {rs}")
                return result

        # 3. Tier 2: CurseForge Fallback
        print(f"    [ONLINE] Modrinth non conclusivo. Fallback su CurseForge per: '{slug}'...")
        cf_data = search_curseforge(slug)
        if cf_data:
            st, rs, conf = classify_curseforge(cf_data)
            if st != 'UNKNOWN':
                result.update({'status': st, 'reason': rs, 'confidence': conf, 'source': 'curseforge'})
                update_cache(slug, {'status': st, 'reason': rs, 'confidence': conf, 'source': 'curseforge'})
                print(f"    [CURSEFORGE] {st} ({conf*100:.0f}%) - {rs}")
                return result

        print(f"    [FALLBACK] Nessuna API conclusiva. Mantengo risultato statico.")
        result['source'] = 'static'

    return result


# ============================================================================
# PROCESSAMENTO MODPACK & REPORT
# ============================================================================

def process_modpack(input_folder: Path, output_folder: Path, dry_run: bool = False, list_only: bool = False):
    print(f"\n{'='*70}\n  ForgeModSearch - Mod Separation Tool v3.3.0\n{'='*70}\n")
    
    if not input_folder.exists():
        print(f"Errore: Cartella '{input_folder}' non trovata.")
        sys.exit(1)
        
    server_mods_folder = output_folder / 'Server Mod'
    if not dry_run and not list_only:
        server_mods_folder.mkdir(parents=True, exist_ok=True)
        
    cache = load_cache()
    jar_files = sorted([f for f in input_folder.iterdir() if f.is_file() and f.suffix.lower() == '.jar'])
    print(f"Trovate {len(jar_files)} mod .jar da analizzare...")

    results = []
    stats = {'total': 0, 'client_only': 0, 'server_only': 0, 'both': 0, 'unknown': 0,
             'modrinth': 0, 'curseforge': 0, 'static': 0}

    for jar in jar_files:
        stats['total'] += 1
        res = analyze_mod(jar, cache)
        results.append(res)
        
        st = res['status']
        if st == 'CLIENT_ONLY': stats['client_only'] += 1
        elif st == 'SERVER_ONLY': stats['server_only'] += 1
        elif st == 'BOTH': stats['both'] += 1
        else: stats['unknown'] += 1
        
        src = res.get('source', 'static')
        if src in stats:
            stats[src] += 1
        else:
            stats['static'] += 1

    # Copia mod Server
    if not dry_run and not list_only:
        for r in results:
            if r['status'] in ('SERVER_ONLY', 'BOTH'):
                shutil.copy2(r['path'], server_mods_folder / Path(r['path']).name)

    # Scrittura Report
    report_path = output_folder / 'mod_analysis_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"FORGEMODSEARCH REPORT v3.3.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Totali: {stats['total']} | Client: {stats['client_only']} | Both: {stats['both']} | Server: {stats['server_only']} | Unknown: {stats['unknown']}\n")
        f.write(f"Riconoscimento -> Modrinth: {stats['modrinth']} | CurseForge: {stats['curseforge']} | Statico: {stats['static']}\n\n")
        for r in results:
            f.write(f"[{r['status']}] {r['name']}\n  Motivo: {r['reason']} (Fonte: {r.get('source','').upper()})\n\n")

    print(f"\nReport salvato in: {report_path}")
    print(f"Server-Ready: {stats['both'] + stats['server_only']} | Client-Only: {stats['client_only']} | Unknown: {stats['unknown']}")

def main():
    parser = argparse.ArgumentParser(description='Separatore di mod Client/Server per Minecraft.')
    parser.add_argument('input_folder', type=Path, nargs='?', default=Path('./mods'))
    parser.add_argument('--output', '-o', type=Path, default=Path('./mods'))
    parser.add_argument('--dry-run', '-n', action='store_true')
    parser.add_argument('--list-only', action='store_true')
    args = parser.parse_args()

    process_modpack(args.input_folder, args.output, dry_run=args.dry_run, list_only=args.list_only)

if __name__ == '__main__':
    main()