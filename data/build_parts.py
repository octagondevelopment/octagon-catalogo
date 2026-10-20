# Builds data/parts.csv and data/extraction_report.md from data/transcription_A.txt.
# The transcription is read #1; an independent read #2 found no differences,
# and the manual's repeated left/right pages serve as a cross-check.
import csv, os, re, collections
from translations_es import TR

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ["sku", "sku_8dig", "nombre_en", "nombre_es", "modulo", "subconjunto", "precio_cad",
        "imagen_origen", "posicion_en_diagrama", "confianza", "notas"]
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
libros = sorted(os.listdir(r"C:/Users/faleu/Mi unidad/Maestrena Tutorial/Libros"))
table_n = {p["n"] for p in pages}
def diagram_for(n):
    k = n + 1
    while k in table_n: k += 1
    return libros[k - 1] if k - 1 < len(libros) else ""

sku_owner = collections.defaultdict(set)
for a, lst in occ.items():
    for o in lst:
        if o["sku"]: sku_owner[o["sku"]].add(a)

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

    rows.append(dict(sku=art, sku_8dig=sku8, nombre_en=en, nombre_es=tr_es(art, en), modulo=mod,
                     subconjunto=sec, precio_cad="", imagen_origen=p["img"],
                     posicion_en_diagrama=f"table row {first['row']}; diagram {diagram_for(p['n'])}",
                     confianza=conf, notas="; ".join(notes)))

with open(os.path.join(HERE, "parts.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)

# ---- report ----
by_mod = collections.Counter(r["modulo"] for r in rows)
by_conf = collections.Counter(r["confianza"] for r in rows)
rev = [r for r in rows if r["confianza"] in ("medium", "low")]
L = ["# Extraction report: Mastrena II 230V catalog", "",
     f"Source: Thermoplan *Spare parts catalogue Mastrena II - 230V* (07.08.2023_EN), {len(pages)} pages with a parts table.", "",
     f"Unique parts: **{len(rows)}** (from {sum(len(v) for v in occ.values())} rows read; repeated rows were merged into one).", "",
     "## By module", ""] + [f"- {m}: {by_mod.get(m, 0)}" for m in ["Mechanical", "Steam", "Hydraulic", "Chassis", "Other"]] + [
     "", "## By confidence", ""] + [f"- {c}: {by_conf.get(c, 0)}" for c in ["high", "medium", "low", "illegible"]] + [
     "", f"## Rows to check against the paper manual ({len(rev)})", "",
     "| SKU (Article no.) | 8-digit SKU | Name | Image | Confidence | Reason |", "|---|---|---|---|---|---|"]
for r in rev:
    reason = "; ".join(x for x in r["notas"].split("; ") if not x.startswith("Also in"))
    L.append(f"| {r['sku']} | {r['sku_8dig']} | {r['nombre_en']} | {r['imagen_origen']} | {r['confianza']} | {reason} |")
open(os.path.join(HERE, "extraction_report.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(rows), dict(by_mod), dict(by_conf))
