#!/usr/bin/env python3
"""
Test del fallback CurseForge con mod non presenti su Modrinth
"""

import sys
import os

sys.path.insert(0, '.')

from forge_mod_separation import search_modrinth, search_curseforge, classify_modrinth, classify_curseforge

# Mod che NON sono su Modrinth (per testare il fallback)
test_slugs_no_modrinth = ["additional_lights", "architectury", "create", "cloth-config", "fabric-api"]

print("=" * 70)
print("TEST FALLBACK CURSEFORGE (Mod NON su Modrinth)")
print("=" * 70)

for slug in test_slugs_no_modrinth:
    print(f"\n[TEST] {slug.upper()}")
    
    # Primo tentativo Modrinth
    print(f"  [INFO] Tentativo Modrinth API...")
    modrinth_data = search_modrinth(slug)
    
    if modrinth_data:
        print(f"  [OK] Modrinth: {modrinth_data.get('title', 'N/A')}")
        status, reason, confidence, full_reason, name, slug, version = classify_modrinth(modrinth_data)
        print(f"  [STATUS] {status}")
        print(f"  [REASON] {reason}")
        print(f"  [CONFIDENCE] {confidence*100:.0f}%")
    else:
        print(f"  [WARN] Modrinth: nessuna risposta")
        print(f"  [INFO] Fallback su CurseForge API...")
        
        # Fallback su CurseForge
        curseforge_data = search_curseforge(slug)
        
        if curseforge_data:
            print(f"  [OK] CurseForge: risposta ricevuta")
            print(f"  Title: {curseforge_data.get('title', 'N/A')}")
            print(f"  Slug: {curseforge_data.get('slug', 'N/A')}")
            print(f"  Categories: {len(curseforge_data.get('categories', []))}")
            
            # Classifica
            status, reason, confidence, full_reason, title, slug, version = classify_curseforge(curseforge_data)
            print(f"  [STATUS] {status}")
            print(f"  [REASON] {reason}")
            print(f"  [CONFIDENCE] {confidence*100:.0f}%")
        else:
            print(f"  [WARN] CurseForge: nessuna risposta")

print("\n" + "=" * 70)
print("TEST FALLBACK COMPLETATO")
print("=" * 70)