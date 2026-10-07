#!/usr/bin/env python3
"""Generate the two Manchester STOP 4 replacement photos (breeder's answers, 2026-10-07:
q02 travel heading and q03 guarantee heading, "regenerate a similar type photo but for the
page", "use Gemini the new 2.1 model"). One image at a time, every call logged by
scripts/gemini_log.py. Reads GEMINI_API_KEY from the environment only; never prints it.

    python3 scripts/gen_manchester_stop4.py travel-h2
    python3 scripts/gen_manchester_stop4.py guarantee-h2

Each master is saved as PNG beside the breeder's own photos (bsuk-image-generation step 3),
then drafted with scripts/ingest_image.py for the board's sha12 approval. Nothing is
published from here.
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import env_loader  # noqa: E402
from gemini_log import log_call  # noqa: E402

env_loader.load_env()

MODEL = "gemini-nano-banana-2.1"  # the breeder's pick at STOP 4 (2026-10-07); $0.0336 per 1K image
SLUG = "blue-staffy-puppies-manchester-uk"
OUT = ROOT / "bluestaffyuk-cms/Assets/Images/generated"

# IMAGE-DESIGNS.md §2, verbatim.
WRAPPER = ("Editorial pet photography, soft natural daylight with a gentle warm cast, shallow depth of "
           "field, a true-to-breed blue Staffordshire Bull Terrier: medium-sized and muscular, broad "
           "and deep head with pronounced cheek muscles, short, smooth, close-lying grey/blue coat, "
           "natural rose or half-pricked ears, calm friendly expression, relaxed family home in the north of England, "
           "steel-blue and bone palette with one small brass accent, photorealistic, crisp detail on "
           "the eyes and coat.")
# IMAGE-DESIGNS.md §3, verbatim.
NEGATIVE = ("no text, no watermarks, no logos, no captions, no UI chrome, no cropped ears, no fighting or "
            "aggression imagery, no bared teeth or snarling, no dog pulling toward another dog, no "
            "spiked collar, no chain collar, no XL Bully build, no pit-bull-type build, no oversized "
            "head or exaggerated bulk, no tall leggy frame, nothing that could imply a banned type, no "
            "other breed, no generic dog, no merle or bright-blue coat, no cartoon, 3D or illustration "
            "style for a photo slot, no cold blue cast, no clinical or studio lighting, no kennel rows "
            "or cages, no distorted anatomy, no extra legs or merged paws, no sharp identifiable human "
            "faces unless it is a real buyer photo, no cluttered background.")

SLOTS = {
    # H2 "How Will Your Blue Staffy Puppy Travel to Greater Manchester?" — like the van photo the
    # breeder picked, without the lettering or logo; §4 "Travel and collection" light and lens.
    "travel-h2": ("Scene: travel and collection, clean interior daylight, 35mm f/4. "
                  "Subject: three blue Staffordshire Bull Terrier puppies sitting calmly together in the "
                  "open side door of a plain, completely unbranded white van, on a soft bone-coloured "
                  "blanket beside an open travel crate, ready for a gentle journey to their new home; "
                  "the van body is plain white with no writing, stickers or graphics of any kind."),
    # H2 "Which Health Problems Can Staffy Dogs Develop, and What Will We Stand Behind?" — like the
    # wellbeing photo the breeder picked, without its printed banner; §4 health light and lens.
    "guarantee-h2": ("Scene: health check, diffused warm daylight from a window, no flash, 85mm f/2.8. "
                     "Subject: a healthy adult blue Staffordshire Bull Terrier sitting calmly on a vet's "
                     "examination table beside a stethoscope, wearing a plain soft harness, looking "
                     "content; a vet's hand rests gently on its shoulder, the vet's face out of frame; "
                     "plain warm bone-coloured walls with nothing written on them."),
}


def prompt(slot):
    return f"{WRAPPER} {SLOTS[slot]} Avoid: {NEGATIVE}"


def main(argv):
    if len(argv) != 1 or argv[0] not in SLOTS:
        print("usage: gen_manchester_stop4.py " + "|".join(SLOTS))
        return 2
    if not os.environ.get("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set in the environment")
        return 2
    from google import genai
    from google.genai import types
    slot = argv[0]
    client = genai.Client()  # keep the client in a variable (bsuk-image-generation)
    try:
        resp = client.models.generate_content(
            model=MODEL, contents=prompt(slot),
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="16:9")))
        log_call(MODEL, f"{SLUG}/{slot}", 200, note="Manchester STOP 4 replacement (q02/q03)")
    except Exception as e:
        log_call(MODEL, f"{SLUG}/{slot}",
                 getattr(e, "code", None) or getattr(e, "status_code", None) or "error",
                 note=str(e)[:200])
        raise
    data = None
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            data = part.inline_data.data
            break
    if data is None:
        print("no image returned")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{SLUG}-{slot}.png"
    from io import BytesIO
    from PIL import Image
    Image.open(BytesIO(data)).save(out, "PNG")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
