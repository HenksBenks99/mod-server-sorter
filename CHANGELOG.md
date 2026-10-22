# Changelog

Tutti i cambiamenti importanti per questo progetto sono documentati in questo file.

## [3.5.0] - 2026-10-23

### Aggiunti
- **Fallback automatico su CurseForge API**: Quando Modrinth non trova una mod (404), il fallback su CurseForge è automatico
- **Nuova funzione `search_curseforge()`**: Cerca mod su CurseForge API con parametri corretti
- **Nuova funzione `classify_curseforge()`**: Classifica mod basandosi sulle categorie CurseForge
- **File di configurazione `config.example.py`**: Template per configurazioni personalizzate
- **File `.gitignore` aggiornato**: Esclude `config.py`, `cf_cache.json`, `*.env`, `*.cache`
- **File `README.md` aggiornato**: Istruzioni complete su come configurare le API

### Corretto
- **Header Authorization CurseForge**: Cambiato da `Authorization: Bearer` a `x-api-key`
- **Parametri URL CurseForge**: Aggiunti `classId=6`, `sortField`, `sortOrder`, `pageSize`
- **Parsing dei dati CurseForge**: Estrazione corretta di `title`, `slug`, `version`, `categories`
- **Categorie client-only**: Aggiunte categorie 423, 6814, 421, 414
- **Variabile `CURSEFORGE_CLASS_ID`**: Corretto errore `name 'CURSEFORGE_CLASS_ID' is not defined`

### Testati
- **API Modrinth**: Funzionante (testato)
- **API CurseForge**: Funzionante (testato con testapicurse.py)
- **Fallback automatico**: Attivo e funzionante
- **Classificazione Journeymap**: CLIENT_ONLY su CurseForge (categoria 423)
- **Classificazione Architectury**: BOTH su CurseForge (categoria API and Library)

---

## [3.4.0] - 2026-10-23

### Aggiunti
- **`BOTH_WHITELIST`**: Lista di mod note classificate come BOTH anche se `client_side=required`
- **Funzione `classify_curseforge()`**: Classifica mod basandosi sulle categorie CurseForge

### Corretto
- **Parsing dati Modrinth**: Usato `mod_data.get('title', '')` invece di `mod_data.get('name', '')`
- **Parsing dati Modrinth**: Usato `mod_data.get('versions', [])[0]` invece di `mod_data.get('latestVersion', '')`
- **Report**: Mostrato "Modrinth Title" invece di "Modrinth Name"

---

## [3.3.0] - 2026-10-22

### Corretto
- **API Modrinth**: Usa i campi corretti `title` e `versions` invece di `name` e `latestVersion`
- **Parsing dati Modrinth**: Ora restituisce correttamente name, slug, version
- **Report**: Mostra "Modrinth Title" invece di "Modrinth Name"

---

## [3.2.0] - 2026-10-22

### Migliorato
- **Parsing dati Modrinth**: Ora estrae correttamente name, slug, version
- **Threshold di fiducia**: Aumentato da 0.85 a 0.90 per evitare falsi positivi
- **Logica di classificazione**: Più robusta per displayTest="both"
- **Funzione `update_cache()`**: Separata per migliorare la cache

### Corretto
- **Nomi dei file**: Le mod vengono copiate nella cartella "Server Mod" con il nome originale (con estensione .jar)

---

## [3.1.0] - 2026-10-22

### Corretto
- **Nomi dei file**: Le mod vengono copiate nella cartella "Server Mod" con il nome originale (con estensione .jar)

---

## [3.0.0] - 2026-10-22

### Migrato
- **Rimossa CurseForge**: Ora solo Modrinth API + classificazione statica

### Ristrutturato
- **Flusso semplificato**: Funzione `analyze_mod()` unifica il processo
- **Timeout API aumentato**: Da 5 a 10 secondi
- **Gestione errori più robusta**

---

## [2.5.0] - 2026-10-21

### Aggiunto
- **Integrazione API Modrinth come priorità**
- **Gestione cache locale** (`cf_cache.json`)
- **CurseForge ora è fallback** invece che principale

---

## [2.1.0] - 2026-10-20

### Aggiunto
- **Analisi statica** (lettura dei file .toml/.json)
- **Blacklist** per classificazione rapida

---

## [1.2.0] - 2026-10-22

### Aggiunto
- **Analisi statica** (lettura dei file .toml/.json)
- **Blacklist** per classificazione rapida

---

## [1.0.0] - 2026-10-19

### Rilascio iniziale
- **Analisi statica**
- **Classificazione basata su nome**
- **Blacklist/Whitelist**

---

<div align="center">

**ForgeModSearch - Made with ❤️ by Riccardo**

</div>