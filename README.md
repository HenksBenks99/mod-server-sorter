# ForgeModSearch - Mod Separation Tool

<div align="center">

## 🔍 Identifica e separa mod Client-Only dalle mod Server-Ready per Minecraft modpacks

**ForgeModSearch v3.5.0** - Integrazione API Modrinth + CurseForge

</div>

---

## 🎯 Caratteristiche Principali

- ✅ **Analisi Statica**: Legge `fabric.mod.json`, `mods.toml`, `neoforge.mods.toml`
- ✅ **API Modrinth** (Prioritaria): Verifica online tramite [api.modrinth.com](https://api.modrinth.com)
- ✅ **API CurseForge** (Fallback Automatico): Verifica tramite [api.curseforge.com](https://api.curseforge.com)
- ✅ **Whitelist BOTH**: Mod note classificate come BOTH anche se `client_side=required`
- ✅ **Cache Locale**: Memorizza i risultati per evitare chiamate API duplicate
- ✅ **Gestione Errori Robusta**: Timeout, retry, fallback automatico

---

## 📦 Requisiti

- **Python 3.8+**
- **Python 3.11+ consigliato** (per supporto `tomllib`)

### Installazione

```bash
# Python 3.11+ (nativo)
python --version

# Python 3.8-3.10 (usa tomli)
pip install tomli
```

---

## 🚀 Uso Rapido

### Analisi di base

```bash
python forge_mod_separation.py ./mods --output ./mods
```

### Dry-run (solo analisi, senza copia)

```bash
python forge_mod_separation.py ./mods --output ./mods --dry-run
```

### Solo lista delle mod

```bash
python forge_mod_separation.py ./mods --output ./mods --list-only
```

### Clear cache

```bash
python forge_mod_separation.py ./mods --output ./mods --clear-cache
```

### Mostra cache

```bash
python forge_mod_separation.py ./mods --output ./mods --show-cache
```

---

## ⚙️ Configurazione API

### Modrinth API (Prioritaria)

L'API Modrinth **non richiede autenticazione**:

```python
MODRINTH_BASE_URL = "https://api.modrinth.com/v2/project"
MODRINTH_HEADERS = {
    'User-Agent': 'ForgeModSearch/3.5.0 (Riccardo.Contatto.GitHub)',
}
```

**Importante**: Il header `User-Agent` è obbligatorio per evitare i rate limit!

### CurseForge API (Fallback Automatico - Opzionale)

Per abilitare il fallback automatico su CurseForge:

1. Vai su [https://app.curseforge.com/api](https://app.curseforge.com/api)
2. Crea una **Personal Access Token**
3. Copia la token e inseriscila nel file di configurazione

#### Opzione 1: File di Configurazione (Consigliato)

Crea un file `config.py` nella stessa directory:

```python
# config.py
CURSEFORGE_API_KEY = "la_tua_api_key_qui"
```

Poi modifica `forge_mod_separation.py`:

```python
from config import *  # Importa le configurazioni
```

#### Opzione 2: Variabile d'Ambiente (Più Sicuro)

```bash
# Windows
set CURSEFORGE_API_KEY=tua_api_key_qui

# Linux/Mac
export CURSEFORGE_API_KEY=tua_api_key_qui
```

Poi nel codice:

```python
import os
CURSEFORGE_API_KEY = os.environ.get('CURSEFORGE_API_KEY')
```

#### Opzione 3: Hardcoded (Sconsigliato per GitHub)

```python
# forge_mod_separation.py
CURSEFORGE_API_KEY = "la_tua_api_key_qui"  # ⚠️ Mai commitare!
```

---

## 📂 Struttura Progetto

```
forge_mod_search/
├── forge_mod_separation.py    # Script principale
├── config.example.py           # Template configurazione
├── .gitignore                  # File da ignorare da Git
├── README.md                   # Questo file
├── CHANGELOG.md                # Changelog
├── testapicurse.py             # Test API CurseForge
├── test_complete_api.py        # Test completo API
└── mods/                       # Cartella delle mod
    ├── mods-corrected/         # Mod validate manualmente
    └── Server Mod/             # Mod copiate (SERVER_ONLY + BOTH)
```

---

## 🔄 Flusso di Lavoro

### 1. Analisi Statica (Prima Priorità)

Lo script legge prima i file di configurazione interni alle mod:
- `fabric.mod.json`
- `META-INF/mods.toml`
- `META-INF/neoforge.mods.toml`

### 2. Verifica Online Modrinth (Prioritaria)

Se l'analisi statica restituisce `UNKNOWN` o fiducia < 90%:
- Chiamata API Modrinth: `GET /v2/project/{slug}`
- Classificazione basata su `client_side` e `server_side`

### 3. Fallback CurseForge (Automatico)

Se Modrinth non trova la mod (404):
- Fallback automatico su CurseForge API
- Classificazione basata sulle categorie

### 4. Whitelist BOTH

Alcune mod note sono classificate come BOTH anche se `client_side=required`:
- JEI, REI, EMI, Jade, ecc.
- Librerie come Fabric API, Architectury, ecc.

---

## 📊 Output del Report

Il report `mod_analysis_report.txt` include:

```
======================================================================
FORGEMODSEARCH - MOD ANALYSIS REPORT v3.5.0
======================================================================

STATISTICHE
----------------------------------------------------------------------
  Mod totali:              244
  Client-Only:             44
  Server-Only:             2
  Both (Client+Server):     197
  Unknown:                 1
  Modrinth Checked:        34
  Modrinth Found:          34
  Static Only:             210

DETAILED LIST
----------------------------------------------------------------------

[BOTH]
  Mod: additional_lights-1.20.1-2.1.7
  Percorso: mods/additional_lights-1.20.1-2.1.7.jar
  Motivo: CurseForge: mod server-ready (non client-only)
  Affidabilità: 85%
  Fonte: CURSEFORGE
  CurseForge Title: Additional Lights
  CurseForge Slug: additional-lights
  CurseForge Version: 2.1.7
```

---

## 🛡️ Sicurezza

### ⚠️ NON Commitare mai questi file!

- `config.py` - Contiene API key
- `cf_cache.json` - Cache locale
- `*.env` - File di ambiente

### Come proteggere le API key

1. **Usa variabili d'ambiente** (più sicuro)
2. **Usa un file di configurazione separato** (`config.py`)
3. **Mai hardcoded nel codice** (rischio di esposizione su GitHub)

### .gitignore

Il file `.gitignore` esclude automaticamente:
- `config.py`
- `cf_cache.json`
- `*.env`
- `*.cache`

---

## 🔧 Opzioni di Esecuzione

### Analisi completa

```bash
python forge_mod_separation.py ./mods --output ./mods
```

### Dry-run (solo analisi)

```bash
python forge_mod_separation.py ./mods --output ./mods --dry-run
```

### Solo lista delle mod

```bash
python forge_mod_separation.py ./mods --output ./mods --list-only
```

### Clear cache

```bash
python forge_mod_separation.py ./mods --output ./mods --clear-cache
```

### Mostra cache

```bash
python forge_mod_separation.py ./mods --output ./mods --show-cache
```

---

## 📝 Esempio di Output

```
======================================================================
  ForgeModSearch - Mod Separation Tool v3.5.0
======================================================================
  INTEGRAZIONE MODRINTH MIGLIORATA
======================================================================


Trovati 209 file .jar da analizzare...

  [additional_lights-1.20.1-2.1.7.jar]
    [BOTH] additional_lights-1.20.1-2.1.7
    TOML: displayTest="both" o entrambi gli entrypoints
    Affidabilità: 80%

    [INFO] displayTest="both" con fiducia bassa - uso Modrinth API
    [INFO] Slug Modrinth: additional-lights
    [INFO] Chiamata API Modrinth per: additional-lights
    [WARN] Mod non trovata su Modrinth
    [INFO] Fallback automatico su CurseForge API...
    [INFO] CurseForge API: risposta ricevuta

    [BOTH] additional_lights-1.20.1-2.1.7
    CurseForge: mod server-ready (non client-only)
    Affidabilità: 85%
    Fonte: CURSEFORGE
    CurseForge Title: Additional Lights
    CurseForge Slug: additional-lights
    CurseForge Version: 2.1.7
```

---

## 🐛 Debug

### Debug Modrinth

```bash
python test_complete_api.py
```

### Debug CurseForge

```bash
python testapicurse.py
```

### Test Journeymap (CLIENT_ONLY)

```bash
python test_journeymap.py
```

---

## 📜 Licenza

Questo script è fornito come parte del progetto ForgeModSearch.

---

## 🤝 Contribuire

Se vuoi contribuire, crea una issue o un pull request!

---

## 📞 Contatti

- **GitHub**: [Henks](https://github.com/HenksBenks99)
- **Email**: tuo_contatto_github

---

<div align="center">

**Made with ❤️ by Henks**

</div>
