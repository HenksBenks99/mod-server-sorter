#!/usr/bin/env python3
"""
ForgeModSearch - Mod Separation Tool v4.1.0 - CORREZIONE CLASSIFICAZIONE
Usa metadati interni dei jar e una mappa di override per classificare correttamente le mod.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from mod_parser import ModMetadataParser

# Configurazione cartelle
MODS_SOURCE = Path('./mods/mods-corrected')
SERVER_MODS_DIR = Path('./mods/Server_Ready')

# --- Mappa di override per classificazioni errate ---
# Queste mod vengono classificata erroneamente come 'client' o 'unknown'
# ma sono NECESSARIE al server per fornire API o dipendenze critiche.
SERVER_SIDE_FORCE_INCLUDE = {
    "jei",                # Fornisce integrazione per item nel server
    "ferritecore",        # Ottimizzazione memoria fondamentale, usata da molte mod
    "tconjei",            # Integrazione JEI per Tinkers' Construct (server necessità del .jar)
    "appleskin",
    "refined-storage-jei", # Integrazione JEI
    "searchables",        # Fornisce funzionalità di ricerca anche al server
    "polymorph",          # Compatibilità tra mod, necessaria al server
    "journeymap",         # Fornisce dati API al server anche se è una minimappa client
    "kotlinforforge",     # Libreria Kotlin necessaria a mod server-side (es. tinkers)
    "connector",          # Bridge Fabric-to-Forge, spesso necessario
}

def get_final_side(jar_path: Path, metadata: dict) -> str:
    """
    Combina il risultato del parser con la mappa di override.
    Priorità assoluta: se in SERVER_SIDE_FORCE_INCLUDE, va sempre al server.
    """
    mod_name_lower = jar_path.stem.lower()

    # 1. Controllo override forzato verso il server
    if any(keyword in mod_name_lower for keyword in SERVER_SIDE_FORCE_INCLUDE):
        print(f"    [INFO] Override: {jar_path.name} forzato a SERVER (libreria API necessaria)")
        return 'both'  # 'both' garantisce la copia nel server

    # 2. Se il parser ha identificato 'client', rispetta
    if metadata['side'] == 'client':
        return 'client'

    # 3. Rispetta il parsing dinamico altrimenti
    return metadata['side']


def main():
    parser = argparse.ArgumentParser(description='Separazione intelligente mod server-side')
    parser.add_argument('--input', type=Path, default=MODS_SOURCE)
    parser.add_argument('--output', type=Path, default=SERVER_MODS_DIR)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Errore: Cartella di input {args.input} non trovata.")
        sys.exit(1)

    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Analisi mod in: {args.input}")
    print(f"Destinazione server: {args.output}")

    # Statistiche
    stats = {'server': 0, 'client': 0, 'unknown': 0}

    # Processamento
    for jar_path in args.input.glob("*.jar"):
        # 1. Analisi Metadati Interni
        metadata = ModMetadataParser.get_jar_metadata(jar_path)

        # 2. Applica logica di override
        final_side = get_final_side(jar_path, metadata)

        # 3. Decisione
        if final_side in ['both', 'server']:
            shutil.copy2(jar_path, args.output / jar_path.name)
            stats['server'] += 1
            print(f"[SERVER] {jar_path.name}")
        elif final_side == 'client':
            stats['client'] += 1
            print(f"[CLIENT] {jar_path.name}")
        else:
            # Qui andrà il fallback API (da implementare in step successivi se necessario)
            stats['unknown'] += 1
            print(f"[UNKNOWN] {jar_path.name}")

    print("\n--- ANALISI COMPLETATA ---")
    print(f"Mod Server-Ready copiate: {stats['server']}")
    print(f"Mod Client-Only ignorate: {stats['client']}")
    print(f"Mod da verificare (API): {stats['unknown']}")

if __name__ == '__main__':
    main()
