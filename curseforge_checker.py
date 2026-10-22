#!/usr/bin/env python3
"""
CurseForge Checker - Ora solo Modrinth API + gestione cache
NOTA: CurseForge rimosso. Solo Modrinth API.
"""

import os
import json
import re
import urllib.parse
import urllib.request
from typing import Optional, Tuple

# ============================================================================
# CONFIGURAZIONE API MODRINTH
# ============================================================================

MODRINTH_BASE_URL = "https://api.modrinth.com/v2/project"
MODRINTH_HEADERS = {
    'User-Agent': 'ForgeModSearch/3.0.0 (Riccardo.Contatto.GitHub)',
}


# ============================================================================
# GESTIONE CACHE
# ============================================================================

CACHE_FILE = "cf_cache.json"


def get_cache_path() -> str:
    """Restituisce il percorso assoluto del file di cache."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_FILE)


def load_cache() -> dict:
    """Carica i dati dalla cache JSON. Restituisce un dizionario vuoto se il file non esiste."""
    cache_path = get_cache_path()
    if not os.path.exists(cache_path):
        return {}
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"    [WARN] Errore lettura cache: {e}")
        return {}


def save_cache(cache_data: dict) -> bool:
    """Salva i dati nella cache JSON. Restituisce True se riuscito, False altrimenti."""
    cache_path = get_cache_path()
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"    [WARN] Errore scrittura cache: {e}")
        return False


def get_cached_mod(mod_identifier: str) -> Optional[dict]:
    """
    Cerca una mod nella cache usando il suo slug pulito.
    
    Args:
        mod_identifier: Slug pulito della mod (es. "sodium", "embeddium")
    
    Returns:
        Il dato memorizzato nella cache o None se non presente
    """
    cache = load_cache()
    return cache.get(mod_identifier)


def update_cache(mod_identifier: str, mod_data: dict) -> bool:
    """
    Aggiorna o aggiunge una mod alla cache.
    
    Args:
        mod_identifier: Slug pulito della mod
        mod_data: Dati completi restituiti dall'API
    
    Returns:
        True se salvato con successo, False altrimenti
    """
    cache = load_cache()
    cache[mod_identifier] = mod_data
    return save_cache(cache)


def clear_cache() -> bool:
    """
    Svuota completamente la cache.
    
    Returns:
        True se riuscito, False altrimenti
    """
    cache_path = get_cache_path()
    try:
        if os.path.exists(cache_path):
            os.remove(cache_path)
        return True
    except IOError as e:
        print(f"    [WARN] Errore cancellazione cache: {e}")
        return False


def print_cache_stats() -> None:
    """Stampa statistiche sulla cache."""
    cache = load_cache()
    print(f"\nCache Modrinth ({len(cache)} entry):")
    for slug, data in cache.items():
        print(f"  - {slug}: {data.get('name', 'N/A')}")


# ============================================================================
# FUNZIONI DI PULIZIA NOME MOD
# ============================================================================

def clean_mod_name(mod_name: str) -> str:
    """
    Estrae uno slug pulito dal nome del file .jar.
    
    Rimuove:
    - Numeri di versione (es. 1.20.1, 1.19.4, 1.21.1)
    - Suffissi come -v1.0, -v2, -alpha, -beta, -rc1
    - Estensione .jar
    - Caratteri speciali non alfanumerici (tranne - e _)
    
    Args:
        mod_name: Nome completo del file .jar (es. "sodium-1.20.1-0.5.0+build.183.jar")
    
    Returns:
        Slug pulito (es. "sodium")
    """
    # Rimuovi estensione .jar
    name = mod_name.replace('.jar', '')
    
    # Rimuovi suffissi come -forge, -fabric, -neoforge
    name = re.sub(r'-forge', '', name)
    name = re.sub(r'-fabric', '', name)
    name = re.sub(r'-neoforge', '', name)
    
    # Rimuovi pattern di versione come 1.20.1, 1.19.4, 1.21.1
    name = re.sub(r'-\d+\.\d+\.\d+', '-', name)
    
    # Rimuovi suffissi come -v1.0, -v2, -alpha, -beta, -rc1, -preview
    name = re.sub(r'-v\d+', '-', name)
    name = re.sub(r'-alpha', '-', name)
    name = re.sub(r'-beta', '-', name)
    name = re.sub(r'-rc\d+', '-', name)
    name = re.sub(r'-preview', '-', name)
    name = re.sub(r'-snapshot', '-', name)
    
    # Rimuovi build numbers come +build.183, +mc.1.20.1
    name = re.sub(r'\+build\.\d+', '', name)
    name = re.sub(r'\+mc\.\d+\.\d+', '', name)
    name = re.sub(r'\+\d+\.\d+', '', name)
    
    # Rimuovi tutto tranne lettere, numeri, - e _
    name = re.sub(r'[^a-zA-Z0-9\-_]', '', name)
    
    # Normalizza i separatori (sostituisci multipli - o _ con un singolo)
    name = re.sub(r'[-_]+', '-', name)
    
    # Rimuovi trattini iniziali e finali
    name = name.strip('-')
    
    # Rimuovi numeri iniziali (es. "123-modname" -> "modname")
    name = re.sub(r'^\d+-?', '', name)
    
    return name.lower().strip()


def extract_mod_slug_from_path(jar_path: str) -> str:
    """
    Estrarre lo slug pulito direttamente dal percorso del file.
    
    Args:
        jar_path: Percorso completo del file .jar
    
    Returns:
        Slug pulito della mod
    """
    # Estrai il nome del file
    filename = os.path.basename(jar_path)
    
    # Rimuovi estensione .jar
    name = filename.replace('.jar', '')
    
    # Rimuovi suffissi come -forge, -fabric, -neoforge
    name = re.sub(r'-forge', '', name)
    name = re.sub(r'-fabric', '', name)
    name = re.sub(r'-neoforge', '', name)
    
    # Trova l'ultimo trattino o underscore dopo il nome della mod
    # Es: "sodium-1.20.1-0.5.0+build.183.jar" -> "sodium"
    parts = name.split('-')
    if parts:
        # Il primo elemento è solitamente il nome della mod
        return clean_mod_name(parts[0])
    
    return clean_mod_name(name)


# ============================================================================
# API MODRINTH
# ============================================================================

def search_modrinth(slug: str) -> dict:
    """
    Cerca una mod su Modrinth API.
    
    Args:
        slug: Slug pulito della mod (es. "journeymap")
    
    Returns:
        Dati della mod o {} in caso di errore
    """
    try:
        url = f"{MODRINTH_BASE_URL}/{slug}"
        headers = dict(MODRINTH_HEADERS)
        
        req = urllib.request.Request(
            url,
            headers=headers,
            method='GET'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
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


def classify_modrinth(mod_data: dict) -> Tuple[str, str, float, str]:
    """
    Classifica una mod basandosi sui dati Modrinth.
    
    Args:
        mod_data: Dati completi della mod dall'API Modrinth
    
    Returns:
        Tuple (status, reason, confidence, full_reason)
    """
    status = 'UNKNOWN'
    reason = 'Nessuna info disponibile'
    confidence = 0.0
    
    client_side = mod_data.get('client_side', '')
    server_side = mod_data.get('server_side', '')
    
    # Logica di classificazione Modrinth
    if client_side in ('unsupported',) and server_side in ('required', 'optional'):
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
    
    return status, reason, confidence, full_reason


# ============================================================================
# ANALISI MODRINTH COMPLETA
# ============================================================================

def analyze_mod_with_modrinth(jar_path: str) -> dict:
    """
    Analizza una mod usando Modrinth API.
    
    Args:
        jar_path: Percorso del file .jar
    
    Returns:
        Dizionario con i risultati dell'analisi
    """
    result = {
        'path': jar_path,
        'name': jar_path,
        'status': 'UNKNOWN',
        'reason': 'Nessuna info disponibile',
        'confidence': 0.0,
        'source': 'static',
        'modrinth_data': None,
        'modrinth_used': False,
        'modrinth_error': None,
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
            result['modrinth_error'] = 'Modrinth API: nessuna risposta'
            return result
        
        print(f"    [INFO] Modrinth API: risposta ricevuta")
        result['modrinth_used'] = True
        
        # Estrai i dati
        modrinth_name = modrinth_data.get('name', '')
        modrinth_slug = modrinth_data.get('slug', '')
        modrinth_version = modrinth_data.get('latestVersion', '')
        client_side = modrinth_data.get('client_side', '')
        server_side = modrinth_data.get('server_side', '')
        
        print(f"    [INFO] Modrinth Name: {modrinth_name}")
        print(f"    [INFO] Modrinth Slug: {modrinth_slug}")
        print(f"    [INFO] Modrinth Version: {modrinth_version}")
        print(f"    [INFO] client_side: {client_side}")
        print(f"    [INFO] server_side: {server_side}")
        
        # Classifica
        status, reason, confidence, full_reason = classify_modrinth(modrinth_data)
        
        result['status'] = status
        result['reason'] = full_reason
        result['confidence'] = confidence
        result['source'] = 'modrinth'
        result['modrinth_data'] = modrinth_data
        
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


# ============================================================================
# REPORTING
# ============================================================================

def clear_cache_and_restart() -> None:
    """Svuota la cache e ristarta."""
    if clear_cache():
        print("Cache svuotata con successo")
    else:
        print("Errore nel vuoto della cache")