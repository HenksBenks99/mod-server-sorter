#!/usr/bin/env python3
"""
Test specifico per Journeymap - dovrebbe essere CLIENT_ONLY
"""

import sys
import os

sys.path.insert(0, '.')

from forge_mod_separation import search_modrinth, search_curseforge, classify_modrinth, classify_curseforge

print("=" * 70)
print("TEST JOURNEYMAP - DOVREBBE ESSERE CLIENT_ONLY")
print("=" * 70)

# Test Modrinth
print("\n[1] TENTATIVO MODRINTH")
print("-" * 70)
modrinth_data = search_modrinth("journeymap")

if modrinth_data:
    print(f"  [OK] Modrinth: {modrinth_data.get('title', 'N/A')}")
    print(f"  client_side: {modrinth_data.get('client_side', 'N/A')}")
    print(f"  server_side: {modrinth_data.get('server_side', 'N/A')}")
    
    status, reason, confidence, full_reason, name, slug, version = classify_modrinth(modrinth_data)
    print(f"  [STATUS] {status}")
    print(f"  [REASON] {reason}")
    print(f"  [CONFIDENCE] {confidence*100:.0f}%")
else:
    print(f"  [WARN] Modrinth: nessuna risposta")
    print(f"  [INFO] Fallback su CurseForge API...")
    
    # Fallback su CurseForge
    curseforge_data = search_curseforge("journeymap")
    
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
print("TEST COMPLETATO")
print("=" * 70)