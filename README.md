<!--
  Suggested GitHub repo description (one line, ~120 chars):
    Every Pokémon as a Codex pet: 2D pixel-art (Gen 1–5) + 3D community-animated (Gen 1–9). One curl install.
  Suggested topics:
    codex, openai-codex, codex-pet, codex-pets, custom-pet, pokemon, pixel-art, spritesheet, pokeapi, pokemon-showdown, fan-art, pet-pack
-->

<h1 align="center">Codex PokéPets</h1>

<p align="center">
  <a href="pets/"><img src="https://img.shields.io/badge/pets-1738-ff5d5d" alt="1738 pets"></a>
  <a href="#"><img src="https://img.shields.io/badge/Pok%C3%A9mon-Gen%201--9-3b82f6" alt="Pokémon Gen 1-9"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT%20%2B%20fan--use-yellow" alt="License: MIT + fan-use"></a>
</p>

<p align="center"><img src="assets/hero.gif" alt="codex-pokepets hero" width="640"></p>

**Every Pokémon as a [Codex](https://github.com/openai/codex) pet**,
sourced from existing animated sprites. No AI generation, no re-drawing.

- **2D pixel-art**: 649 Gen 1–5 Pokémon plus 85 alt forms
- **3D animated**: 1004 Gen 1–9 Pokémon (use `-3d` suffix)

## Install

Install one or more pets directly into `~/.codex/pets/` without cloning
anything. Just type the Pokémon's name:

```bash
curl -fsSL https://raw.githubusercontent.com/dnnyngyen/codex-pokepets/main/install-pet.sh | bash -s -- charizard
```

<p><img src="pets/charizard/preview.gif" width="80" alt="charizard"></p>

> 3D variants use the `-3d` suffix (`charizard-3d`). Forms use PokeAPI's
> hyphen convention (`deoxys-attack`, `unown-z`, `arceus-fire`).

For the 3D animated version, add `-3d`:

```bash
curl -fsSL https://raw.githubusercontent.com/dnnyngyen/codex-pokepets/main/install-pet.sh | bash -s -- charizard-3d
```

<p><img src="pets/charizard-3d/preview.gif" width="80" alt="charizard-3d"></p>

Pokémon with alternate forms (Rotom, Unown, Arceus, etc.) install all
their forms together by default:

```bash
curl -fsSL https://raw.githubusercontent.com/dnnyngyen/codex-pokepets/main/install-pet.sh | bash -s -- rotom
```

<p>
  <img src="pets/rotom/preview.gif" width="80" alt="rotom">
  <img src="pets/rotom-fan/preview.gif" width="80" alt="rotom-fan">
  <img src="pets/rotom-frost/preview.gif" width="80" alt="rotom-frost">
  <img src="pets/rotom-heat/preview.gif" width="80" alt="rotom-heat">
  <img src="pets/rotom-mow/preview.gif" width="80" alt="rotom-mow">
  <img src="pets/rotom-wash/preview.gif" width="80" alt="rotom-wash">
</p>

For one specific form, type the form's full name:

```bash
curl -fsSL https://raw.githubusercontent.com/dnnyngyen/codex-pokepets/main/install-pet.sh | bash -s -- rotom-wash
```

<p><img src="pets/rotom-wash/preview.gif" width="80" alt="rotom-wash"></p>

> Gen 6+ Pokémon (Cinderace, Gholdengo, Koraidon, etc.) only have a 3D
> version, so the bare name installs that automatically — no `-3d` needed.

Install several at once by listing them:

```bash
curl -fsSL https://raw.githubusercontent.com/dnnyngyen/codex-pokepets/main/install-pet.sh | bash -s -- charizard mewtwo lucario garchomp
```

<p>
  <img src="pets/charizard/preview.gif" width="80" alt="charizard">
  <img src="pets/mewtwo/preview.gif" width="80" alt="mewtwo">
  <img src="pets/lucario/preview.gif" width="80" alt="lucario">
  <img src="pets/garchomp/preview.gif" width="80" alt="garchomp">
</p>

Then restart Codex and pick your pet in **Settings → Appearance → Pets**.
To uninstall: `rm -rf ~/.codex/pets/<slug>`.

## Featured pets

### 2D (Gen 1–5, PokeAPI BW animated)

<p align="center"><img src="assets/featured-2d.gif" alt="featured 2D pets" width="640"></p>

Featured: charizard, lucario, rayquaza, garchomp, umbreon, gengar, mewtwo,
tyranitar, bulbasaur, lugia, chandelure, pikachu, eevee, luxray, zoroark,
flygon.

### 3D (Gen 1–9, Pokemon Showdown animated)

<p align="center"><img src="assets/featured-3d.gif" alt="featured 3D pets" width="640"></p>

Featured: greninja, lucario, mimikyu, charizard, umbreon, sylveon, garchomp,
rayquaza, gardevoir, gengar, dragapult, tyranitar, mewtwo, eevee, pikachu,
aegislash. (All install with `<name>-3d`.)

## Browse

- [pets/](pets/) — every directory has `pet.json`, `spritesheet.webp`, and `preview.gif`
- [pets.json](pets.json) — registry index with slug, name, gen, pokedex_id, style, form

## Sources & licensing

Pokémon sprites are © Nintendo / Game Freak / Creatures Inc.

- **2D pets:** sourced from [PokeAPI/sprites](https://github.com/PokeAPI/sprites) (BW animated set, public since 2014).
- **3D pets:** sourced from [Pokémon Showdown](https://play.pokemonshowdown.com/sprites/ani/) community-animated sprites.

[LICENSE](LICENSE) is split: MIT for install scripts and registry metadata,
fan-use only for sprite imagery (personal Codex companions, no commercial use).
This is a fan work, not affiliated with or endorsed by Nintendo, Game Freak,
The Pokémon Company, or Pokémon Showdown.

## Thanks

This pack only exists because of upstream work. None of the sprite imagery
here was drawn for this repo.

- The [PokeAPI](https://github.com/PokeAPI/sprites) project, for openly
  hosting Pokémon Black & White animated sprites since 2014. The 2D pets
  in this pack are derived from GIFs served by `PokeAPI/sprites`.
- The [Smogon community](https://www.smogon.com/), whose individual
  spriters are credited in
  [the PokeAPI README](https://github.com/PokeAPI/sprites#thanks) for the
  custom B&W-style sprites covering post-Gen-5 Pokémon.
- [Pokémon Showdown](https://github.com/smogon/pokemon-showdown), the
  free and open-source battle simulator, for the 3D animated sprite set
  every `-3d` pet here is derived from.

All credit chains back to the original sprite art by Game Freak, Creatures
Inc., and Nintendo. This pack is a downstream re-packaging.
