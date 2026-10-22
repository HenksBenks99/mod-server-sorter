#!/usr/bin/env python3
"""
Configuration file for ForgeModSearch
======================================

⚠️  IMPORTANT: NEVER commit this file to Git!
⚠️  Use config.example.py as a template instead.
⚠️  Add this file to .gitignore

To use CurseForge API (optional):
1. Go to https://app.curseforge.com/api
2. Create a Personal Access Token
3. Copy the token and paste it below
4. Save this file as config.py (not config.example.py)
"""

# ============================================================================
# MODRINTH API (PRIORITARIA)
# ============================================================================
# Modrinth API non richiede autenticazione
# URL: https://api.modrinth.com/v2/project/{slug}
# User-Agent obbligatorio per evitare rate limit
MODRINTH_BASE_URL = "https://api.modrinth.com/v2/project"
MODRINTH_HEADERS = {
    'User-Agent': 'ForgeModSearch/3.5.0 (Riccardo.Contatto.GitHub)',
}

# ============================================================================
# CURSEFORGE API (FALLBACK AUTOMATICO - OPZIONALE)
# ============================================================================
# CurseForge API richiede una API key personale
# URL: https://app.curseforge.com/api
# 
# CONFIGURARE: Commenta la riga qui sotto e inserisci la tua API key
# per abilitare il fallback automatico su CurseForge

# DISABILITATO: CurseForge API non configurata
CURSEFORGE_API_KEY = None  

# Configurazione CurseForge (usata solo se CURSEFORGE_API_KEY è impostata)
CURSEFORGE_BASE_URL = "https://api.curseforge.com/v1"
CURSEFORGE_GAME_ID = 432  # Minecraft
CURSEFORGE_MODS_ENDPOINT = "/mods/search"
CURSEFORGE_CLASS_ID = 6  # Solo Mods (esclude risorse e pacchetti)

# Categorie Client-Only note su CurseForge:
# 421: API and Library
# 414: Player Transport  
# 423: Map and Information (Minimappe)
# 424: Cosmetic
# 436: Food
# 6814: Optimization/Performance (Shaders)
# 425: Utility / Miscellaneous
CURSEFORGE_CATEGORIES = {
    421: "API and Library",
    414: "Player Transport",
    423: "Map and Information",
    424: "Cosmetic",
    436: "Food",
    6814: "Optimization/Performance",
    425: "Utility / Miscellaneous",
}

# Categorie che identificano mod strettamente Client-Only
STRICT_CLIENT_CATEGORIES = {
    423,   # Map and Information (Minimappe)
    6814,  # Optimization / Performance (Shaders, Sodium, Embeddium)
}

# ============================================================================
# WHITELIST MOD NOTE CHE SONO BOTH ANCHE SE client_side=required
# ============================================================================
# Queste mod hanno client_side=required ma funzionano anche sul server
# DEVONO essere classificate come BOTH
BOTH_WHITELIST = {
    "jei",  # Just Enough Items
    "rei",  # Refined Storage Info / Refined Regolith
    "emi",  # Enchantment Mending Interface
    "jade",  # Jade - Advanced item/tool info
    "entity_model_features",  # Entity Model Features
    "entity_texture_features",  # Entity Texture Features
    "fallingleaves",  # Falling Leaves
    "helditemtooltips",  # Held Item Tooltips
    "holdmyitems",  # Hold My Items
    "mouse-tweaks",  # Mouse Tweaks
    "presencefootsteps",  # Presence Footsteps
    "soundphysicsremastered",  # Sound Physics Remastered
    "sounds",  # Sounds
    "immerse-ui",  # ImmerseUI
    "betterpingdisplay",  # Better Ping Display
    "inventorytweaks",  # Inventory Tweaks
    "mousewheelie",  # Mouse Wheelie
    "controlling",  # Controlling
    "ferritecore",  # FerriteCore (memory optimization)
    "distant-horizons",  # Distant Horizons
    "dynamicfps",  # Dynamic FPS
    "tconjei",  # Tinkers' Construct JEI
    "searchables",  # Searchables
    "stackrefill",  # Stack Refill
    "fabric-api",  # Fabric API (necessaria per tutto)
    "architectury",  # Architectury API
    "balm",  # Balm (MultiMod Framework)
    "cloth-config",  # Cloth Config
    "modmenu",  # Mod Menu
    "kotlinforforge",  # Kotlin for Forge (libreria)
    "geckolib",  # GeckoLib
    "polytone",  # Polytone
    "modmenu",  # Mod Menu
    "fabric-api",  # Fabric API
    "yet-another-config-lib-v3",  # YACL
    "puzzleslib",  # PuzzlesLib
    "let-s-do",  # Let's Do (various mods)
    "handcrafted",  # Handcrafted
    "cristellib",  # CristalLib
    "mdm",  # MDM (Multidimensional Mod)
    "resourcefullib",  # Resourceful Lib
    "moonlight",  # Moonlight Librarian
    "octolib",  # OctoLib
    "obscure-api",  # Obscure API
    "player-animation-lib-forge",  # Player Animation Lib
    "playeranimatorapi",  # Player Animator API
    "tinkersinnovation",  # Tinkers Innovation
    "mimimod",  # MiMiMod
    "tinkerbettercombat",  # Tinker Better Combat
    "tinkersjewelry",  # Tinkers Jewelry
    "tinkersdelight",  # Tinkers Delight
    "create-tinkers-compat",  # Create Tinkers Compat
    "create-ore-excavation",  # Create Ore Excavation
    "create-struct-arise",  # Create Structures Arise
    "create-questing",  # Create Questing
    "create-connected",  # Create Connected
    "create-deco",  # Create Decor
    "create-numismatics",  # Create Numismatics
    "create-addition",  # Create Addition
    "tconstruct",  # Tinkers Construct
    "mantle",  # Mantle
    "l2library",  # L2Library
    "ldlib",  # LDLib
    "decorative-blocks",  # Decorative Blocks
    "delightful",  # Delightful
    "does-it-tick",  # Does It Tick
    "dynamic-trees",  # Dynamic Trees
    "dynamic-trees-plus",  # Dynamic Trees Plus
    "immersive-weathering",  # Immersive Weathering
    "iter-rpg",  # Iter RPG
}

# ============================================================================
# BLACKLIST E WHITELIST
# ============================================================================

LIBRARY_DEPENDENCIES = {
    "kotlinforforge",
    "geckolib",
    "polytone",
    "modmenu",
}

CLIENT_ONLY_BLACKLIST = {
    "sodium", "rubidium", "iris", "embeddium", "embed", "ophiurei",
    "oculus", "turbo", "turbo-api", "optifine",
    "journeymap", "xaerominimap", "xaeroworldmap",
    "appleskin", "inventorytweaks", "mousewheelie", "controlling",
    "ferritecore", "jei", "rei", "emi", "waystones",
    "animatica", "cameraoverhaul", "distant-horizons", "dynamic-fps",
    "enhanced-boss-bars", "entity-model-features", "entity-texture-features",
    "fallingleaves", "flerovium", "held-item-tooltips", "holdmyitems",
    "modelfix", "mouse-tweaks", "polytone", "presence-footsteps",
    "sodium-dynamic-lights", "sodium-options-api", "sound-physics-remastered",
    "sounds", "immerse-ui", "jade", "amendments", "better-advancements",
    "better-ping-display",
    "betteradvancements", "betterpingdisplay", "distanthorizons", "dynamicfps",
    "enhancedbossbars", "entitymodelfeatures", "entitytexturefeatures",
    "fallingleaves", "flerovium", "helditemtooltips", "holdmyitems",
    "immediatelyfast", "immersiveui", "modelfix", "mousetweaks",
    "presencefootsteps", "polytone", "sodiumdynamiclights", "sodiumoptionsapi",
    "soundphysicsremastered", "sounds",
}

CLIENT_WORDS_IN_SERVER_MODS = {
    "balm", "architectury", "cloth-config", "modmenu",
}

# ============================================================================
# CACHE FILE
# ============================================================================
CACHE_FILE = "cf_cache.json"

# ============================================================================
# API MODRINTH (PRIORITARIA)
# ============================================================================
MODRINTH_BASE_URL = "https://api.modrinth.com/v2/project"
MODRINTH_HEADERS = {
    'User-Agent': 'ForgeModSearch/3.5.0 (Riccardo.Contatto.GitHub)',
}

# ============================================================================
# API CURSEFORGE (FALLBACK AUTOMATICO)
# ============================================================================
CURSEFORGE_API_KEY = None  # Lascia None se non hai una API key CurseForge
CURSEFORGE_BASE_URL = "https://api.curseforge.com/v1"
CURSEFORGE_GAME_ID = 432  # Minecraft
CURSEFORGE_MODS_ENDPOINT = "/mods/search"

# Categorie Client-Only note su CurseForge:
# 421: API and Library
# 414: Player Transport  
# 423: Map and Information (Minimappe)
# 424: Cosmetic
# 436: Food
# 6814: Optimization/Performance (Shaders)
# 425: Utility / Miscellaneous
CURSEFORGE_CATEGORIES = {
    421: "API and Library",
    414: "Player Transport",
    423: "Map and Information",
    424: "Cosmetic",
    436: "Food",
    6814: "Optimization/Performance",
    425: "Utility / Miscellaneous",
}

# Categorie che identificano mod strettamente Client-Only
STRICT_CLIENT_CATEGORIES = {
    423,   # Map and Information (Minimappe)
    6814,  # Optimization / Performance (Shaders, Sodium, Embeddium)
}

# ============================================================================
# WHITELIST MOD NOTE CHE SONO BOTH ANCHE SE client_side=required
# ============================================================================
# Queste mod hanno client_side=required ma funzionano anche sul server
# DEVONO essere classificate come BOTH
BOTH_WHITELIST = {
    "jei",  # Just Enough Items
    "rei",  # Refined Storage Info / Refined Regolith
    "emi",  # Enchantment Mending Interface
    "jade",  # Jade - Advanced item/tool info
    "entity_model_features",  # Entity Model Features
    "entity_texture_features",  # Entity Texture Features
    "fallingleaves",  # Falling Leaves
    "helditemtooltips",  # Held Item Tooltips
    "holdmyitems",  # Hold My Items
    "mouse-tweaks",  # Mouse Tweaks
    "presencefootsteps",  # Presence Footsteps
    "soundphysicsremastered",  # Sound Physics Remastered
    "sounds",  # Sounds
    "immerse-ui",  # ImmerseUI
    "betterpingdisplay",  # Better Ping Display
    "inventorytweaks",  # Inventory Tweaks
    "mousewheelie",  # Mouse Wheelie
    "controlling",  # Controlling
    "ferritecore",  # FerriteCore (memory optimization)
    "distant-horizons",  # Distant Horizons
    "dynamicfps",  # Dynamic FPS
    "tconjei",  # Tinkers' Construct JEI
    "searchables",  # Searchables
    "stackrefill",  # Stack Refill
    "fabric-api",  # Fabric API (necessaria per tutto)
    "architectury",  # Architectury API
    "balm",  # Balm (MultiMod Framework)
    "cloth-config",  # Cloth Config
    "modmenu",  # Mod Menu
    "kotlinforforge",  # Kotlin for Forge (libreria)
    "geckolib",  # GeckoLib
    "polytone",  # Polytone
    "modmenu",  # Mod Menu
    "fabric-api",  # Fabric API
    "yet-another-config-lib-v3",  # YACL
    "puzzleslib",  # PuzzlesLib
    "let-s-do",  # Let's Do (various mods)
    "handcrafted",  # Handcrafted
    "cristellib",  # CristalLib
    "mdm",  # MDM (Multidimensional Mod)
    "resourcefullib",  # Resourceful Lib
    "moonlight",  # Moonlight Librarian
    "octolib",  # OctoLib
    "obscure-api",  # Obscure API
    "player-animation-lib-forge",  # Player Animation Lib
    "playeranimatorapi",  # Player Animator API
    "tinkersinnovation",  # Tinkers Innovation
    "mimimod",  # MiMiMod
    "tinkerbettercombat",  # Tinker Better Combat
    "tinkersjewelry",  # Tinkers Jewelry
    "tinkersdelight",  # Tinkers Delight
    "create-tinkers-compat",  # Create Tinkers Compat
    "create-ore-excavation",  # Create Ore Excavation
    "create-struct-arise",  # Create Structures Arise
    "create-questing",  # Create Questing
    "create-connected",  # Create Connected
    "create-deco",  # Create Decor
    "create-numismatics",  # Create Numismatics
    "create-addition",  # Create Addition
    "tconstruct",  # Tinkers Construct
    "mantle",  # Mantle
    "l2library",  # L2Library
    "ldlib",  # LDLib
    "decorative-blocks",  # Decorative Blocks
    "delightful",  # Delightful
    "does-it-tick",  # Does It Tick
    "dynamic-trees",  # Dynamic Trees
    "dynamic-trees-plus",  # Dynamic Trees Plus
    "immersive-weathering",  # Immersive Weathering
    "iter-rpg",  # Iter RPG
}

# ============================================================================
# BLACKLIST E WHITELIST
# ============================================================================

LIBRARY_DEPENDENCIES = {
    "kotlinforforge",
    "geckolib",
    "polytone",
    "modmenu",
}

CLIENT_ONLY_BLACKLIST = {
    "sodium", "rubidium", "iris", "embeddium", "embed", "ophiurei",
    "oculus", "turbo", "turbo-api", "optifine",
    "journeymap", "xaerominimap", "xaeroworldmap",
    "appleskin", "inventorytweaks", "mousewheelie", "controlling",
    "ferritecore", "jei", "rei", "emi", "waystones",
    "animatica", "cameraoverhaul", "distant-horizons", "dynamic-fps",
    "enhanced-boss-bars", "entity-model-features", "entity-texture-features",
    "fallingleaves", "flerovium", "held-item-tooltips", "holdmyitems",
    "modelfix", "mouse-tweaks", "polytone", "presencefootsteps",
    "sodium-dynamic-lights", "sodium-options-api", "sound-physics-remastered",
    "sounds", "immerse-ui", "jade", "amendments", "better-advancements",
    "better-ping-display",
    "betteradvancements", "betterpingdisplay", "distanthorizons", "dynamicfps",
    "enhancedbossbars", "entitymodelfeatures", "entitytexturefeatures",
    "fallingleaves", "flerovium", "helditemtooltips", "holdmyitems",
    "immediatelyfast", "immersiveui", "modelfix", "mousetweaks",
    "presencefootsteps", "polytone", "sodiumdynamiclights", "sodiumoptionsapi",
    "soundphysicsremastered", "sounds",
}

CLIENT_WORDS_IN_SERVER_MODS = {
    "balm", "architectury", "cloth-config", "modmenu",
}