#!/usr/bin/env python3
"""
ForgeModSearch - Mod Separation Tool v3.2.0 - INTEGRAZIONE MODRINTH MIGLIORATA
NOTA: Solo Modrinth API + classificazione statica. CurseForge rimosso.
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
# BLACKLIST E WHITELIST
# ============================================================================

LIBRARY_DEPENDENCIES = {
    "kotlinforforge",
    "geckolib",
    "polytone",
    "modmenu",
}

CLIENT_ONLY_BLACKLIST = {
    "sodium", "rubidium", "iris", "embeddium", "embed", "ophiurei",
    "oculus", "turbo", "turbo-api", "optifine",
    "journeymap", "xaerominimap", "xaeroworldmap",
    "appleskin", "inventorytweaks", "mousewheelie", "controlling",
    "ferritecore", "jei", "rei", "emi", "waystones",
    "animatica", "cameraoverhaul", "distant-horizons", "dynamic-fps",
    "enhanced-boss-bars", "entity-model-features", "entity-texture-features",
    "fallingleaves", "flerovium", "held-item-tooltips", "holdmyitems",
    "modelfix", "mouse-tweaks", "polytone", "presence-footsteps",
    "sodium-dynamic-lights", "sodium-options-api", "sound-physics-remastered",
    "sounds", "immerse-ui", "jade", "amendments", "better-advancements",
    "better-ping-display",
    "betteradvancements", "betterpingdisplay", "distanthorizons", "dynamicfps",
    "enhancedbossbars", "entitymodelfeatures", "entitytexturefeatures",
    "fallingleaves", "flerovium", "helditemtooltips", "holdmyitems",
    "immediatelyfast", "immersiveui", "modelfix", "mousetweaks",
    "presencefootsteps", "polytone", "sodiumdynamiclights", "sodiumoptionsapi",
    "soundphysicsremastered", "sounds",
}

CLIENT_WORDS_IN_SERVER_MODS = {
    "balm", "architectury", "cloth-config", "modmenu",
}

# ============================================================================
# CONFIGURAZIONE API CURSEFORGE (FALLBACK AUTOMATICO)
# ============================================================================
# CurseForge API come fallback quando Modrinth non trova la mod
CURSEFORGE_API_KEY = "REDACTED_CURSEFORGE_API_KEY"
CURSEFORGE_BASE_URL = "https://api.curseforge.com/v1"
CURSEFORGE_GAME_ID = 432  # Minecraft
CURSEFORGE_MODS_ENDPOINT = "/mods/search"

# Categorie Client-Only note su CurseForge:
# 414: Rendering / Shaders / Graphics
# 421: Map & Information / Minimap
# 423: Cosmetic / Customization
# 424: Sound / Audio
# 425: Utility / Inventory / UI
# 436: User Interface
CURSEFORGE_CLIENT_CATEGORIES = {414, 421, 423, 424, 425, 436}


# ============================================================================
# WHITELIST MOD NOTE CHE SONO BOTH ANCHE SE client_side=required
# ============================================================================
# Queste mod hanno client_side=required ma funzionano anche sul server
# DEVONO essere classificate come BOTH
BOTH_WHITELIST = {
    "jei",  # Just Enough Items
    "rei",  # Refined Storage Info / Refined Regolith
    "emi",  # Enchantment Mending Interface
    "jade",  # Jade - Advanced item/tool info
    "entity_model_features",  # Entity Model Features
    "entity_texture_features",  # Entity Texture Features
    "fallingleaves",  # Falling Leaves
    "helditemtooltips",  # Held Item Tooltips
    "holdmyitems",  # Hold My Items
    "mouse-tweaks",  # Mouse Tweaks
    "presencefootsteps",  # Presence Footsteps
    "soundphysicsremastered",  # Sound Physics Remastered
    "sounds",  # Sounds
    "immerse-ui",  # ImmerseUI
    "betterpingdisplay",  # Better Ping Display
    "inventorytweaks",  # Inventory Tweaks
    "mousewheelie",  # Mouse Wheelie
    "controlling",  # Controlling
    "ferritecore",  # FerriteCore (memory optimization)
    "distant-horizons",  # Distant Horizons
    "dynamicfps",  # Dynamic FPS
    "tconjei",  # Tinkers' Construct JEI
    "searchables",  # Searchables
    "stackrefill",  # Stack Refill
    "fabric-api",  # Fabric API (necessaria per tutto)
    "architectury",  # Architectury API
    "balm",  # Balm (MultiMod Framework)
    "cloth-config",  # Cloth Config
    "modmenu",  # Mod Menu
    "kotlinforforge",  # Kotlin for Forge (libreria)
    "geckolib",  # GeckoLib
    "polytone",  # Polytone
    "modmenu",  # Mod Menu
    "fabric-api",  # Fabric API
    "yet-another-config-lib-v3",  # YACL
    "puzzleslib",  # PuzzlesLib
    "let-s-do",  # Let's Do (various mods)
    "handcrafted",  # Handcrafted
    "cristellib",  # CristalLib
    "mdm",  # MDM (Multidimensional Mod)
    "resourcefullib",  # Resourceful Lib
    "moonlight",  # Moonlight Librarian
    "octolib",  # OctoLib
    "obscure-api",  # Obscure API
    "player-animation-lib-forge",  # Player Animation Lib
    "playeranimatorapi",  # Player Animator API
    "tinkersinnovation",  # Tinkers Innovation
    "mimimod",  # MiMiMod
    "tinkerbettercombat",  # Tinker Better Combat
    "tinkersjewelry",  # Tinkers Jewelry
    "tinkersdelight",  # Tinkers Delight
    "create-tinkers-compat",  # Create Tinkers Compat
    "create-ore-excavation",  # Create Ore Excavation
    "create-struct-arise",  # Create Structures Arise
    "create-questing",  # Create Questing
    "create-connected",  # Create Connected
    "create-deco",  # Create Decor
    "create-numismatics",  # Create Numismatics
    "create-addition",  # Create Addition
    "tconstruct",  # Tinkers Construct
    "mantle",  # Mantle
    "l2library",  # L2Library
    "ldlib",  # LDLib
    "decorative-blocks",  # Decorative Blocks
    "delightful",  # Delightful
    "does-it-tick",  # Does It Tick
    "dynamic-trees",  # Dynamic Trees
    "dynamic-trees-plus",  # Dynamic Trees Plus
    "immersive-weathering",  # Immersive Weathering
    "iter-rpg",  # Iter RPG
}


# ============================================================================
# FUNZIONI DI ANALISI STATICA
# ============================================================================

def classify_mod_by_name(mod_id: str) -> str:
    """Classifica una mod basandosi sul nome."""
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
    """Parsa fabric.mod.json per determinare client/server."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            with z.open('fabric.mod.json') as f:
                data = json.load(f)
            env = data.get('environment', '')
            if env == 'client':
                return 'client'
            elif env == 'server':
                return 'server'
            elif env == 'both':
                return 'both'
            entrypoints = data.get('entrypoints', {})
            if 'client' in entrypoints and 'server' not in entrypoints:
                return 'client'
            elif 'server' in entrypoints and 'client' not in entrypoints:
                return 'server'
            elif 'client' in entrypoints and 'server' in entrypoints:
                return 'both'
            return 'both'
    except Exception as e:
        print(f"    [WARN] Errore parse fabric.mod.json: {e}")
        return None


def parse_toml_mods(zip_path: Path) -> Optional[str]:
    """Parsa META-INF/mods.toml o META-INF/neoforge.mods.toml."""
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
                if mixin_sided.get('name', '').lower() == 'client':
                    return 'client'
                elif mixin_sided.get('name', '').lower() == 'server':
                    return 'server'
            display_test = mod.get('displayTest', '').lower()
            if display_test in ('client', 'server', 'both'):
                return display_test
            return 'both'
    except Exception as e:
        print(f"    [WARN] Errore parse TOML: {e}")
        return None


def analyze_mod_jar(jar_path: Path) -> dict:
    """Analizza una mod usando solo metodi statici (lettura file)."""
    result = {
        'path': str(jar_path),
        'name': jar_path.stem,
        'status': 'UNKNOWN',
        'reason': 'Nessuna info disponibile',
        'confidence': 0.0,
        'display_test': None,
        'config_file': None,
    }
    mod_id_lower = result['name'].lower()
    
    # 1. Controlla librerie dipendenza
    for lib in LIBRARY_DEPENDENCIES:
        if lib in mod_id_lower:
            result['status'] = 'BOTH'
            result['reason'] = f'LIBRERIA DIPENDENZA: {lib} (necessaria per mod che usano Kotlin)'
            result['confidence'] = 0.95
            return result
    
    # 2. Cerca file di configurazione
    config_patterns = [
        'fabric.mod.json',
        'META-INF/mods.toml',
        'META-INF/neoforge.mods.toml',
    ]
    found_config = None
    config_type = None
    for pattern in config_patterns:
        try:
            with zipfile.ZipFile(jar_path, 'r') as z:
                if pattern in z.namelist():
                    found_config = pattern
                    config_type = pattern
                    break
        except Exception:
            continue
    
    if found_config:
        if config_type == 'fabric.mod.json':
            env = parse_fabric_mod_json(jar_path)
            if env == 'client':
                result['status'] = 'CLIENT_ONLY'
                result['reason'] = 'fabric.mod.json: environment="client" o solo entrypoint client'
                result['confidence'] = 0.95
                result['config_file'] = 'fabric.mod.json'
            elif env == 'server':
                result['status'] = 'SERVER_ONLY'
                result['reason'] = 'fabric.mod.json: environment="server" o solo entrypoint server'
                result['confidence'] = 0.95
                result['config_file'] = 'fabric.mod.json'
            elif env == 'both':
                result['status'] = 'BOTH'
                result['reason'] = 'fabric.mod.json: environment="both" o entrambi gli entrypoints'
                result['confidence'] = 0.90
                result['config_file'] = 'fabric.mod.json'
            else:
                result['status'] = classify_mod_by_name(result['name'])
                result['reason'] = f'Classificazione basata su nome: {result["reason"]}'
                result['confidence'] = 0.50
        elif config_type in ('META-INF/mods.toml', 'META-INF/neoforge.mods.toml'):
            mod_id_lower = result['name'].lower()
            for keyword in CLIENT_ONLY_BLACKLIST:
                if keyword in mod_id_lower:
                    result['status'] = 'CLIENT_ONLY'
                    result['reason'] = f'Blacklist: {keyword} (mod client-only)'
                    result['confidence'] = 0.95
                    result['config_file'] = config_type
                    break
            if result['status'] == 'UNKNOWN':
                env = parse_toml_mods(jar_path)
                if env == 'client':
                    result['status'] = 'CLIENT_ONLY'
                    result['reason'] = f'TOML: displayTest="client" o serverSidedProvider="client"'
                    result['confidence'] = 0.85
                    result['config_file'] = config_type
                elif env == 'server':
                    result['status'] = 'SERVER_ONLY'
                    result['reason'] = f'TOML: displayTest="server" o serverSidedProvider="server"'
                    result['confidence'] = 0.85
                    result['config_file'] = config_type
                elif env == 'both':
                    if mod_id_lower in LIBRARY_DEPENDENCIES:
                        result['status'] = 'BOTH'
                        result['reason'] = f'LIBRERIA DIPENDENZA: {mod_id_lower} (necessaria per mod che usano Kotlin)'
                        result['confidence'] = 0.95
                        result['config_file'] = config_type
                    else:
                        result['status'] = 'BOTH'
                        result['reason'] = 'TOML: displayTest="both" o entrambi gli entrypoints'
                        result['confidence'] = 0.80
                        result['config_file'] = config_type
                        result['display_test'] = 'both'
                else:
                    result['status'] = classify_mod_by_name(result['name'])
                    result['reason'] = f'Classificazione basata su nome: {result["reason"]}'
                    result['confidence'] = 0.50
    return result


# ============================================================================
# API MODRINTH
# ============================================================================

MODRINTH_BASE_URL = "https://api.modrinth.com/v2/project"
MODRINTH_HEADERS = {
    'User-Agent': 'ForgeModSearch/3.2.0 (Riccardo.Contatto.GitHub)',
}


def search_modrinth(slug: str) -> dict:
    """Cerca una mod su Modrinth API."""
    try:
        url = f"{MODRINTH_BASE_URL}/{slug}"
        headers = dict(MODRINTH_HEADERS)
        
        req = urllib.request.Request(
            url,
            headers=headers,
            method='GET'
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"    [WARN] Mod non trovata su Modrinth")
        else:
            print(f"    [WARN] Errore HTTP Modrinth {e.code}: {e.reason}")
        return {}
    except urllib.error.URLError as e:
        print(f"    [WARN] Errore di rete Modrinth: {e.reason}")
        return {}
    except json.JSONDecodeError as e:
        print(f"    [WARN] Errore parsing JSON Modrinth: {e}")
        return {}
    except Exception as e:
        print(f"    [WARN] Errore imprevisto Modrinth: {e}")
        return {}


def search_curseforge(slug: str) -> dict:
    """
    Cerca una mod su CurseForge API come fallback.
    
    Args:
        slug: Slug pulito della mod (es. "journeymap")
    
    Returns:
        Dati della mod con campi pre-estratti o {} in caso di errore
    """
    if not CURSEFORGE_API_KEY or len(CURSEFORGE_API_KEY) == 0:
        print(f"    [WARN] CurseForge API non configurata")
        return {}
    
    try:
        # Usa gli stessi parametri di testapicurse.py
        params = urllib.parse.urlencode({
            'gameId': CURSEFORGE_GAME_ID,
            'classId': 6,
            'sortField': 2,        # Ordina per download totali
            'sortOrder': 'desc',
            'searchFilter': slug,
            'pageSize': 5
        })
        url = f"{CURSEFORGE_BASE_URL}/mods/search?{params}"
        
        headers = {
            'Accept': 'application/json',
            'x-api-key': CURSEFORGE_API_KEY,
            'User-Agent': 'ForgeModSearch/3.5.0',
        }
        
        req = urllib.request.Request(
            url,
            headers=headers,
            method='GET'
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read().decode('utf-8')
            response_data = json.loads(data)
            
            # Estrai i dati della mod come in testapicurse.py
            mods = response_data.get('data', [])
            
            if not mods:
                return {}
            
            # Cerca la mod corrispondente allo slug inserito
            matched_mod = mods[0]
            clean_input = slug.lower().replace("-", "")
            for m in mods:
                if clean_input in m.get('slug', '').replace("-", ""):
                    matched_mod = m
                    break
            
            # Estrai i campi come in testapicurse.py
            return {
                'title': matched_mod.get('name', ''),
                'slug': matched_mod.get('slug', ''),
                'version': matched_mod.get('version', ''),
                'categories': matched_mod.get('categories', []),
                'id': matched_mod.get('id', ''),
                'downloads': matched_mod.get('downloadCount', 0),
            }
    except urllib.error.HTTPError as e:
        error_msg = f"Errore HTTP CurseForge {e.code}: {e.reason}"
        if e.code == 401:
            print(f"    [WARN] Non autorizzato su CurseForge ({error_msg})")
        elif e.code == 403:
            print(f"    [WARN] Accesso negato su CurseForge - API key non valida ({error_msg})")
        elif e.code == 404:
            print(f"    [WARN] Mod non trovata su CurseForge ({error_msg})")
        else:
            print(f"    [WARN] Errore API CurseForge: {error_msg}")
        return {}
    except urllib.error.URLError as e:
        print(f"    [WARN] Errore di rete CurseForge: {e.reason}")
        return {}
    except json.JSONDecodeError as e:
        print(f"    [WARN] Errore parsing JSON CurseForge: {e}")
        return {}
    except Exception as e:
        print(f"    [WARN] Errore imprevisto CurseForge: {e}")
        return {}


def classify_modrinth(mod_data: dict) -> tuple:
    """
    Classifica una mod basandosi sui dati Modrinth.
    
    Returns:
        (status, reason, confidence, full_reason, modrinth_name, modrinth_slug, modrinth_version)
    """
    status = 'UNKNOWN'
    reason = 'Nessuna info disponibile'
    confidence = 0.0
    
    client_side = mod_data.get('client_side', '')
    server_side = mod_data.get('server_side', '')
    
    # Estrai i dati Modrinth - CORRETTO: usa 'title' invece di 'name'
    modrinth_name = mod_data.get('title', '') or mod_data.get('name', '')
    modrinth_slug = mod_data.get('slug', '')
    # CORRETTO: usa 'versions' array invece di 'latestVersion'
    versions = mod_data.get('versions', [])
    modrinth_version = versions[0] if versions else ''
    
    # CORRETTO: Controlla la whitelist di mod note che sono BOTH
    mod_lower = modrinth_name.lower()
    if mod_lower in BOTH_WHITELIST:
        status = 'BOTH'
        reason = f'WHITELIST: {modrinth_name} (mod nota che funziona sia client che server)'
        confidence = 0.98
        full_reason = f'WHITELIST: {modrinth_name} (client_side={client_side}, server_side={server_side})'
    # Logica di classificazione Modrinth
    elif client_side in ('unsupported',) and server_side in ('required', 'optional'):
        status = 'SERVER_ONLY'
        reason = 'Modrinth: server_side=required/optional, client_side=unsupported'
        confidence = 0.95
        full_reason = f'Modrinth: server_side={server_side}, client_side={client_side}'
    elif client_side in ('required', 'optional') and server_side in ('unsupported',):
        status = 'CLIENT_ONLY'
        reason = 'Modrinth: client_side=required/optional, server_side=unsupported'
        confidence = 0.95
        full_reason = f'Modrinth: client_side={client_side}, server_side={server_side}'
    elif client_side not in ('unsupported',) and server_side not in ('unsupported',):
        status = 'BOTH'
        reason = 'Modrinth: entrambi client_side e server_side sono supportati'
        confidence = 0.95
        full_reason = f'Modrinth: client_side={client_side}, server_side={server_side}'
    elif client_side in ('unsupported',) and server_side in ('unsupported',):
        status = 'UNKNOWN'
        reason = 'Modrinth: entrambi client_side e server_side sono unsupported'
        confidence = 0.0
        full_reason = f'Modrinth: client_side={client_side}, server_side={server_side}'
    else:
        status = 'BOTH'
        reason = 'Modrinth: mod non classificabile definitivamente'
        confidence = 0.50
        full_reason = f'Modrinth: client_side={client_side}, server_side={server_side}'
    
    return status, reason, confidence, full_reason, modrinth_name, modrinth_slug, modrinth_version


def classify_curseforge(mod_data: dict) -> tuple:
    """
    Classifica una mod basandosi sui dati CurseForge.
    
    Args:
        mod_data: Dati completi della mod dall'API CurseForge
    
    Returns:
        (status, reason, confidence, full_reason, title, slug, version)
    """
    status = 'UNKNOWN'
    reason = 'Nessuna info disponibile'
    confidence = 0.0
    
    # Estrai i dati correttamente
    mod_title = mod_data.get('title', '')
    mod_slug = mod_data.get('slug', '')
    mod_version = mod_data.get('version', '')
    
    categories = mod_data.get('categories', [])
    category_ids = [cat.get('id') for cat in categories]
    
    # Mappatura delle categorie CurseForge (Minecraft gameId: 432)
    # 421: API and Library
    # 414: Player Transport
    # 423: Map and Information (Minimappe)
    # 424: Cosmetic
    # 436: Food
    # 6814: Optimization/Performance
    # 425: Utility / Miscellaneous
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
    
    # Identifica se client-only tramite le categorie specifiche
    is_client = any(cid in STRICT_CLIENT_CATEGORIES for cid in category_ids)
    
    # Se la mod contiene categorie di libreria (421) o trasporto (414), non è client-only
    if 421 in category_ids or 414 in category_ids:
        is_client = False
    
    if is_client:
        status = 'CLIENT_ONLY'
        reason = f'CurseForge: mod client-only (categorie: {", ".join([CURSEFORGE_CATEGORIES.get(cid, str(cid)) for cid in category_ids])})'
        confidence = 0.95
        full_reason = f'CurseForge: mod client-only (categorie: {", ".join([CURSEFORGE_CATEGORIES.get(cid, str(cid)) for cid in category_ids])})'
    else:
        # Non è client-only, assumiamo BOTH/SERVER
        status = 'BOTH'
        reason = 'CurseForge: mod server-ready (non client-only)'
        confidence = 0.85
        full_reason = f'CurseForge: mod server-ready (categorie: {", ".join([CURSEFORGE_CATEGORIES.get(cid, str(cid)) for cid in category_ids])})'
    
    return status, reason, confidence, full_reason, mod_title, mod_slug, mod_version


def analyze_mod_with_modrinth(jar_path: Path) -> dict:
    """
    Analizza una mod usando Modrinth API.
    
    Args:
        jar_path: Percorso del file .jar
    
    Returns:
        Dizionario con i risultati dell'analisi
    """
    result = {
        'path': str(jar_path),
        'name': jar_path.stem,
        'status': 'UNKNOWN',
        'reason': 'Nessuna info disponibile',
        'confidence': 0.0,
        'source': 'static',
        'modrinth_data': None,
        'modrinth_used': False,
        'modrinth_error': None,
        'display_test': None,
        'config_file': None,
    }
    
    try:
        # Estrarre lo slug pulito dal nome
        filename = os.path.basename(jar_path)
        name = filename.replace('.jar', '')
        
        # Rimuovi suffissi come -forge, -fabric, -neoforge
        name = re.sub(r'-forge', '', name)
        name = re.sub(r'-fabric', '', name)
        name = re.sub(r'-neoforge', '', name)
        
        # Rimuovi numeri di versione come 1.20.1
        name = re.sub(r'-\d+\.\d+\.\d+', '-', name)
        
        # Rimuovi build numbers come +build.183
        name = re.sub(r'\+build\.\d+', '', name)
        name = re.sub(r'\+mc\.\d+\.\d+', '', name)
        
        # Rimuovi tutto tranne lettere, numeri, - e _
        name = re.sub(r'[^a-zA-Z0-9\-_]', '', name)
        
        # Normalizza i separatori
        name = re.sub(r'[-_]+', '-', name)
        name = name.strip('-')
        
        slug = name.lower().strip()
        
        if not slug:
            result['status'] = 'UNKNOWN'
            result['reason'] = 'Impossibile estrarre slug dalla mod'
            result['confidence'] = 0.0
            return result
        
        print(f"    [INFO] Slug Modrinth: {slug}")
        
        # Cerca su Modrinth
        print(f"    [INFO] Chiamata API Modrinth per: {slug}")
        modrinth_data = search_modrinth(slug)
        
        if not modrinth_data:
            print(f"    [WARN] Modrinth API: nessuna risposta")
            print(f"    [INFO] Fallback automatico su CurseForge API...")
            
            # Fallback su CurseForge
            curseforge_data = search_curseforge(slug)
            
            if not curseforge_data:
                print(f"    [WARN] CurseForge API: nessuna risposta")
                result['modrinth_error'] = 'Modrinth e CurseForge: nessuna risposta'
                return result
            
            print(f"    [INFO] CurseForge API: risposta ricevuta")
            result['modrinth_used'] = True
            result['curseforge_used'] = True
            
            # Estrai i dati CurseForge
            categories = curseforge_data.get('data', [])
            if categories:
                mod_data = categories[0]  # Prendi il primo risultato
                modrinth_name = mod_data.get('title', '') or mod_data.get('name', '')
                modrinth_slug = mod_data.get('slug', '')
                modrinth_version = mod_data.get('version', '')
                
                print(f"    [INFO] CurseForge Name: {modrinth_name}")
                print(f"    [INFO] CurseForge Slug: {modrinth_slug}")
                print(f"    [INFO] CurseForge Version: {modrinth_version}")
                
                # Classifica con CurseForge
                status, reason, confidence, full_reason, m_title, m_slug, m_version = classify_curseforge(curseforge_data)
                
                result['status'] = status
                result['reason'] = full_reason
                result['confidence'] = confidence
                result['source'] = 'curseforge'
                result['curseforge_data'] = mod_data
                result['curseforge_title'] = m_title
                result['curseforge_slug'] = m_slug
                result['curseforge_version'] = m_version
            else:
                result['modrinth_error'] = 'Modrinth e CurseForge: nessuna mod trovata'
                return result
        else:
            print(f"    [INFO] Modrinth API: risposta ricevuta")
            result['modrinth_used'] = True
        
        # Estrai i dati - CORRETTO: usa 'title' e 'versions'
        modrinth_name = modrinth_data.get('title', '') or modrinth_data.get('name', '')
        modrinth_slug = modrinth_data.get('slug', '')
        versions = modrinth_data.get('versions', [])
        modrinth_version = versions[0] if versions else ''
        client_side = modrinth_data.get('client_side', '')
        server_side = modrinth_data.get('server_side', '')
        
        print(f"    [INFO] Modrinth Name: {modrinth_name}")
        print(f"    [INFO] Modrinth Slug: {modrinth_slug}")
        print(f"    [INFO] Modrinth Version: {modrinth_version}")
        print(f"    [INFO] client_side: {client_side}")
        print(f"    [INFO] server_side: {server_side}")
        
        # Classifica
        status, reason, confidence, full_reason, m_name, m_slug, m_version = classify_modrinth(modrinth_data)
        
        result['status'] = status
        result['reason'] = full_reason
        result['confidence'] = confidence
        result['source'] = 'modrinth'
        result['modrinth_data'] = modrinth_data
        result['display_test'] = 'both'  # Modrinth indica BOTH
        
        # Salva nella cache
        if update_cache(slug, modrinth_data):
            print(f"    [INFO] Dato Modrinth salvato nella cache")
        
        return result
        
    except Exception as e:
        result['status'] = 'UNKNOWN'
        result['reason'] = f'Errore imprevisto: {str(e)}'
        result['confidence'] = 0.0
        result['modrinth_error'] = str(e)
        print(f"    [WARN] Errore nell'analisi con Modrinth: {e}")
        return result


def update_cache(mod_identifier: str, mod_data: dict) -> bool:
    """Salva i dati nella cache."""
    try:
        cache_path = os.path.join(os.path.dirname(__file__), 'cf_cache.json')
        cache = {}
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        cache[mod_identifier] = mod_data
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"    [WARN] Errore scrittura cache: {e}")
        return False


# ============================================================================
# ANALISI COMPLETA (STATICA + MODRINTH)
# ============================================================================

def analyze_mod(jar_path: Path) -> dict:
    """
    Analizza una mod usando prima metodi statici, poi Modrinth API.
    
    Args:
        jar_path: Percorso del file .jar
    
    Returns:
        Dizionario con i risultati dell'analisi
    """
    # 1. Analisi statica (prima)
    print(f"\n  [{jar_path.name}]")
    static_result = analyze_mod_jar(jar_path)
    
    print(f"    [{static_result['status']}] {static_result['name']}")
    print(f"    {static_result['reason']}")
    print(f"    Affidabilità: {static_result['confidence']*100:.0f}%")
    
    # 2. Se UNKNOWN o bassa affidabilità (< 0.90), usa Modrinth
    # Aumentato threshold a 0.90 per evitare falsi positivi
    if static_result['status'] == 'UNKNOWN' or static_result['confidence'] < 0.90:
        # Controllo: se è BOTH con displayTest="both", FORZA la verifica API
        if static_result['display_test'] == 'both' and static_result['confidence'] < 0.95:
            print(f"\n    [INFO] displayTest=\"both\" con fiducia bassa - uso Modrinth API")
        elif static_result['status'] == 'UNKNOWN':
            print(f"\n    [INFO] Classificazione statica UNKNOWN - uso Modrinth API")
        elif static_result['confidence'] < 0.90:
            print(f"\n    [INFO] Fiducia bassa ({static_result['confidence']*100:.0f}%) - uso Modrinth API")
        else:
            print(f"\n    [INFO] Fiducia sufficiente ({static_result['confidence']*100:.0f}%) - skip API")
        
        online_result = analyze_mod_with_modrinth(jar_path)
        
        if online_result['status'] != 'UNKNOWN':
            print(f"\n    [{online_result['status']}] {online_result['name']}")
            print(f"    {online_result['reason']}")
            print(f"    Affidabilità: {online_result['confidence']*100:.0f}%")
            print(f"    Fonte: {online_result['source'].upper()}")
            
            if online_result.get('modrinth_data'):
                m_data = online_result['modrinth_data']
                # CORRETTO: usa 'title' e 'versions' come campi corretti dell'API
                print(f"    Modrinth Title: {m_data.get('title', '') or m_data.get('name', 'N/A')}")
                print(f"    Modrinth Slug: {m_data.get('slug', 'N/A')}")
                versions = m_data.get('versions', [])
                print(f"    Modrinth Version: {versions[0] if versions else 'N/A'}")
            
            return online_result
        else:
            # Modrinth non ha trovato la mod, restituisce static
            return static_result
    
    return static_result


def analyze_mod_folder(folder_path: Path) -> list:
    """Analizza tutte le mod in una cartella."""
    results = []
    for item in folder_path.iterdir():
        if item.is_file() and item.suffix == '.jar':
            results.append(analyze_mod(item))
    return results


# ============================================================================
# PROCESSAMENTO MODPACK
# ============================================================================

def process_modpack(input_folder: Path, output_folder: Path, dry_run: bool = False, list_only: bool = False) -> dict:
    print(f"\n{'='*70}")
    print(f"  ForgeModSearch - Mod Separation Tool v3.2.0")
    print(f"{'='*70}")
    print(f"  INTEGRAZIONE MODRINTH MIGLIORATA")
    print(f"{'='*70}\n")
    
    if not input_folder.exists():
        print(f"\nErrore: La cartella '{input_folder}' non esiste.")
        sys.exit(1)
    
    if not dry_run:
        output_folder.mkdir(parents=True, exist_ok=True)
        server_mods_folder = output_folder / 'Server Mod'
        server_mods_folder.mkdir(exist_ok=True)
    
    results = []
    stats = {
        'total': 0,
        'client_only': 0,
        'server_only': 0,
        'both': 0,
        'unknown': 0,
        'modrinth_checked': 0,
        'modrinth_found': 0,
        'static_only': 0,
    }
    
    jar_count = 0
    for item in input_folder.iterdir():
        if item.is_file() and item.suffix.lower() == '.jar':
            jar_count += 1
    
    print(f"\nTrovati {jar_count} file .jar da analizzare...")
    
    # Analizza tutte le mod
    for jar_path in sorted(input_folder.iterdir()):
        if jar_path.is_file() and jar_path.suffix.lower() == '.jar':
            stats['total'] += 1
            result = analyze_mod(jar_path)
            results.append(result)
    
    # Calcola statistiche
    for result in results:
        status = result['status'].upper()
        if status == 'CLIENT_ONLY':
            stats['client_only'] += 1
        elif status == 'SERVER_ONLY':
            stats['server_only'] += 1
        elif status == 'BOTH':
            stats['both'] += 1
        else:
            stats['unknown'] += 1
        
        if result.get('modrinth_data'):
            stats['modrinth_checked'] += 1
            stats['modrinth_found'] += 1
        else:
            stats['static_only'] += 1
    
    # Copia le mod SERVER_ONLY e BOTH
    if not dry_run:
        for result in results:
            status = result['status'].upper()
            if status in ('SERVER_ONLY', 'BOTH'):
                # Usa il nome originale del file (con .jar) per mantenere l'estensione
                dest = server_mods_folder / Path(result['path']).name
                if dest.exists():
                    print(f"\n  [{dest.name}] Mod già esiste in 'Server Mod/', sovrascrivere?")
                    overwrite = input("Sovrascrivere (y/n)? ").lower() == 'y'
                else:
                    overwrite = True
                if overwrite:
                    shutil.copy2(str(result['path']), str(dest))
                    print(f"    [OK] Copiato in 'Server Mod'/")
    
    # Genera il report
    generate_report(results, stats, input_folder, output_folder, dry_run, list_only)
    
    return results


def generate_report(results: list, stats: dict, input_folder: Path, output_folder: Path, dry_run: bool, list_only: bool):
    data_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = output_folder / 'mod_analysis_report.txt'
    
    if not dry_run or list_only:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("FORGEMODSEARCH - MOD ANALYSIS REPORT v3.2.0\n")
            f.write("="*70 + "\n\n")
            f.write(f"Input folder: {input_folder}\n")
            f.write(f"Output folder: {output_folder}\n")
            f.write(f"Data: {data_str}\n")
            f.write("API: Modrinth (PRIORITARIA)\n")
            
            f.write("\n" + "-"*70 + "\n")
            f.write("STATISTICHE\n")
            f.write("-"*70 + "\n")
            f.write(f"  Mod totali:              {stats['total']}\n")
            f.write(f"  Client-Only:             {stats['client_only']}\n")
            f.write(f"  Server-Only:             {stats['server_only']}\n")
            f.write(f"  Both (Client+Server):     {stats['both']}\n")
            f.write(f"  Unknown:                 {stats['unknown']}\n")
            f.write(f"  Modrinth Checked:        {stats['modrinth_checked']}\n")
            f.write(f"  Modrinth Found:          {stats['modrinth_found']}\n")
            f.write(f"  Static Only:             {stats['static_only']}\n")
            f.write("\n" + "-"*70 + "\n")
            f.write("NOTE:\n")
            f.write("-"*70 + "\n")
            f.write("  - Mod SERVER_ONLY e BOTH sono state copiate in 'Server Mod/'\n")
            f.write("  - Mod CLIENT_ONLY rimangono nella cartella originale (da rimuovere)\n")
            f.write("  - Mod UNKNOWN rimangono nella cartella originale (da verificare)\n")
            f.write("  - LIBRERIE DIPENDENZA (BOTH) sono necessarie per il server\n")
            f.write("  - Modrinth API utilizzata per verificare mod UNKNOWN o con bassa affidabilità\n")
            f.write("  - Cache locale: cf_cache.json\n")
            f.write("\n" + "-"*70 + "\n")
            f.write("DIPENDENZE LIBRERIA:\n")
            f.write("-"*70 + "\n")
            f.write(f"  Librerie incluse: {', '.join(sorted(LIBRARY_DEPENDENCIES))}\n")
            f.write("\n" + "-"*70 + "\n")
            f.write("DETAILED LIST\n")
            f.write("-"*70 + "\n")
            
            for result in results:
                status = result['status'].upper()
                f.write(f"\n[{status}]\n")
                f.write(f"  Mod: {result['name']}\n")
                f.write(f"  Percorso: {result['path']}\n")
                f.write(f"  Motivo: {result['reason']}\n")
                f.write(f"  Affidabilità: {result['confidence']*100:.0f}%\n")
                f.write(f"  Fonte: {result.get('source', 'unknown').upper()}\n")
                
                if result.get('modrinth_data'):
                    m_data = result['modrinth_data']
                    # CORRETTO: usa 'title' e 'versions' come campi corretti dell'API
                    f.write(f"  Modrinth Title: {m_data.get('title', '') or m_data.get('name', 'N/A')}\n")
                    f.write(f"  Modrinth Slug: {m_data.get('slug', 'N/A')}\n")
                    versions = m_data.get('versions', [])
                    f.write(f"  Modrinth Version: {versions[0] if versions else 'N/A'}\n")
                elif result.get('modrinth_error'):
                    f.write(f"  Modrinth Error: {result['modrinth_error']}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("FINE REPORT\n")
            f.write("="*70 + "\n")
    
    print(f"\n{'='*70}")
    print(f"  REPORT GENERATO: {report_path}")
    print(f"{'='*70}\n")
    print()
    print("="*70)
    print("FORGEMODSEARCH - MOD ANALYSIS REPORT v3.2.0")
    print("="*70)
    print()
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Data: {data_str}")
    print("API: Modrinth (PRIORITARIA)")
    print()
    print("-"*70)
    print("STATISTICHE")
    print("-"*70)
    print(f"  Mod totali:              {stats['total']}")
    print(f"  Client-Only:             {stats['client_only']}")
    print(f"  Server-Only:             {stats['server_only']}")
    print(f"  Both (Client+Server):     {stats['both']}")
    print(f"  Unknown:                 {stats['unknown']}")
    print(f"  Modrinth Checked:        {stats['modrinth_checked']}")
    print(f"  Modrinth Found:          {stats['modrinth_found']}")
    print(f"  Static Only:             {stats['static_only']}")
    print()
    print("-"*70)
    print("NOTE:")
    print("-"*70)
    print("  - Mod SERVER_ONLY e BOTH sono state copiate in 'Server Mod/'")
    print("  - Mod CLIENT_ONLY rimangono nella cartella originale (da rimuovere)")
    print("  - Mod UNKNOWN rimangono nella cartella originale (da verificare)")
    print("  - LIBRERIE DIPENDENZA (BOTH) sono necessarie per il server")
    print("  - Modrinth API utilizzata per verificare mod UNKNOWN o con bassa affidabilità")
    print("  - Cache locale: cf_cache.json")
    print()
    print("-"*70)
    print("DIPENDENZE LIBRERIA")
    print("-"*70)
    print(f"  Librerie incluse: {', '.join(sorted(LIBRARY_DEPENDENCIES))}")
    print()
    print("-"*70)
    print("DETAILED LIST")
    print("-"*70)
    print()
    for result in results:
        status = result['status'].upper()
        print(f"[{status}] {result['name']}")
        print(f"  Percorso: {result['path']}")
        print(f"  Motivo: {result['reason']}")
        print(f"  Affidabilità: {result['confidence']*100:.0f}%")
        print(f"  Fonte: {result.get('source', 'unknown').upper()}")
        if result.get('modrinth_data'):
            m_data = result['modrinth_data']
            # CORRETTO: usa 'title' e 'versions' come campi corretti dell'API
            print(f"  Modrinth Title: {m_data.get('title', '') or m_data.get('name', 'N/A')}")
            print(f"  Modrinth Slug: {m_data.get('slug', 'N/A')}")
            versions = m_data.get('versions', [])
            print(f"  Modrinth Version: {versions[0] if versions else 'N/A'}")
        elif result.get('modrinth_error'):
            print(f"  Modrinth Error: {result['modrinth_error']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Identifica e separa mod Client-Only dalle mod Server-Ready per Minecraft modpacks.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'input_folder',
        type=Path,
        nargs='?',
        default=Path('./mods'),
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('./mods'),
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
    )
    parser.add_argument(
        '--list-only',
        action='store_true',
    )
    args = parser.parse_args()
    
    if args.output != Path('./mods'):
        args.input_folder = args.output
        args.output = Path('./mods')
    
    if not args.quiet:
        print(f"Input folder: {args.input_folder}")
        print(f"Output folder: {args.output}")
        print(f"Modalità: {'DRY-RUN' if args.dry_run else 'AUTO'}")
    
    results = process_modpack(
        input_folder=args.input_folder,
        output_folder=args.output,
        dry_run=args.dry_run,
        list_only=args.list_only
    )
    
    if args.list_only:
        print("\n" + "="*70)
        print("MOD CLASSIFICATE PER TIPO:")
        print("="*70)
        print("\n[CLIENT_ONLY] - Da rimuovere:")
        for result in results:
            if result['status'] == 'CLIENT_ONLY':
                print(f"  - {result['name']}")
                print(f"    {result['reason']}")
        print("\n[SERVER_ONLY] - Pronte per il server:")
        for result in results:
            if result['status'] == 'SERVER_ONLY':
                print(f"  - {result['name']}")
                print(f"    {result['reason']}")
        print("\n[BOTH] - Client e Server:")
        for result in results:
            if result['status'] == 'BOTH':
                print(f"  - {result['name']}")
                print(f"    {result['reason']}")
        print("\n[UNKNOWN] - Da verificare:")
        for result in results:
            if result['status'] == 'UNKNOWN':
                print(f"  - {result['name']}")
                print(f"    {result['reason']}")
        print()


if __name__ == '__main__':
    main()