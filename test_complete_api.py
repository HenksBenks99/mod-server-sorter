#!/usr/bin/env python3
"""
Test completo delle API Modrinth e CurseForge con forge_mod_separation.py
"""

import sys
import os

sys.path.insert(0, '.')

from forge_mod_separation import search_modrinth, search_curseforge, classify_modrinth, classify_curseforge

# Test Modrinth
print("=" * 70)
print("TEST API MODRINTH")
print("=" * 70)

test_slugs_modrinth = ["journeymap", "sodium", "jei", "create"]

for slug in test_slugs_modrinth:
    print(f"\n[TEST] {slug.upper()}")
    modrinth_data = search_modrinth(slug)
    
    if modrinth_data:
        print(f"  [OK] Trovata: {modrinth_data.get('title', 'N/A')}")
        print(f"  client_side: {modrinth_data.get('client_side', 'N/A')}")
        print(f"  server_side: {modrinth_data.get('server_side', 'N/A')}")
        
        # Classifica
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
            
            # Classifica
            status, reason, confidence, full_reason, title, slug, version = classify_curseforge(curseforge_data)
            print(f"  [STATUS] {status}")
            print(f"  [REASON] {reason}")
            print(f"  [CONFIDENCE] {confidence*100:.0f}%")
        else:
            print(f"  [WARN] CurseForge: nessuna risposta")

print("\n" + "=" * 70)
print("TEST COMPLETATO")
print("=" * 70)