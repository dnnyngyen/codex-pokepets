# Evolution families and context ranges

The first PR uses **context usage only**. It starts each supported Kanto starter
family in its final form, steps back at 33% and 66%, and enters a Poké Ball at 90%
(or a configured threshold such as 95%). It recovers when usage drops. Response
grading and the stat-based ranges below are **not enabled in the companion**.

## Coverage

[The full exploration table](evolution-ranges.csv) covers all **1,738 pet entries**
in this pack, representing **1,004 species**, with **1,797 rows** because branching
families can have multiple final forms. Each row includes:

- Selected pet, style, earliest species and one reachable final species.
- The species path from earliest to final and each species' default base-stat total.
- Proposed context bands for that path and any missing base-species sprite assets.

Here, “minimum” and “maximum” mean earliest and terminal evolution stages, not
weakest and strongest combat performance. For an intermediate species, the table
includes its ancestors and each reachable terminal descendant. For a selected
terminal species, it follows that branch only. **44 pet entries** have multiple
possible terminal descendants; do not silently pick a branch for them.

The rows contain 345 one-stage paths, 836 two-stage paths, and 616 three-stage
paths. These counts include both styles, form variants and repeated paths for
different selected pets; they are not counts of distinct evolution families.
24 rows need at least one base-species sprite that this pack does not provide in
the selected style. The table identifies those gaps rather than pretending all
paths can already run in the companion.

## How to partition ranges using Pokémon stats

A possible **cosmetic policy**, separate from measuring response quality:

1. Choose a specific root-to-final evolution path.
2. Add each form's six base stats (HP, Attack, Defense, Special Attack, Special
   Defense, Speed) to obtain its base-stat total, or BST.
3. Reserve context usage at or above `ball_at` for the Poké Ball.
4. Divide `[0, ball_at)` among the forms, final to earliest, with each form's
   interval width equal to `ball_at × its BST / sum(path BSTs)`.

This gives higher-stat forms more room while keeping the family-specific bands
contiguous and bounded. It never sorts the lineage by stats. It is a proposed
game mechanic, **not a benchmark-derived model-quality threshold**. A Pokémon's
BST has no established relationship to an agent's accuracy or context capacity.
The first PR keeps the simpler configurable 33/66/90 defaults until the expanded
family behavior is reviewed.

Examples with `ball_at = 90` (rounded to two decimals; boundaries belong to the
next form, and Poké Ball covers 90–100%):

| Family / branch, final → earliest | BSTs in that order | Proposed context bands |
| --- | --- | --- |
| Charizard → Charmeleon → Charmander | 534 / 405 / 309 | 0–38.51 / 38.51–67.72 / 67.72–90 |
| Venusaur → Ivysaur → Bulbasaur | 525 / 405 / 318 | 0–37.86 / 37.86–67.07 / 67.07–90 |
| Blastoise → Wartortle → Squirtle | 530 / 405 / 314 | 0–38.19 / 38.19–67.37 / 67.37–90 |
| Gyarados → Magikarp | 540 / 200 | 0–65.68 / 65.68–90 |
| Raichu → Pikachu → Pichu | 485 / 320 / 205 | 0–43.22 / 43.22–71.73 / 71.73–90 |
| Vaporeon → Eevee | 525 / 325 | 0–55.59 / 55.59–90 |
| Mewtwo | 680 | 0–90 |

For a 95% Poké Ball threshold, multiply every pre-ball boundary by `95 / 90`.
Single-stage Pokémon keep their species until the ball threshold; do not invent
earlier evolutions. A future display could show fatigue independently of species.

## Branches, forms and unusual stats

- Eevee has eight terminal descendants in the source data. Ask the user to select
  the final form; sibling evolutions should not degrade into each other.
- Pikachu's earliest species is Pichu. A family should not stop at the selected
  pet merely because its baby evolution was introduced in a later generation.
- Nincada branches to Ninjask and Shedinja. Shedinja's default BST (236) is lower
  than Nincada's (266), so raw stat sorting or assuming every evolution increases
  BST gives the wrong stage order. Preserve the species graph.
- These are **species-level paths**. Regional/form-conditional routes are not
  resolved by `evolves_from_species_id`. For example, the Farfetch'd → Sirfetch'd
  species link must not be treated as an evolution of ordinary Kantonian
  Farfetch'd. Validate form-specific routes before expanding runtime support.
- Alternate forms and temporary battle transformations are not automatically
  additional species stages. All form entries in this report use their species'
  **default** BST, not an asserted form-specific combat score. That limitation is
  explicit in the CSV column name and mapping scope.
- Some terminal evolutions are newer than the pack's assets. An expanded runtime
  needs an explicit missing-art policy and branch choice; it must not promise a
  drawable final stage based on species metadata alone.

## Context pressure versus response quality

The only live measurement in this PR is the latest request's
`last_token_usage.total_tokens / model_context_window`. Duplicate snapshots do
not accumulate. Manual or automatic compaction restores forms on the next valid
usage update; a compaction event alone does not imply zero usage. Restarting reads
the latest state, not the worst historical state. A new session has independent
state, and the companion must be pointed at its UUID/path.

Long-context research shows that relevant-information position can affect task
performance; it does not establish a universal quality curve for current models
at 33%, 66% or 90% occupancy. See
[Lost in the Middle](https://arxiv.org/abs/2307.03172). Larger input context is a
token-volume signal, not proof that a particular response is bad or more costly
by a fixed amount; caching and model pricing are separate concerns.

If response quality is added later, keep it a separately labelled, evidence-backed
score: task-specific acceptance tests, explicit user feedback, or a rubric
validated against human judgments. A shell command's failure can be an expected
part of debugging, so raw failed-command counts should not be treated as failed
answers. [GDPval's grading methodology](https://openai.com/index/gdpval/) illustrates
the need for task-specific rubrics and calibration. No transcript is sent to a
grader, no grading model is invoked, and no quality score is inferred in this PR.

## Data and reproduction

The table is derived from the public PokeAPI CSV tables at commit
[`d4f9a4af58ade123fbc0558f68b1c69daa97d9e4`](https://github.com/PokeAPI/pokeapi/tree/d4f9a4af58ade123fbc0558f68b1c69daa97d9e4/data/v2/csv):
`pokemon_species.csv` supplies ancestry; `pokemon.csv` selects the default Pokémon
record for each species; `pokemon_stats.csv` supplies the six base stats. See the
[PokeAPI data documentation](https://pokeapi.co/docs/v2). Data attribution and
redistribution terms are retained in [POKEAPI-LICENSE.md](POKEAPI-LICENSE.md).

Download those three CSVs at that revision into a local directory, then run:

```bash
python3 tools/explore-evolutions.py /path/to/csv-directory
```

This regenerates `docs/evolution-ranges.csv` from the pack's registry. It is an
offline research utility; running the companion does not load the table or fetch
anything from PokeAPI.
