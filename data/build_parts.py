# Builds from data/transcription_A.txt:
#   data/parts.csv                    verified parts only (published, loaded by the app)
#   data/internal/parts_all.csv       every part, including the ones still to validate (local only, not committed)
#   data/internal/extraction_report.md  totals and the rows to check (local only, not committed)
# Parts validated by hand against the paper manual are listed in data/manual_validations.txt.
# The transcription is read #1; an independent read #2 found no differences,
# and the manual's repeated left/right pages serve as a cross-check.
import csv, os, re, collections
from translations_es import TR

HERE = os.path.dirname(os.path.abspath(__file__))
INTERNAL = os.path.join(HERE, "internal")
os.makedirs(INTERNAL, exist_ok=True)

# Article numbers validated by hand against the paper manual. One per line: "NNN.NNN  optional note"; "#" starts a comment.
MANUAL = {}
_mv = os.path.join(HERE, "manual_validations.txt")
if os.path.exists(_mv):
    for _line in open(_mv, encoding="utf-8"):
        _line = _line.split("#", 1)[0].strip()
        if _line:
            _a, _, _note = _line.partition(" ")
            MANUAL[_a] = "Validated against the paper manual" + (f" ({_note.strip()})" if _note.strip() else "")
COLS = ["sku", "sku_8digit", "page", "name_en", "name_es", "module", "subassembly", "price_cad",
        "source_image", "diagram_position", "confidence", "notes", "qty_per_machine", "on_hand", "validation", "evidence"]
# Quantity per machine, only where the manual states it for the whole machine: the main table on page 3 of the
# catalogue ("1 Mastrena II - 230V"). Other quantities in the manual are per subassembly, so they stay blank.
PER_MACHINE = {"110.533": "1", "116.093": "1", "127.028": "1", "127.734": "1", "127.950": "1", "128.036": "1",
               "128.037": "1", "128.047": "1", "128.051": "1", "128.065": "1", "128.386": "1", "128.653": "1",
               "129.562": "1", "130.702": "2", "130.704": "1", "131.365": "1", "133.029": "1", "133.661": "1",
               "133.690": "1"}
# Columns people see in the published catalog and in the CSV they export (the manual page is there so anyone can check a part
# against the paper manual). The rest (source image, diagram position,
# confidence, validation status, evidence) is for development only and stays in data/internal/parts_all.csv.
PUBLIC_COLS = ["sku", "sku_8digit", "page", "name_en", "name_es", "module", "subassembly", "price_cad",
               "qty_per_machine", "on_hand", "notes"]
ART = re.compile(r"^\d{3}\.\d{3}$")
SKU8 = re.compile(r"^11\d{6}$")
# Page 3 lists the main assemblies: module depends on what each assembly is.
TOP_MODULE = {"127.028": "Mechanical", "127.734": "Hydraulic", "127.950": "Steam", "128.036": "Chassis"}
TOP_SECTION = "1 Mastrena II - 230V (main assemblies)"
# Blurry photos: an article that only appears here gets medium confidence.
BLURRY = {7, 132}
SIC = {"127.996": "fermal", "129.095": "whitout", "128.065": "coatad", "128.009": "Vesses",
       "115.827": "Exernal", "104.024": "M04x10"}
DOUBT_DESC = {"130.922": "length '90mm' not sharp in the photo",
              "130.925": "size 'ø8/6 x 310mm' not sharp in the photo",
              "129.354": "'tool' not sharp in the photo"}

def tr_es(art, en):
    if art in TR: return TR[art]
    m = re.match(r"FEP pipe (.*)", en)
    if m: return "Tubo FEP " + m.group(1)
    m = re.match(r"O-Ring (.*)", en)
    if m: return "O-ring " + m.group(1)
    m = re.match(r"Wiring harness (.*)", en)
    if m: return "Arnés de cables " + m.group(1)
    raise KeyError(f"Missing Spanish translation for {art} {en}")

# ---- read transcription ----
pages, occ, cur = [], collections.OrderedDict(), None
for line in open(os.path.join(HERE, "transcription_A.txt"), encoding="utf-8"):
    line = line.rstrip("\n")
    if line.startswith("## "):
        n, img, sec, mod = line[3:].split("|")
        cur = dict(n=int(n), img=img, sec=sec, mod=mod, row=0); pages.append(cur); continue
    if not line or line.startswith("#"): continue
    art, sku, desc = line.split("|", 2)
    cur["row"] += 1
    occ.setdefault(art, []).append(dict(page=cur, row=cur["row"], sku=sku, desc=desc))

# Diagram image: the next photo that is not a table.
_libros_dirs = [r"C:/Users/faleu/Mi unidad/Maestrena Tutorial/Libros", os.path.join(HERE, "internal", "Maestrena Tutorial", "Libros")]
libros = sorted(os.listdir(next(d for d in _libros_dirs if os.path.isdir(d))))
table_n = {p["n"] for p in pages}
def diagram_for(n):
    k = n + 1
    while k in table_n: k += 1
    return libros[k - 1] if k - 1 < len(libros) else ""

sku_owner = collections.defaultdict(set)
for a, lst in occ.items():
    for o in lst:
        if o["sku"]: sku_owner[o["sku"]].add(a)

# Chapter titles (normalized) -> chapter number, used to confirm assembly names against their own chapter page.
def norm_title(s):
    return re.sub(r"\s+", " ", s.lower().replace(" mastrena ii", "").replace("mastrena ii ", "")).strip(" .")
CHAPTER = {norm_title(re.sub(r"^[\d.]+\s*", "", p["sec"])): p["sec"].split(" ")[0] for p in pages}

# Printed page of each chapter's parts table. Every chapter of this manual takes two pages: the parts table on an even
# page and its diagram on the next odd page, starting with the table on page 4. Checked against the page numbers
# printed in the photos (31 of the 67 chapters, spread over the whole book): none disagreed.
_chapters = []
for _p in pages:
    if _p["sec"] not in _chapters: _chapters.append(_p["sec"])
PAGE_OF = {s: 4 + 2 * i for i, s in enumerate(_chapters)}

rows = []
for art, lst in occ.items():
    first = lst[0]; p = first["page"]
    skus = sorted({o["sku"] for o in lst})
    descs = sorted({o["desc"] for o in lst}, key=len, reverse=True)
    en = descs[0]
    sku8 = skus[-1] if skus else ""
    conf, notes = "high", []
    mod = TOP_MODULE.get(art, "Other") if p["mod"] == "*" else p["mod"]
    sec = TOP_SECTION if p["mod"] == "*" else p["sec"]

    if not ART.match(art):
        conf = "low"; notes.append("Article no. does not match NNN.NNN")
    if len(skus) > 1:
        conf = "low"; notes.append("Different SKU across pages: " + " / ".join(skus))
    if len({d.rstrip('.') for d in descs}) > 1:
        notes.append("Name variants: " + " / ".join(descs))
    if sku8 and not SKU8.match(sku8):
        conf = "medium" if conf == "high" else conf
        notes.append(f"8-digit SKU '{sku8}' has {len(sku8)} digits (does not match 11xxxxxx)")
    others = sorted(sku_owner[sku8] - {art}) if sku8 else []
    if others:
        conf = "medium" if conf == "high" else conf
        notes.append(f"Same 8-digit SKU as {', '.join(others)}")
    if {o["page"]["n"] for o in lst} <= BLURRY:
        conf = "medium" if conf == "high" else conf
        notes.append("Only appears in a blurry photo")
    if art in DOUBT_DESC:
        conf = "medium" if conf == "high" else conf
        notes.append("Uncertain name: " + DOUBT_DESC[art])
    if art in SIC:
        notes.append(f"'{SIC[art]}' as printed in the manual")
    secs = []
    for o in lst[1:]:
        s = o["page"]["sec"]
        if s != p["sec"] and s not in secs: secs.append(s)
    if secs:
        names = [s.split(" ")[0] for s in secs]
        more = f" +{len(names) - 4} more" if len(names) > 4 else ""
        notes.append("Also in: " + ", ".join(names[:4]) + more)

    # Validation: a part goes straight into the catalog only when a second, independent source agrees with the first read.
    #  a) the same article, SKU and name read identically on 2+ clear pages, or
    #  b) its name equals the title of its own chapter (read once, but the name is confirmed elsewhere).
    # Both need an article no. NNN.NNN, an 8-digit SKU 11xxxxxx used by no other article, and no typo flagged in the manual.
    pages_seen = {o["page"]["n"] for o in lst}
    clear = pages_seen - BLURRY
    same = len(skus) == 1 and len({o["desc"].rstrip(".") for o in lst}) == 1
    strict = bool(ART.match(art) and SKU8.match(sku8 or "") and len(sku_owner[sku8]) == 1 and art not in SIC)
    verified, ev = False, f"Read on {len(clear)} clear page{'' if len(clear) == 1 else 's'}"
    if not clear:
        ev = "Only in a blurry photo"
    elif not same:
        ev = "Readings differ between pages"
    elif strict and len(clear) >= 2:
        verified, ev = True, f"Same values read on {len(clear)} independent clear pages"
    elif strict and norm_title(en) in CHAPTER:
        verified, ev = True, f"Name matches chapter title {CHAPTER[norm_title(en)]}; SKU read once"
    if art in MANUAL:
        verified, ev, conf = True, MANUAL[art], "high"
    rows.append(dict(sku=art, sku_8digit=sku8, page=PAGE_OF[p["sec"]], name_en=en, name_es=tr_es(art, en), module=mod,
                     subassembly=sec, price_cad="", source_image=p["img"],
                     diagram_position=f"table row {first['row']}; diagram {diagram_for(p['n'])}",
                     confidence=conf, notes="; ".join(notes),
                     qty_per_machine=PER_MACHINE.get(art, ""), on_hand="",
                     validation="verified" if verified else "pending", evidence=ev))

def write_csv(path, subset, cols):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(subset)
write_csv(os.path.join(HERE, "parts.csv"), [r for r in rows if r["validation"] == "verified"], PUBLIC_COLS)
write_csv(os.path.join(INTERNAL, "parts_all.csv"), rows, COLS)

# ---- report ----
by_mod = collections.Counter(r["module"] for r in rows)
by_conf = collections.Counter(r["confidence"] for r in rows)
rev = [r for r in rows if r["confidence"] in ("medium", "low")]
L = ["# Extraction report: Mastrena II 230V catalog", "",
     f"Source: Thermoplan *Spare parts catalogue Mastrena II - 230V* (07.08.2023_EN), {len(pages)} pages with a parts table.", "",
     f"Unique parts: **{len(rows)}** (from {sum(len(v) for v in occ.values())} rows read; repeated rows were merged into one).", "",
     f"Verified (shown in the catalog): **{sum(r['validation'] == 'verified' for r in rows)}**. To validate: **{sum(r['validation'] == 'pending' for r in rows)}**.", "",
     "## By module", ""] + [f"- {m}: {by_mod.get(m, 0)}" for m in ["Mechanical", "Steam", "Hydraulic", "Chassis", "Other"]] + [
     "", "## By confidence", ""] + [f"- {c}: {by_conf.get(c, 0)}" for c in ["high", "medium", "low", "illegible"]] + [
     "", f"## Rows to check against the paper manual ({len(rev)})", "",
     "| SKU (Article no.) | 8-digit SKU | Name | Image | Confidence | Reason |", "|---|---|---|---|---|---|"]
for r in rev:
    reason = "; ".join(x for x in r["notes"].split("; ") if not x.startswith("Also in"))
    L.append(f"| {r['sku']} | {r['sku_8digit']} | {r['name_en']} | {r['source_image']} | {r['confidence']} | {reason} |")
open(os.path.join(INTERNAL, "extraction_report.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(rows), dict(by_mod), dict(by_conf), "verified:", sum(r["validation"] == "verified" for r in rows))
