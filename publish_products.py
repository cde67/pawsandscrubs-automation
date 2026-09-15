"""
Automates: upload design -> create product -> publish, on Printify,
for the PawsAndScrubs pet x nurse niche store.
"""
import base64
import json
import os
import sys
import time
import urllib.request

API_BASE = "https://api.printify.com/v1"
SHOP_ID = 28931744  # PawsAndScrubs
BLUEPRINT_ID = 12   # Bella+Canvas 3001 Unisex Jersey Tee
PRINT_PROVIDER_ID = 99  # Printify Choice

VARIANTS_BY_COLOR = {
    "Black": [18100, 18101, 18102, 18103, 18104],
    "Navy": [18396, 18397, 18398, 18399, 18400],
    "White": [18540, 18541, 18542, 18543, 18544],
    "Ash": [38602, 38605, 38608, 38611, 38614],
    "Sand Dune": [80593, 80594, 80595, 80596, 80597],
}

TONE_COLORS = {
    "black_shirt": ["Black", "Navy"],
    "white_shirt": ["White", "Ash", "Sand Dune"],
}

PRICE_CENTS = 2499


def load_token():
    env_token = os.environ.get("PRINTIFY_API_TOKEN")
    if env_token:
        return env_token
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path) as f:
        for line in f:
            if line.startswith("PRINTIFY_API_TOKEN="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("token not found")


TOKEN = load_token()


def api_request(method, path, payload=None):
    url = f"{API_BASE}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "PawsAndScrubsAutomation/1.0")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def upload_image(file_path, file_name):
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    result = api_request("POST", "/uploads/images.json", {
        "file_name": file_name,
        "contents": b64,
    })
    return result["id"]


def build_variants_and_print_areas(image_id, tone):
    colors = TONE_COLORS[tone]
    variant_ids = []
    for c in colors:
        variant_ids.extend(VARIANTS_BY_COLOR[c])

    variants = [{"id": vid, "price": PRICE_CENTS, "is_enabled": True} for vid in variant_ids]
    print_areas = [{
        "variant_ids": variant_ids,
        "placeholders": [{
            "position": "front",
            "images": [{
                "id": image_id,
                "x": 0.5, "y": 0.5,
                "scale": 0.85,
                "angle": 0,
            }],
        }],
    }]
    return variants, print_areas


def create_and_publish(title, description, tags, image_id, tone):
    variants, print_areas = build_variants_and_print_areas(image_id, tone)
    product = api_request("POST", f"/shops/{SHOP_ID}/products.json", {
        "title": title,
        "description": description,
        "blueprint_id": BLUEPRINT_ID,
        "print_provider_id": PRINT_PROVIDER_ID,
        "variants": variants,
        "print_areas": print_areas,
        "tags": tags,
    })
    product_id = product["id"]

    api_request("POST", f"/shops/{SHOP_ID}/products/{product_id}/publish.json", {
        "title": True,
        "description": True,
        "images": True,
        "variants": True,
        "tags": True,
    })
    return product_id


DESIGNS = [
    {
        "file": "designs/design_01_golden_retriever_nurse.png",
        "tone": "black_shirt",
        "title": "Golden Retriever Mom Nurse Shirt - Dog Mom Nursing Gift Tee",
        "description": "A soft, comfy unisex tee for Golden Retriever moms who are also nurses. "
                        "The perfect gift for a nurse who loves her golden retriever - nurse appreciation, "
                        "dog mom pride, and nurse life all in one shirt.",
        "tags": ["golden retriever mom", "nurse gift", "dog mom shirt", "nurse life shirt", "dog nurse tee"],
    },
    {
        "file": "designs/design_02_german_shepherd_icu.png",
        "tone": "black_shirt",
        "title": "German Shepherd Dad ICU Nurse Shirt - Dog Dad Nursing Gift Tee",
        "description": "Show your German Shepherd dad pride and ICU nurse life on one comfy unisex tee. "
                        "A great gift for a critical care nurse who is also a proud dog dad.",
        "tags": ["german shepherd dad", "icu nurse gift", "dog dad shirt", "nurse life shirt", "critical care nurse"],
    },
    {
        "file": "designs/design_03_frenchie_er_nurse.png",
        "tone": "white_shirt",
        "title": "French Bulldog Mom ER Nurse Shirt - Frenchie Mom Nursing Gift Tee",
        "description": "For French Bulldog moms working the ER. A soft unisex tee that's the perfect "
                        "gift for an emergency room nurse who is also a devoted frenchie mom.",
        "tags": ["french bulldog mom", "er nurse gift", "frenchie mom shirt", "emergency nurse tee", "dog mom gift"],
    },
    {
        "file": "designs/design_04_labrador_school_nurse.png",
        "tone": "white_shirt",
        "title": "Labrador Mom School Nurse Shirt - Dog Mom Nursing Gift Tee",
        "description": "A comfy unisex tee for Labrador moms who work as school nurses. The perfect "
                        "school nurse appreciation gift for a proud lab mom.",
        "tags": ["labrador mom", "school nurse gift", "dog mom shirt", "nurse appreciation tee", "lab mom gift"],
    },
    {
        "file": "designs/design_05_corgi_nurse.png",
        "tone": "black_shirt",
        "title": "Corgi Mom Nurse Shirt - Dog Mom Nursing Gift Tee",
        "description": "A soft unisex tee celebrating Corgi moms who are also nurses. A great nurse "
                        "life gift for any proud corgi mom.",
        "tags": ["corgi mom", "nurse gift", "dog mom shirt", "nurse life shirt", "corgi nurse tee"],
    },
]


def main():
    base_dir = os.path.dirname(__file__)
    results = []
    for d in DESIGNS:
        path = os.path.join(base_dir, d["file"])
        print(f"Uploading {d['file']}...")
        image_id = upload_image(path, os.path.basename(d["file"]))
        print(f"  uploaded, image_id={image_id}")
        time.sleep(1)
        print("  creating + publishing product...")
        product_id = create_and_publish(
            d["title"], d["description"], d["tags"], image_id, d["tone"]
        )
        print(f"  done, product_id={product_id}")
        results.append({"title": d["title"], "product_id": product_id, "image_id": image_id})
        time.sleep(1)

    print("\nSummary:")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
