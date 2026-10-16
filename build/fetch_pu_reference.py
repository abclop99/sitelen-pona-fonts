#!/usr/bin/env python3
"""Download jan Sonja's pu drawings for the glyph files' reference layer.

fonts/<font>/glyphs.svg links to reference/pu/downloads/<word>.svg
(git-ignored) instead of copying the drawings into the repo. This fetches them from Wikimedia
Commons, where each is "<Word> - sitelen pona in Sonja Lang's handwriting.svg".

    python3 build/fetch_pu_reference.py

Or extract them from a saved copy (.mhtml) of the sona pona wiki page
"Comparison of Madame Lang's handwriting and linja pona". The browser only
saves images it has loaded, so scroll to the bottom of the page first.

    python3 build/fetch_pu_reference.py --from-mhtml page.mhtml
"""

import argparse
import email
import json
import urllib.parse
import urllib.request

from common import ROOT, read_words

OUT = ROOT / "reference" / "pu" / "downloads"
API = "https://commons.wikimedia.org/w/api.php"
SUFFIX = " - sitelen pona in Sonja Lang's handwriting.svg"
HEADERS = {"User-Agent": "sitelen-pona-fonts reference fetcher "
                         "(https://github.com/abclop99/sitelen-pona-fonts)"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS)) as r:
        return r.read()


def from_commons(words):
    titles = {f"File:{w[0].upper()}{w[1:]}{SUFFIX}": w for w in words}
    found = {}
    names = list(titles)
    for i in range(0, len(names), 50):
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "prop": "imageinfo",
            "iiprop": "url", "titles": "|".join(names[i:i + 50]),
        })
        data = json.loads(get(f"{API}?{query}"))
        normal = {n["to"]: n["from"] for n in data["query"].get("normalized", [])}
        for page in data["query"]["pages"].values():
            if "imageinfo" not in page:
                continue
            title = normal.get(page["title"], page["title"])
            found[titles[title]] = page["imageinfo"][0]["url"]
    for word, url in sorted(found.items()):
        (OUT / f"{word}.svg").write_bytes(get(url))
    return set(found)


def from_mhtml(path, words):
    msg = email.message_from_bytes(path.read_bytes())
    found = set()
    for part in msg.walk():
        loc = urllib.parse.unquote(part.get("Content-Location", "").split("?")[0])
        name = loc.rsplit("/", 1)[-1].replace("_", " ")
        if not name.endswith(SUFFIX):
            continue
        word = name[: -len(SUFFIX)].lower()
        if word in words:
            (OUT / f"{word}.svg").write_bytes(part.get_payload(decode=True))
            found.add(word)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-mhtml", help="extract from a saved wiki page instead")
    args = ap.parse_args()

    words = [w["word"] for w in read_words() if w["set"] == "pu"]
    OUT.mkdir(parents=True, exist_ok=True)
    if args.from_mhtml:
        from pathlib import Path
        found = from_mhtml(Path(args.from_mhtml), set(words))
    else:
        found = from_commons(words)
    have = {p.stem for p in OUT.glob("*.svg")}
    missing = [w for w in words if w not in have]
    print(f"{len(found)} drawings saved to {OUT.relative_to(ROOT)}; "
          f"{len(words) - len(missing)} of {len(words)} pu words present")
    if missing:
        print("still missing:", " ".join(missing))


if __name__ == "__main__":
    main()
