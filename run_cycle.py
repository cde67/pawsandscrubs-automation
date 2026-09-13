"""
One automation cycle for the PawsAndScrubs catalog: picks a batch of new
breed x nurse-specialty combos not yet used in any catalog_batchN.py file,
generates designs, publishes them to Printify, expands tags, and builds a
Pinterest CSV for just this new batch. Writes catalog_batchN.py so future
runs know what's already been done.

Requires PRINTIFY_API_TOKEN as an environment variable (do not hardcode it
here or commit it to the repo).
"""
import csv
import glob
import importlib
import os
import re
import sys
import time
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_design as g
import publish_products as p

SHOP_ID = 28931744
NEW_BATCH_SIZE = 12

# Pools of breeds/roles to draw new combos from. As long as this stays
# bigger than (batch size x number of runs before you refresh it), the
# script won't run out of fresh combos.
DOG_BREEDS = [
    "Boston Terrier", "Dalmatian", "Basset Hound", "Bloodhound", "Akita",
    "Samoyed", "Malamute", "Papillon", "Havanese", "Bichon Frise", "Maltese",
    "Pug", "English Bulldog", "Rhodesian Ridgeback", "Chow Chow", "Collie",
    "Sheltie", "Whippet", "Greyhound", "Basenji", "Jack Russell Terrier",
    "West Highland Terrier", "Scottish Terrier", "Bull Terrier", "Mastiff",
]
CAT_BREEDS = [
    "Russian Blue Cat", "Scottish Fold Cat", "Abyssinian Cat",
    "British Shorthair Cat", "Devon Rex Cat", "Norwegian Forest Cat",
    "Tuxedo Cat", "Tortoiseshell Cat", "Himalayan Cat",
]
ROLES = [
    "Trauma Nurse", "Recovery Nurse", "Case Manager Nurse", "Nurse Educator",
    "Wound Care Nurse", "Telemetry Nurse", "Infusion Nurse",
    "Occupational Health Nurse", "Nurse Manager", "Ambulatory Care Nurse",
    "Correctional Nurse", "Labor Nurse", "Neonatal Nurse", "Nurse Life",
    "ICU Nurse", "ER Nurse", "School Nurse", "RN Life",
]

FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def used_breeds():
    used = set()
    base = os.path.dirname(os.path.abspath(__file__))
    for path in glob.glob(os.path.join(base, "catalog_batch*.py")):
        mod_name = os.path.splitext(os.path.basename(path))[0]
        mod = importlib.import_module(mod_name)
        for combo in mod.COMBOS:
            breed = combo[0]
            for suffix in (" Mom", " Dad"):
                breed = breed.replace(suffix, "")
            used.add(breed.strip())
    return used


def next_batch_number():
    base = os.path.dirname(os.path.abspath(__file__))
    nums = [0]
    for path in glob.glob(os.path.join(base, "catalog_batch*.py")):
        m = re.search(r"catalog_batch(\d+)\.py", path)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def pick_new_combos(n):
    used = used_breeds()
    candidates = []
    for i, breed in enumerate(DOG_BREEDS):
        if breed not in used:
            role = ROLES[i % len(ROLES)]
            parent = "Mom" if i % 2 == 0 else "Dad"
            tone = "black_shirt" if i % 2 == 0 else "white_shirt"
            candidates.append((f"{breed} {parent}", role, tone, "dog"))
    for i, breed in enumerate(CAT_BREEDS):
        if breed not in used:
            role = ROLES[(i + 5) % len(ROLES)]
            tone = "black_shirt" if i % 2 == 0 else "white_shirt"
            candidates.append((f"{breed} Mom", role, tone, "cat"))
    return candidates[:n]


def build_meta(breed, role, animal, pronoun="her"):
    title = f"{breed} {role} Shirt - {animal.capitalize()} Gift Nursing Tee"
    description = (
        f"A soft, comfy unisex tee for {breed}s who are also {role}s. "
        f"The perfect gift for a {role.lower()} who loves {pronoun} {animal}."
    )
    tags = [
        breed.lower(), f"{role.lower()} gift",
        f"{animal} mom shirt" if "mom" in breed.lower() else f"{animal} dad shirt",
        "nurse life shirt", f"{animal} nurse tee",
        f"{breed.lower()} lover gift", "nurse appreciation gift",
        f"gift for {role.lower()}", f"{animal} lover shirt",
        "nurse week gift", "healthcare worker gift", "cute nurse shirt",
    ]
    seen, out = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return title, description, out[:13]


def api_with_retry(method, path, payload=None, tries=6):
    for i in range(tries):
        try:
            return p.api_request(method, path, payload)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                wait = 45 * (i + 1)
                print(f"  rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


def upload_with_retry(path, name, tries=6):
    for i in range(tries):
        try:
            return p.upload_image(path, name)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                time.sleep(45 * (i + 1))
            else:
                raise


def main():
    if not os.environ.get("PRINTIFY_API_TOKEN"):
        print("ERROR: PRINTIFY_API_TOKEN env var not set.")
        sys.exit(1)
    # publish_products.py reads the token from .env by default; override
    # its loader to use the env var instead (cloud runs won't have .env).
    p.TOKEN = os.environ["PRINTIFY_API_TOKEN"]

    combos = pick_new_combos(NEW_BATCH_SIZE)
    if not combos:
        print("No new breed combos left in the pool - add more to DOG_BREEDS/CAT_BREEDS/ROLES.")
        sys.exit(0)

    batch_num = next_batch_number()
    base = os.path.dirname(os.path.abspath(__file__))
    designs_dir = os.path.join(base, "designs")
    os.makedirs(designs_dir, exist_ok=True)

    final_combos = []
    csv_rows = []

    for breed, role, tone, animal in combos:
        slug = slugify(f"{breed}_{role}")
        pronoun = "his" if "Dad" in breed else "her"
        out_path = os.path.join(designs_dir, f"{slug}.png")
        print(f"Generating {slug}...")
        g.generate(breed, role, tone, out_path)

        title, desc, tags = build_meta(breed, role, animal, pronoun)

        print(f"Uploading {slug}...")
        image_id = upload_with_retry(out_path, f"{slug}.png")
        time.sleep(3)

        variants, print_areas = p.build_variants_and_print_areas(image_id, tone)
        product = api_with_retry("POST", f"/shops/{SHOP_ID}/products.json", {
            "title": title, "description": desc, "blueprint_id": p.BLUEPRINT_ID,
            "print_provider_id": p.PRINT_PROVIDER_ID, "variants": variants,
            "print_areas": print_areas, "tags": tags,
        })
        time.sleep(3)
        api_with_retry("POST", f"/shops/{SHOP_ID}/products/{product['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True, "tags": True
        })
        print(f"  -> {product['id']} published")
        time.sleep(3)

        final_combos.append((breed, role, tone, animal, pronoun, slug))

        # need the mockup URL + product page URL for the Pinterest CSV -
        # fetch the product back since we don't get images/external in the create response reliably yet
        prod_full = api_with_retry("GET", f"/shops/{SHOP_ID}/products/{product['id']}.json")
        media_url = prod_full["images"][0]["src"] if prod_full.get("images") else ""
        link = prod_full.get("external", {}).get("handle", "")
        board = "Cat Nurse Gifts" if animal == "cat" else "Dog Nurse Gifts"
        csv_rows.append({
            "Title": title[:100], "Media URL": media_url, "Pinterest board": board,
            "Description": desc, "Link": link,
        })

    # write the new catalog file so future runs know these are used
    catalog_path = os.path.join(base, f"catalog_batch{batch_num}.py")
    with open(catalog_path, "w") as f:
        f.write(f'"""\nBatch {batch_num}: auto-generated by run_cycle.py.\n"""\n\nCOMBOS = [\n')
        for combo in final_combos:
            f.write(f"    {combo!r},\n")
        f.write("]\n")
    print(f"Wrote {catalog_path}")

    csv_path = os.path.join(base, f"pinterest_batch{batch_num}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "Media URL", "Pinterest board", "Description", "Link"])
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"Wrote {csv_path}")

    print(f"\nCYCLE COMPLETE: {len(final_combos)} new products published (batch {batch_num}).")
    print(f"Pinterest CSV ready at {csv_path} - needs human upload via Pinterest's Bulk Create Pins tool.")


if __name__ == "__main__":
    main()
