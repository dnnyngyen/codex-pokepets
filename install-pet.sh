#!/usr/bin/env bash
# Install one or more Pokémon pets from the codex-pokepets repo into ~/.codex/pets/
# without cloning. Hits raw.githubusercontent.com directly.
#
# Usage (curl-pipe-bash):
#   curl -fsSL .../install-pet.sh | bash -s -- charizard
#   curl -fsSL .../install-pet.sh | bash -s -- charizard mewtwo lucario
#   curl -fsSL .../install-pet.sh | bash -s -- charizard-3d         # 3D variant only
#   curl -fsSL .../install-pet.sh | bash -s -- deoxys-attack        # specific form only
#   curl -fsSL .../install-pet.sh | bash -s -- cinderace            # Gen 6+ → resolves to 3D
#
# Resolution rules:
#   <species>        → species + all 2D forms (Gen 1-5 base species)
#   <species>-3d     → only the 3D variant
#   <species>        → only the 3D pet, if no 2D version exists (Gen 6-9)
#   <form-slug>      → exactly that form (e.g. deoxys-attack, charizard-mega-x)
#
# Override: CODEX_POKEPETS_REF=mybranch, CODEX_HOME=/path/to/.codex
set -euo pipefail

OWNER="${CODEX_POKEPETS_OWNER:-dnnyngyen}"
REPO="${CODEX_POKEPETS_REPO:-codex-pokepets}"
REF="${CODEX_POKEPETS_REF:-main}"
RAW="https://raw.githubusercontent.com/${OWNER}/${REPO}/${REF}"
DEST_DIR="${CODEX_HOME:-$HOME/.codex}/pets"

if [[ $# -eq 0 ]]; then
  cat <<EOF
Usage: install-pet.sh <name> [<name> ...]

Resolution:
  charizard          installs charizard (2D) + all 2D forms
  charizard-3d       installs only charizard-3d
  cinderace          installs cinderace-3d (Gen 6+ has no 2D version)
  deoxys-attack      installs only that specific form

Examples:
  install-pet.sh charizard
  install-pet.sh mewtwo lucario garchomp
  install-pet.sh charizard-3d cinderace gholdengo
  install-pet.sh deoxys-attack giratina-origin

Browse all 1738 pets:
  https://github.com/${OWNER}/${REPO}/tree/${REF}/pets
EOF
  exit 1
fi

REGISTRY="$(mktemp)"
trap 'rm -f "$REGISTRY"' EXIT
if ! curl -fsSL --output "$REGISTRY" "${RAW}/pets.json"; then
  echo "Error: failed to fetch pets.json registry from ${RAW}/pets.json" >&2
  exit 1
fi

resolved="$(python3 - "$REGISTRY" "$@" <<'PY' 2>/tmp/codex-pokepets-resolve-err
import json, sys
data = json.load(open(sys.argv[1]))
names = sys.argv[2:]
pets = data.get("pets", [])

by_slug = {p["slug"]: p for p in pets}
related_by_species = {}
for p in pets:
    sp = p.get("species_slug") or p["slug"]
    related_by_species.setdefault(sp, []).append(p)

resolved, errors = [], []
for name in names:
    entry = by_slug.get(name)
    if entry is not None:
        if entry.get("category") == "pokemon" and entry.get("style") == "2d":
            for related in related_by_species.get(name, []):
                if related.get("style") == "2d":
                    resolved.append(related["slug"])
        else:
            resolved.append(name)
    elif name in related_by_species:
        for related in related_by_species[name]:
            resolved.append(related["slug"])
    else:
        errors.append(name)

seen = set(); unique = []
for s in resolved:
    if s not in seen:
        seen.add(s); unique.append(s)
for s in unique:
    print(s)
if errors:
    print(f"__UNKNOWN__:{','.join(errors)}", file=sys.stderr)
    sys.exit(2)
PY
)" || {
  err="$(cat /tmp/codex-pokepets-resolve-err 2>/dev/null || true)"
  if [[ "$err" == *"__UNKNOWN__:"* ]]; then
    bad="${err##*__UNKNOWN__:}"
    echo "Error: unknown pet name(s): $bad" >&2
    echo "       Browse https://github.com/${OWNER}/${REPO}/tree/${REF}/pets for valid names." >&2
  else
    cat /tmp/codex-pokepets-resolve-err >&2
  fi
  rm -f /tmp/codex-pokepets-resolve-err
  exit 1
}
rm -f /tmp/codex-pokepets-resolve-err

PET_SLUGS=()
while IFS= read -r slug; do
  [[ -n "$slug" ]] && PET_SLUGS+=("$slug")
done <<< "$resolved"

[[ ${#PET_SLUGS[@]} -eq 0 ]] && { echo "No pets to install."; exit 1; }

echo "Installing ${#PET_SLUGS[@]} pet(s) into $DEST_DIR..."
mkdir -p "$DEST_DIR"
ok=0; fail=0
for slug in "${PET_SLUGS[@]}"; do
  pet_url="${RAW}/pets/${slug}/pet.json"
  sheet_url="${RAW}/pets/${slug}/spritesheet.webp"
  dst="${DEST_DIR}/${slug}"
  tmp="$(mktemp -d)"

  if ! curl -fsSL --output "${tmp}/pet.json" "$pet_url"; then
    echo "  fail: $slug not found at $pet_url" >&2
    rm -rf "$tmp"; ((fail++)); continue
  fi
  if ! curl -fsSL --output "${tmp}/spritesheet.webp" "$sheet_url"; then
    echo "  fail: spritesheet for $slug missing at $sheet_url" >&2
    rm -rf "$tmp"; ((fail++)); continue
  fi

  mkdir -p "$dst"
  mv "${tmp}/pet.json" "${dst}/pet.json"
  mv "${tmp}/spritesheet.webp" "${dst}/spritesheet.webp"
  rm -rf "$tmp"
  echo "  ok: ${slug}"
  ((ok++))
done

echo ""
echo "Done. ok=$ok fail=$fail"
echo "Restart Codex, then pick your pet in Settings → Appearance → Pets."
exit $(( fail > 0 ? 1 : 0 ))
