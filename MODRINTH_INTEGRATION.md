# Integrazione API Modrinth - ForgeModSearch v3.4.0

## Panoramica

Questa versione di ForgeModSearch integra l'API pubblica di Modrinth come **unica fonte di verifica online**. CurseForge è stata rimossa. L'obiettivo è:

1. **Azzerare i falsi positivi** sulle mod con `displayTest="both"`
2. **Risolvere i casi UNKNOWN** dove l'analisi statica non può determinare la classificazione
3. **Migliorare l'affidabilità** della classificazione tramite dati ufficiali da Modrinth
4. **Correggere le mod BOTH mancanti** (JEI, REI, EMI, Jade, ecc.)

---

## Flusso di Lavoro

### 1. Analisi Statica (Prima Priorità)

Lo script legge prima i file di configurazione interni alle mod:
- `fabric.mod.json`
- `META-INF/mods.toml`
- `META-INF/neoforge.mods.toml`

Se questi file sono presenti e leggibili, la classificazione viene effettuata senza usare le API.

### 2. Verifica Online (Solo se necessario)

L'API Modrinth viene usata SOLO in questi casi:
- **UNKNOWN**: La classificazione statica non ha fornito informazioni
- **CLIENT_ONLY con affidabilità < 90%**: Verifica se è un falso positivo
- **BOTH con displayTest="both" e fiducia < 95%**: Verifica se è un vero BOTH o un client-only che "mente"

### 3. Classificazione Modrinth

**Endpoint**: `GET https://api.modrinth.com/v2/project/{slug}`

**Header obbligatori**:
```
User-Agent: ForgeModSearch/3.2.0 (Riccardo.Contatto.GitHub)
```

**Logica di classificazione**:
```python
client_side = mod_data.get('client_side', '')
server_side = mod_data.get('server_side', '')

# 1. Prima controlla la whitelist di mod note che sono BOTH
if mod_lower in BOTH_WHITELIST:
    → BOTH (98% fiducia)

# 2. Poi logica normale Modrinth
if client_side in ('unsupported',) and server_side in ('required', 'optional'):
    → SERVER_ONLY
elif client_side in ('required', 'optional') and server_side in ('unsupported',):
    → CLIENT_ONLY
elif client_side not in ('unsupported',) and server_side not in ('unsupported',):
    → BOTH
else:
    → UNKNOWN
```

---

## Gestione Cache

### File di Cache: `cf_cache.json`

La cache memorizza i risultati delle chiamate API per evitare chiamate duplicate.

**Struttura**:
```json
{
  "journeymap": {
    "title": "Journeymap",
    "slug": "journeymap",
    "client_side": "unsupported",
    "server_side": "required",
    "versions": ["5.10.3", "5.10.2", ...],
    ...
  }
}
```

**Flusso**:
1. Prima di ogni chiamata API, il dizionario viene caricato da `cf_cache.json`
2. Se il risultato è in cache, viene usato direttamente
3. Altrimenti, si chiama l'API, si aggiorna il dizionario e si salva su `cf_cache.json`

---

## Funzione Principale: `analyze_mod()`

### Sintassi

```python
from forge_mod_separation import analyze_mod

result = analyze_mod(Path("journeymap-1.20.1-5.10.3-forge.jar"))
```

### Parametri

- `jar_path` (Path): Percorso completo del file .jar

### Risposta

```python
{
    'path': 'journeymap-1.20.1-5.10.3-forge.jar',
    'name': 'journeymap-1.20.1-5.10.3-forge.jar',
    'status': 'CLIENT_ONLY',
    'reason': 'Modrinth: client_side=required/optional, server_side=unsupported',
    'confidence': 0.95,
    'source': 'modrinth',
    'modrinth_data': {...},  # Dati Modrinth se usati
    'modrinth_used': True,
    'modrinth_error': None,
    'display_test': 'both',
    'config_file': None,
}
```

---

## Funzioni di Supporto

### `clean_mod_name(mod_name: str) -> str`

Estrae uno slug pulito dal nome del file .jar.

**Esempi**:
- `journeymap-1.20.1-5.10.3-forge.jar` → `journeymap`
- `sodium-1.20.1-0.5.0+build.183.jar` → `sodium`
- `embeddium-0.3.13+minecraft.1.20.1-forge.jar` → `embeddium`

### `extract_mod_slug_from_path(jar_path: str) -> str`

Estrae lo slug pulito direttamente dal percorso del file.

### `search_modrinth(slug: str) -> dict`

Cerca una mod su Modrinth API.

### `classify_modrinth(mod_data: dict) -> Tuple[str, str, float, str, str, str, str]`

Classifica una mod basandosi sui dati Modrinth. Restituisce:
- `status`: CLIENT_ONLY, SERVER_ONLY, BOTH, UNKNOWN
- `reason`: Motivo della classificazione
- `confidence`: Livello di affidabilità (0.0 - 1.0)
- `full_reason`: Motivo completo con dati Modrinth
- `modrinth_name`: Nome della mod da Modrinth (usando `title`)
- `modrinth_slug`: Slug della mod
- `modrinth_version`: Versione più recente (usando `versions[0]`)

### `analyze_mod_with_modrinth(jar_path: str) -> dict`

Analizza una mod usando Modrinth API (fallback se l'analisi statica fallisce).

### `update_cache(mod_identifier: str, mod_data: dict) -> bool`

Salva i dati nella cache.

---

## Funzione Principale: `process_modpack()`

Questa funzione gestisce automaticamente tutto il flusso:

```python
from forge_mod_separation import process_modpack

results = process_modpack(
    input_folder=Path("./mods"),
    output_folder=Path("./mods"),
    dry_run=False,
    list_only=False,
)
```

---

## Uso dalla Linea di Comando

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

## Output del Report

Il report finale (`mod_analysis_report.txt`) include:

- **STATISTICHE**: Totale, Client-Only, Server-Only, Both, Unknown
- **MODRINTH CHECKED**: Numero di mod verificate tramite Modrinth
- **STATIC ONLY**: Numero di mod classificate solo tramite analisi statica
- **DETAILED LIST**: Per ogni mod, indica se è stato usato Modrinth

**Esempio di entry nel report**:
```
[CLIENT_ONLY]
  Mod: journeymap-1.20.1-5.10.3-forge.jar
  Percorso: mods/journeymap-1.20.1-5.10.3-forge.jar
  Motivo: Modrinth: client_side=required, server_side=unsupported
  Affidabilità: 95%
  Fonte: MODRINTH
  Modrinth Title: Journeymap
  Modrinth Slug: journeymap
  Modrinth Version: 5.10.3
```

---

## Note Importanti

1. **Solo Modrinth**: CurseForge completamente rimossa.
2. **Modrinth è prioritaria**: Viene usata per verificare mod UNKNOWN o con bassa affidabilità.
3. **Cache locale**: La cache migliora le prestazioni riducendo le chiamate API duplicate.
4. **User-Agent**: `ForgeModSearch/3.2.0 (Riccardo.Contatto.GitHub)` è obbligatorio per evitare i rate limit.
5. **Timeout**: 10 secondi per ogni chiamata API.
6. **Librerie standard**: Usa solo `urllib.request`, nessuna dipendenza esterna.
7. **Nomi dei file**: Le mod vengono copiate nella cartella "Server Mod" con il **nome originale** (con estensione .jar).
8. **Threshold di fiducia**: Aumentato a 0.90 per evitare falsi positivi.
9. **API Modrinth CORRETTO**: Usa i campi `title` e `versions` invece di `name` e `latestVersion`.
10. **WHITELIST BOTH**: Mod note come JEI, REI, EMI, Jade, ecc. sono forzatate come BOTH.

---

## Gestione Errori

### HTTPError (404)

- **404**: Mod non trovata su Modrinth
- In questo caso, la mod rimane classificata come UNKNOWN

### Timeout

Il timeout è impostato a 10 secondi per ogni chiamata API.

### Errore di Rete

Se c'è un errore di rete, viene stampato un `[WARN]` e la mod viene classificata come UNKNOWN.

---

## Changelog

### v3.4.0 (2026-10-23)

- **CORRETTO**: Aggiunta `BOTH_WHITELIST` con mod note che sono BOTH anche se client_side=required
- **CORRETTO**: Mod JEI, REI, EMI, Jade, Entity Model Features, Entity Texture Features, ecc. ora classificate correttamente come BOTH
- **CORRETTO**: Logica di classificazione controlla la whitelist PRIMA della logica normale Modrinth
- **CORRETTO**: Risoluzione del problema che causava crash del server

### v3.3.0 (2026-10-22)

- **CORRETTO**: API Modrinth usa i campi corretti `title` e `versions` invece di `name` e `latestVersion`
- **CORRETTO**: Parsing dati Modrinth ora restituisce correttamente name, slug, version
- **CORRETTO**: Report mostra "Modrinth Title" invece di "Modrinth Name"
- **CORRETTO**: Report mostra "Modrinth Version" con il primo elemento dell'array `versions`

### v3.2.0 (2026-10-22)

- **MIGLIORATO**: Parsing dati Modrinth corretto - ora estrae correttamente name, slug, version
- **MIGLIORATO**: Threshold di fiducia aumentato da 0.85 a 0.90 per evitare falsi positivi
- **MIGLIORATO**: Logica di classificazione più robusta per displayTest="both"
- **MIGLIORATO**: Gestione migliore dei casi ambigui
- **MIGLIORATO**: Funzione `update_cache()` separata per migliorare la cache

### v3.1.0 (2026-10-22)

- **CORRETTO**: Le mod vengono copiate nella cartella "Server Mod" con il nome originale (con estensione .jar)
- **MIGLIORATO**: Gestione del percorso di destinazione corretta

### v3.0.0 (2026-10-22)

- **MIGRATO**: Rimossa CurseForge, ora solo Modrinth API
- **RISTRUTTURATO**: Flusso semplificato con funzione `analyze_mod()` unifica il processo
- **MIGLIORATO**: Timeout API aumentato a 10 secondi
- **MIGLIORATO**: Gestione errori più robusta
- **RIASSUNTO**: Codice ridotto da 787 a 415 righe (curseforge_checker.py)

### v2.5.0

- Integrazione API Modrinth come priorità
- Gestione cache locale (`cf_cache.json`)
- CurseForge ora è fallback invece che principale

### v2.1.0

- Analisi statica (lettura dei file .toml/.json) e blacklist

---

## Licenza

Questo script è fornito come parte del progetto ForgeModSearch.