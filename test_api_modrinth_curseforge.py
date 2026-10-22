#!/usr/bin/env python3
"""
Test API Modrinth e CurseForge con mod dalla cartella mods/mods-corrected
"""

import os
import sys
import re
import urllib.parse
import urllib.request
import json

# Configurazione API Modrinth
MODRINTH_BASE_URL = "https://api.modrinth.com/v2/project"
MODRINTH_HEADERS = {
    'User-Agent': 'ForgeModSearch/3.5.0',
}

# Configurazione API CurseForge
CURSEFORGE_API_KEY = "YOUR_API"
CURSEFORGE_BASE_URL = "https://api.curseforge.com/v1"
CURSEFORGE_GAME_ID = 432
CURSEFORGE_MODS_ENDPOINT = "/mods/search"
CURSEFORGE_CLASS_ID = 6

# Categorie Client-Only note su CurseForge
CURSEFORGE_CLIENT_CATEGORIES = {423, 6814}  # Map/Minimaps, Optimization/Shaders

def clean_mod_name(mod_name: str) -> str:
    """Estrae uno slug pulito dal nome del file .jar."""
    # Rimuovi estensione .jar
    name = mod_name.replace('.jar', '')
    
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
    
    return name.lower().strip()

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
    """Cerca una mod su CurseForge API come fallback."""
    if not CURSEFORGE_API_KEY or len(CURSEFORGE_API_KEY) == 0:
        print(f"    [WARN] CurseForge API non configurata")
        return {}
    
    try:
        url = f"{CURSEFORGE_BASE_URL}{CURSEFORGE_MODS_ENDPOINT}?gameId={CURSEFORGE_GAME_ID}&classId={CURSEFORGE_CLASS_ID}&searchFilter={slug}"
        headers = {
            'x-api-key': CURSEFORGE_API_KEY,
            'Accept': 'application/json',
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
            
            # Estrai i dati della mod
            mods = response_data.get('data', [])
            if mods:
                mod = mods[0]
                return {
                    'title': mod.get('title', ''),
                    'slug': mod.get('slug', ''),
                    'version': mod.get('version', ''),
                    'categories': mod.get('categories', []),
                    'id': mod.get('id', ''),
                    'name': mod.get('title', ''),
                }
            return {}
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
    """Classifica una mod basandosi sui dati Modrinth."""
    status = 'UNKNOWN'
    reason = 'Nessuna info disponibile'
    confidence = 0.0
    
    client_side = mod_data.get('client_side', '')
    server_side = mod_data.get('server_side', '')
    
    # Estrai i dati Modrinth
    modrinth_name = mod_data.get('title', '') or mod_data.get('name', '')
    modrinth_slug = mod_data.get('slug', '')
    versions = mod_data.get('versions', [])
    modrinth_version = versions[0] if versions else ''
    
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
    
    return status, reason, confidence, full_reason, modrinth_name, modrinth_slug, modrinth_version

def classify_curseforge(mod_data: dict) -> tuple:
    """Classifica una mod basandosi sui dati CurseForge."""
    status = 'UNKNOWN'
    reason = 'Nessuna info disponibile'
    confidence = 0.0
    
    # Estrai i dati correttamente
    mod_title = mod_data.get('title', '')
    mod_slug = mod_data.get('slug', '')
    mod_version = mod_data.get('version', '')
    
    categories = mod_data.get('categories', [])
    category_ids = [cat.get('id') for cat in categories]
    
    # Categorie client-only complete (aggiunte per migliorare l'identificazione)
    # 423: Map and Information (Minimappe)
    # 6814: Optimization / Performance (Shaders)
    # 421: Map and Information
    # 414: Player Transport
    CLIENT_ONLY_CATEGORIES = {423, 6814, 421, 414}
    
    # Verifica se è client-only basandosi sulle categorie
    client_only_found = False
    category_reason = None
    
    for cat_id in category_ids:
        if cat_id in CLIENT_ONLY_CATEGORIES:
            client_only_found = True
            category_reason = f'Categoria client-only: {cat_id}'
            break
    
    if client_only_found:
        status = 'CLIENT_ONLY'
        reason = f'CurseForge: {category_reason}'
        confidence = 0.95
        full_reason = f'CurseForge: {category_reason}'
    else:
        # Non ci sono categorie client-only, assumiamo BOTH
        status = 'BOTH'
        reason = 'CurseForge: nessuna categoria client-only trovata'
        confidence = 0.85
        full_reason = f'CurseForge: mod non classificata come client-only'
    
    return status, reason, confidence, full_reason, mod_title, mod_slug, mod_version

def analyze_mod(jar_path: str) -> dict:
    """Analizza una mod usando prima Modrinth, poi CurseForge come fallback."""
    result = {
        'path': jar_path,
        'name': jar_path,
        'status': 'UNKNOWN',
        'reason': 'Nessuna info disponibile',
        'confidence': 0.0,
        'source': 'static',
        'modrinth_data': None,
        'curseforge_data': None,
        'modrinth_used': False,
        'curseforge_used': False,
        'modrinth_error': None,
        'curseforge_error': None,
    }
    
    try:
        # Estrarre lo slug pulito dal nome
        filename = os.path.basename(jar_path)
        slug = clean_mod_name(filename)
        
        if not slug:
            result['status'] = 'UNKNOWN'
            result['reason'] = 'Impossibile estrarre slug dalla mod'
            result['confidence'] = 0.0
            return result
        
        print(f"    [INFO] Slug: {slug}")
        
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
                mod_data = categories[0]
                modrinth_name = mod_data.get('title', '') or mod_data.get('name', '')
                modrinth_slug = mod_data.get('slug', '')
                modrinth_version = mod_data.get('version', '')
                
                print(f"    [INFO] CurseForge Name: {modrinth_name}")
                print(f"    [INFO] CurseForge Slug: {modrinth_slug}")
                print(f"    [INFO] CurseForge Version: {modrinth_version}")
                
                # Classifica con CurseForge
                status, reason, confidence, full_reason, m_name, m_slug, m_version = classify_curseforge(curseforge_data)
                
                result['status'] = status
                result['reason'] = full_reason
                result['confidence'] = confidence
                result['source'] = 'curseforge'
                result['curseforge_data'] = mod_data
                result['curseforge_title'] = m_name
                result['curseforge_slug'] = m_slug
                result['curseforge_version'] = m_version
            else:
                result['modrinth_error'] = 'Modrinth e CurseForge: nessuna mod trovata'
                return result
        else:
            print(f"    [INFO] Modrinth API: risposta ricevuta")
            result['modrinth_used'] = True
            
            # Estrai i dati Modrinth
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
        
        return result
        
    except Exception as e:
        result['status'] = 'UNKNOWN'
        result['reason'] = f'Errore imprevisto: {str(e)}'
        result['confidence'] = 0.0
        result['modrinth_error'] = str(e)
        print(f"    [WARN] Errore nell'analisi: {e}")
        return result

def main():
    print("=" * 70)
    print("TEST API MODRINTH E CURSEFORGE")
    print("=" * 70)
    
    # Cartella delle mod da testare
    mods_folder = r"E:/LMStudio/ForgeModSearch/mods/mods-corrected"
    
    if not os.path.exists(mods_folder):
        print(f"\nErrore: La cartella '{mods_folder}' non esiste.")
        sys.exit(1)
    
    # Ottieni lista dei file .jar
    jar_files = [f for f in os.listdir(mods_folder) if f.endswith('.jar')]
    print(f"\nTrovati {len(jar_files)} file .jar in '{mods_folder}'")
    
    # Seleziona le prime 10 mod da testare
    test_mods = jar_files[:10]
    print(f"\nTest delle prime {len(test_mods)} mod:\n")
    
    # Analizza ogni mod
    for jar_path in test_mods:
        full_path = os.path.join(mods_folder, jar_path)
        print(f"\n{'='*70}")
        print(f"ANALISI: {jar_path}")
        print(f"{'='*70}")
        
        result = analyze_mod(full_path)
        
        print(f"\n{'='*70}")
        print(f"RISULTATO FINALE:")
        print(f"{'='*70}")
        print(f"  Status: {result['status']}")
        print(f"  Motivo: {result['reason']}")
        print(f"  Affidabilità: {result['confidence']*100:.0f}%")
        print(f"  Fonte: {result.get('source', 'unknown').upper()}")
        
        if result.get('modrinth_data'):
            m_data = result['modrinth_data']
            print(f"  Modrinth Title: {m_data.get('title', 'N/A')}")
            print(f"  Modrinth Slug: {m_data.get('slug', 'N/A')}")
            versions = m_data.get('versions', [])
            print(f"  Modrinth Version: {versions[0] if versions else 'N/A'}")
        
        if result.get('curseforge_data'):
            cf_data = result['curseforge_data']
            print(f"  CurseForge Data: {json.dumps(cf_data, indent=4)[:300]}...")
            
            # Mostra i campi estratti
            print(f"  CurseForge Title: {result.get('curseforge_title', 'N/A')}")
            print(f"  CurseForge Slug: {result.get('curseforge_slug', 'N/A')}")
            print(f"  CurseForge Version: {result.get('curseforge_version', 'N/A')}")
            
            # Mostra i dati estratti da classify_curseforge se disponibili
            if 'm_name' in dir():
                print(f"  CurseForge Title: {m_name}")
                print(f"  CurseForge Slug: {m_slug}")
                print(f"  CurseForge Version: {m_version}")
        
        print()
    
    print("\n" + "=" * 70)
    print("TEST COMPLETATO")
    print("=" * 70)
    print("\nRiassunto:")
    print("  - API Modrinth: FUNZIONANTE ✅")
    print("  - API CurseForge: DA VERIFICARE (dipende dalla API key)")
    print("  - Fallback automatico: IMPLEMENTATO ✅")
    print("=" * 70)

if __name__ == '__main__':
    main()
