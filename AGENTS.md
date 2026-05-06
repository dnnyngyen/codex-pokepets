# AGENTS.md

Conventions and file layout for AI coding agents working on this repo.

## What this repo is

`codex-pokepets` is a drop-in pet pack for [OpenAI Codex](https://openai.com/codex). It ships **1738 prebuilt pets** sourced from existing animated Pokémon sprites — no AI generation, no model output, no build pipeline.

- **2D pixel-art** (Gen 1-5, 734 pets): originally generated from PokeAPI Black/White animated GIFs.
- **3D animated** (Gen 1-9, 1004 pets): originally generated from Pokémon Showdown community-animated GIFs. Slug suffix `-3d`.

Both styles coexist. A user can install `charizard` and `charizard-3d` side-by-side. The build pipeline that originally generated these pets is **not shipped** — this repo is a finished pet pack, not a generator.

## Repo layout

```
codex-pokepets/
├── pets/                       # 1738 prebuilt pets (the whole point)
│   └── <slug>/
│       ├── pet.json            # 4-field Codex contract
│       ├── spritesheet.webp    # 1536×1872, 8×9 grid of 192×208 cells
│       └── preview.gif         # rendered idle row preview
├── pets.json                   # top-level registry (schema v4)
├── assets/hero.gif             # README header image (animated 4×3 pet grid)
├── install-pet.sh              # the only installer — curl-pipe-bash, fetches per-pet
├── README.md
├── LICENSE                     # MIT for install scripts + registry; fan-use for sprite imagery
└── AGENTS.md
```

## The Codex pet contract

A Codex pet is exactly two files: `pet.json` and `spritesheet.webp`. Per-pet `pet.json`:

```json
{
  "id": "charizard",
  "displayName": "Charizard",
  "description": "Flame Pokémon. Spits fire hot enough to melt boulders.",
  "spritesheetPath": "spritesheet.webp"
}
```

The atlas is **1536×1872 WebP**, an **8×9 grid of 192×208 cells**, with 9 hardcoded animation rows (idle, running-right, running-left, waving, jumping, failed, waiting, running, review). Codex plays each row with hardcoded per-row frame durations.

## Slug conventions

- 2D base species: `charizard` (matches PokeAPI canonical name)
- 2D form variants: `charizard-mega-x`, `deoxys-attack`, `unown-z` (PokeAPI form suffix)
- 3D variants: append `-3d` to the species slug → `charizard-3d`, `gholdengo-3d`

The 3D set is base species only — Showdown does not animate alt forms, so the 85 forms remain 2D-only.

## The pets.json registry (schema v4)

Top-level keys: `version`, `sources`, `license_note`, `counts_by_style`, `counts_by_gen`, `counts_by_category`, `total`, `pets`.

Per-pet entry:

```json
{
  "slug": "charizard-3d",
  "name": "Charizard (3D)",
  "description": "...",
  "category": "pokemon",
  "style": "3d",
  "gen": 1,
  "pokedex_id": 6,
  "species_slug": "charizard",
  "license": "fan-use",
  "author": "codex-pokepets"
}
```

`species_slug` is present on form variants and 3D entries — both installers use it to resolve a bare species name to its forms (and to map a Gen 6+ species name to its 3D pet).

## Install script

`install-pet.sh` is the only installer. It runs via curl-pipe-bash, fetches `pets.json` from `raw.githubusercontent.com` to resolve names, then per-pet downloads `pet.json` + `spritesheet.webp` into `~/.codex/pets/<slug>/`.

Resolution rules (no flags, pure positional):

| User types | Resolves to |
|---|---|
| `charizard` (2D species exists) | `charizard` + all 2D forms |
| `charizard-3d` | `charizard-3d` only |
| `cinderace` (Gen 6+, no 2D) | `cinderace-3d` (alias — bare slug points at the 3D pet) |
| `deoxys-attack` | `deoxys-attack` only (specific form) |
| Multiple names | Each resolves independently, results deduped |

Implementation: Python snippet against `pets.json`. A name that exactly matches a 2D base species expands to its 2D family. A name that exactly matches a 3D / form / form-3d entry installs only that. A name that doesn't match any slug but matches a `species_slug` (the Gen 6+ case) expands via that mapping.

## Source attribution

- 2D sprites © Nintendo / Game Freak / Creatures Inc., from [PokeAPI/sprites](https://github.com/PokeAPI/sprites) (Gen 5 BW animated).
- 3D sprites from [Pokémon Showdown community animated set](https://play.pokemonshowdown.com/sprites/ani/).
- Non-commercial fan use. See `LICENSE` for the split between MIT (install scripts + metadata) and fan-use (sprite imagery).
