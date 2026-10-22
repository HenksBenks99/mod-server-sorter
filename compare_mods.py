#!/usr/bin/env python3
"""
Report di confronto tra mod funzionanti e mod che causano crash
Genera un report dettagliato delle differenze tra le due cartelle
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Percorsi delle cartelle
MODS_FOLDER = r"E:\LMStudio\ForgeModSearch\mods\mods"
MODS_TEST_FOLDER = r"E:\LMStudio\ForgeModSearch\mods\mods-test"
REPORT_FILE = r"E:\LMStudio\ForgeModSearch\mods\comparison_report.txt"

def get_mod_list(folder):
    """Estrai lista mod da una cartella."""
    mods = set()
    if not Path(folder).exists():
        return mods
    for item in Path(folder).iterdir():
        if item.is_file() and item.suffix.lower() == '.jar':
            mods.add(item.stem.lower())
    return mods

def analyze_mod(name):
    """Analizza una mod e ritorna se é client-only."""
    name_lower = name.lower()
    
    # Blacklist aggiornata con le nuove mod scoperte
    client_only_keywords = {
        "sodium", "rubidium", "iris", "embeddium", "embed", "ophiurei",
        "oculus", "turbo", "turbo-api", "optifine",
        "journeymap", "xaerominimap", "xaeroworldmap",
        "appleskin", "inventorytweaks", "mousewheelie", "controlling",
        "ferritecore", "jei", "rei", "emi", "waystones",
        # NUOVE MOD IDENTIFICATE COME CLIENT-ONLY
        "animatica", "cameraoverhaul", "distant-horizons", "dynamic-fps",
        "enhanced-boss-bars", "entity-model-features", "entity-texture-features",
        "fallingleaves", "flerovium", "held-item-tooltips", "holdmyitems",
        "modelfix", "mouse-tweaks", "polytone", "presence-footsteps",
        "sodium-dynamic-lights", "sodium-options-api", "sound-physics-remastered",
        "sounds", "immerse-ui", "jade", "amendments", "better-advancements",
        "better-ping-display",
    }
    
    # Eccezioni: mod che contengono parole blacklist ma sono BOTH
    both_keywords = {"balm", "architectury", "cloth-config", "modmenu"}
    
    # Check blacklist
    for keyword in client_only_keywords:
        if keyword in name_lower:
            # Verifica whitelist
            for exception in both_keywords:
                if exception in name_lower:
                    return "BOTH"
            return "CLIENT_ONLY"
    
    return "UNKNOWN"

def main():
    print("="*70)
    print("REPORT DI CONFRONTO: MODS vs MODS-TEST")
    print("="*70)
    print()
    
    # Estrai liste mod
    mods_list = get_mod_list(MODS_FOLDER)
    mods_test_list = get_mod_list(MODS_TEST_FOLDER)
    
    # Mod in eccesso
    diff = mods_test_list - mods_list
    
    print(f"Mod totali in 'mods' (funziona): {len(mods_list)}")
    print(f"Mod totali in 'mods-test' (crash): {len(mods_test_list)}")
    print(f"Mod in eccesso in 'mods-test': {len(diff)}")
    print()
    
    # Classifica mod in eccesso
    print("-"*70)
    print("MOD CLIENT-ONLY IN 'mods-test' (DA RIMUOVERE):")
    print("-"*70)
    
    client_only_mods = []
    both_mods = []
    unknown_mods = []
    
    for mod in sorted(diff):
        classification = analyze_mod(mod)
        if classification == "CLIENT_ONLY":
            client_only_mods.append(mod)
        elif classification == "BOTH":
            both_mods.append(mod)
        else:
            unknown_mods.append(mod)
    
    print(f"\n[CLIENT_ONLY] - {len(client_only_mods)} mod:")
    for mod in client_only_mods:
        print(f"  [CLIENT_ONLY] {mod}")
    
    print(f"\n[BOTH] - {len(both_mods)} mod:")
    for mod in both_mods:
        print(f"  [BOTH] {mod}")
    
    print(f"\n[UNKNOWN] - {len(unknown_mods)} mod:")
    for mod in unknown_mods:
        print(f"  [UNKNOWN] {mod}")
    
    # Genera report in file
    report_path = Path(REPORT_FILE)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("REPORT DI CONFRONTO: MODS vs MODS-TEST\n")
        f.write("="*70 + "\n\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Mod totali in 'mods' (funziona): {len(mods_list)}\n")
        f.write(f"Mod totali in 'mods-test' (crash): {len(mods_test_list)}\n")
        f.write(f"Mod in eccesso in 'mods-test': {len(diff)}\n\n")
        f.write("-"*70 + "\n")
        f.write("MOD CLIENT-ONLY IN 'mods-test' (DA RIMUOVERE):\n")
        f.write("-"*70 + "\n\n")
        f.write(f"[CLIENT_ONLY] - {len(client_only_mods)} mod:\n")
        for mod in client_only_mods:
            f.write(f"  [CLIENT_ONLY] {mod}\n")
        f.write(f"\n[BOTH] - {len(both_mods)} mod:\n")
        for mod in both_mods:
            f.write(f"  [BOTH] {mod}\n")
        f.write(f"\n[UNKNOWN] - {len(unknown_mods)} mod:\n")
        for mod in unknown_mods:
            f.write(f"  [UNKNOWN] {mod}\n")
        f.write("\n" + "="*70 + "\n")
        f.write("CONCLUSIONI:\n")
        f.write("="*70 + "\n")
        f.write("1. Rimuovi le mod [CLIENT_ONLY] dalla cartella 'mods-test'\n")
        f.write("2. Le mod [BOTH] sono sicure per il server\n")
        f.write("3. Verifica le mod [UNKNOWN] manualmente\n")
        f.write("\n4. Usa lo script forge_mod_separation.py per analisi automatica\n")
    
    print(f"\nReport salvato in: {REPORT_FILE}")
    print()
    print("="*70)
    print("CONCLUSIONI:")
    print("="*70)
    print("1. Rimuovi le mod [CLIENT_ONLY] dalla cartella 'mods-test'")
    print("2. Le mod [BOTH] sono sicure per il server")
    print("3. Verifica le mod [UNKNOWN] manualmente")
    print("\n4. Usa lo script forge_mod_separation.py per analisi automatica")

if __name__ == '__main__':
    main()