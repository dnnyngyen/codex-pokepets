#!/usr/bin/env python3
"""Build an offline, species-level exploration; this does not configure the companion.

Download pokemon_species.csv, pokemon.csv and pokemon_stats.csv from
https://github.com/PokeAPI/pokeapi/tree/d4f9a4af58ade123fbc0558f68b1c69daa97d9e4/data/v2/csv
then run: python3 tools/explore-evolutions.py /path/to/csv-directory
"""

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(directory, name):
    """Read a local UTF-8 CSV table into named fields."""
    with (directory / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main():
    """Join local species and stat tables with the registry to write proposed context bands."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_directory", type=Path)
    args = parser.parse_args()
    species = {int(s["id"]): s for s in rows(args.csv_directory, "pokemon_species.csv")}
    defaults = {int(p["species_id"]): int(p["id"]) for p in rows(args.csv_directory, "pokemon.csv")
                if p["is_default"] == "1"}
    stats = defaultdict(int)
    for stat in rows(args.csv_directory, "pokemon_stats.csv"):
        if 1 <= int(stat["stat_id"]) <= 6:
            stats[int(stat["pokemon_id"])] += int(stat["base_stat"])
    children = defaultdict(list)
    for key, entry in species.items():
        if entry["evolves_from_species_id"]:
            children[int(entry["evolves_from_species_id"])].append(key)

    def leaves(key):
        """List terminal descendants while preserving each species-level branch."""
        if not children[key]:
            return [key]
        return [leaf for child in children[key] for leaf in leaves(child)]

    def lineage(key):
        """Follow parent links and return the root-to-selected-species path."""
        path = [key]
        while species[key]["evolves_from_species_id"]:
            key = int(species[key]["evolves_from_species_id"])
            path.append(key)
        return list(reversed(path))

    registry = json.loads((ROOT / "pets.json").read_text())["pets"]
    available = {(p["pokedex_id"], p["style"]) for p in registry if p["category"] == "pokemon"}
    records = []
    for pet in registry:
        key = pet["pokedex_id"]
        for final in leaves(key):
            path = lineage(final)
            names = [species[node]["identifier"] for node in path]
            totals = [stats[defaults[node]] for node in path]
            # Cosmetic proposal: each form's share of the 0–90% band is its BST
            # divided by the path's total BST. Evolution order comes from the tree.
            cursor = 0
            bands = []
            for name, total in reversed(list(zip(names, totals))):
                end = cursor + 90 * total / sum(totals)
                bands.append(f"{name} [{cursor:.2f},{end:.2f})")
                cursor = end
            bands.append("pokeball [90,100]")
            records.append({
                "pet_slug": pet["slug"],
                "species": species[key]["identifier"],
                "style": pet["style"],
                "minimum_species": names[0],
                "maximum_species": names[-1],
                "possible_final_count": len(leaves(key)),
                "path_min_to_max": " > ".join(names),
                "species_default_bst_min_to_max": " > ".join(map(str, totals)),
                "proposed_context_bands_percent": "; ".join(bands),
                "missing_base_species_assets": ";".join(species[node]["identifier"] for node in path
                                                          if (node, pet["style"]) not in available),
                "mapping_scope": "species-only; form-conditional routes not resolved",
            })
    output = ROOT / "docs" / "evolution-ranges.csv"
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    print(f"{len(registry)} pet entries / {len(records)} branch rows written to {output}")


if __name__ == "__main__":
    main()
