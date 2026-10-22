#!/usr/bin/env python3
"""
Test CurseForge per Journeymap
"""

import sys
import os

sys.path.insert(0, '.')

from forge_mod_separation import search_curseforge, classify_curseforge

print("=" * 70)
print("TEST CURSEFORGE JOURNEYMAP")
print("=" * 70)

curseforge_data = search_curseforge("journeymap")

if curseforge_data:
    print(f"  [OK] CurseForge: risposta ricevuta")
    print(f"  Title: {curseforge_data.get('title', 'N/A')}")
    print(f"  Slug: {curseforge_data.get('slug', 'N/A')}")
    print(f"  Categories: {len(curseforge_data.get('categories', []))}")
    print(f"  Categories IDs: {[c.get('id') for c in curseforge_data.get('categories', [])]}")
    
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