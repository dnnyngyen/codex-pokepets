<!--
  Suggested GitHub repo description (one line, ~120 chars):
    1738 drop-in Codex pets: 2D pixel-art (Gen 1–5) + 3D community-animated (Gen 1–9). One curl install.
  Suggested topics:
    codex, openai-codex, codex-pet, codex-pets, custom-pet, pokemon, pixel-art, spritesheet, pokeapi, pokemon-showdown, fan-art, pet-pack
-->

# Codex PokéPets

<p align="center"><img src="assets/hero.gif" alt="codex-pokepets hero" width="640"></p>

**1738 drop-in [Codex](https://github.com/openai/codex) pets** sourced from
existing animated Pokémon sprites — no AI generation, no re-drawing.

- **2D pixel-art** — 734 pets, Gen 1–5, classic Black/White animations
- **3D animated** — 1004 pets, Gen 1–9, slug suffix `-3d`

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

<p>
  <a href="pets/charizard/"><img src="pets/charizard/preview.gif" width="80" alt="charizard"></a>
  <a href="pets/pikachu/"><img src="pets/pikachu/preview.gif" width="80" alt="pikachu"></a>
  <a href="pets/mewtwo/"><img src="pets/mewtwo/preview.gif" width="80" alt="mewtwo"></a>
  <a href="pets/typhlosion/"><img src="pets/typhlosion/preview.gif" width="80" alt="typhlosion"></a>
</p>
<p>
  <a href="pets/lugia/"><img src="pets/lugia/preview.gif" width="80" alt="lugia"></a>
  <a href="pets/rayquaza/"><img src="pets/rayquaza/preview.gif" width="80" alt="rayquaza"></a>
  <a href="pets/lucario/"><img src="pets/lucario/preview.gif" width="80" alt="lucario"></a>
  <a href="pets/garchomp/"><img src="pets/garchomp/preview.gif" width="80" alt="garchomp"></a>
</p>
<p>
  <a href="pets/zoroark/"><img src="pets/zoroark/preview.gif" width="80" alt="zoroark"></a>
  <a href="pets/zekrom/"><img src="pets/zekrom/preview.gif" width="80" alt="zekrom"></a>
  <a href="pets/giratina-origin/"><img src="pets/giratina-origin/preview.gif" width="80" alt="giratina-origin"></a>
  <a href="pets/arceus-fire/"><img src="pets/arceus-fire/preview.gif" width="80" alt="arceus-fire"></a>
</p>

### 3D (Gen 1–9, Pokemon Showdown animated)

<p>
  <a href="pets/charizard-3d/"><img src="pets/charizard-3d/preview.gif" width="80" alt="charizard-3d"></a>
  <a href="pets/mewtwo-3d/"><img src="pets/mewtwo-3d/preview.gif" width="80" alt="mewtwo-3d"></a>
  <a href="pets/lucario-3d/"><img src="pets/lucario-3d/preview.gif" width="80" alt="lucario-3d"></a>
  <a href="pets/greninja-3d/"><img src="pets/greninja-3d/preview.gif" width="80" alt="greninja-3d"></a>
</p>
<p>
  <a href="pets/decidueye-3d/"><img src="pets/decidueye-3d/preview.gif" width="80" alt="decidueye-3d"></a>
  <a href="pets/zacian-3d/"><img src="pets/zacian-3d/preview.gif" width="80" alt="zacian-3d"></a>
  <a href="pets/eternatus-3d/"><img src="pets/eternatus-3d/preview.gif" width="80" alt="eternatus-3d"></a>
  <a href="pets/cinderace-3d/"><img src="pets/cinderace-3d/preview.gif" width="80" alt="cinderace-3d"></a>
</p>
<p>
  <a href="pets/sprigatito-3d/"><img src="pets/sprigatito-3d/preview.gif" width="80" alt="sprigatito-3d"></a>
  <a href="pets/koraidon-3d/"><img src="pets/koraidon-3d/preview.gif" width="80" alt="koraidon-3d"></a>
  <a href="pets/gholdengo-3d/"><img src="pets/gholdengo-3d/preview.gif" width="80" alt="gholdengo-3d"></a>
  <a href="pets/dragapult-3d/"><img src="pets/dragapult-3d/preview.gif" width="80" alt="dragapult-3d"></a>
</p>

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
