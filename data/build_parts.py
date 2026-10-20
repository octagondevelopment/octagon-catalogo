# Genera data/parts.csv y data/reporte_extraccion.md desde data/transcripcion_A.txt.
# La transcripción es la lectura 1; la lectura 2 (independiente) no encontró diferencias,
# y las páginas izquierda/derecha repetidas del manual sirven como verificación cruzada.
import csv, os, re, collections
from traducciones import TR

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ["sku", "sku_8dig", "nombre_en", "nombre_es", "modulo", "subconjunto", "precio_cad",
        "imagen_origen", "posicion_en_diagrama", "confianza", "notas"]
ART = re.compile(r"^\d{3}\.\d{3}$")
SKU8 = re.compile(r"^11\d{6}$")
# Página 3 lista los conjuntos principales: módulo según qué es cada conjunto.
TOP_MODULE = {"127.028": "Mechanical", "127.734": "Hydraulic", "127.950": "Steam", "128.036": "Chassis"}
# Fotos borrosas: un artículo que solo aparece aquí queda en confianza media.
BLURRY = {7, 132}
SIC = {"127.996": "fermal", "129.095": "whitout", "128.065": "coatad", "128.009": "Vesses",
       "115.827": "Exernal", "104.024": "M04x10"}
DOUBT_DESC = {"130.922": "largo '90mm' poco nítido en la foto",
              "130.925": "medidas 'ø8/6 x 310mm' poco nítidas en la foto",
              "129.354": "'tool' poco nítido en la foto"}

def tr_es(art, en):
    if art in TR: return TR[art]
    m = re.match(r"FEP pipe (.*)", en)
    if m: return "Tubo FEP " + m.group(1)
    m = re.match(r"O-Ring (.*)", en)
    if m: return "O-ring " + m.group(1)
    m = re.match(r"Wiring harness (.*)", en)
    if m: return "Arnés de cables " + m.group(1)
    raise KeyError(f"Falta traducción para {art} {en}")

# ---- leer transcripción ----
pages, occ, cur = [], collections.OrderedDict(), None
for line in open(os.path.join(HERE, "transcripcion_A.txt"), encoding="utf-8"):
    line = line.rstrip("\n")
    if line.startswith("## "):
        n, img, sec, mod = line[3:].split("|")
        cur = dict(n=int(n), img=img, sec=sec, mod=mod, fila=0); pages.append(cur); continue
    if not line or line.startswith("#"): continue
    art, sku, desc = line.split("|", 2)
    cur["fila"] += 1
    occ.setdefault(art, []).append(dict(page=cur, fila=cur["fila"], sku=sku, desc=desc))

# Imagen del diagrama: la siguiente foto que no es una tabla.
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
    conf, notas = "alta", ["nombre_es = traducción"]
    mod = TOP_MODULE.get(art, "Other") if p["mod"] == "*" else p["mod"]

    if not ART.match(art):
        conf = "baja"; notas.append("Article no. no calza con NNN.NNN")
    if len(skus) > 1:
        conf = "baja"; notas.append("SKU distinto entre páginas: " + " / ".join(skus))
    if len({d.rstrip('.') for d in descs}) > 1:
        notas.append("Nombre con variantes: " + " / ".join(descs))
    if sku8 and not SKU8.match(sku8):
        conf = "media" if conf == "alta" else conf
        notas.append(f"SKU 8 díg. '{sku8}' tiene {len(sku8)} dígitos (no calza con 11xxxxxx)")
    others = sorted(sku_owner[sku8] - {art}) if sku8 else []
    if others:
        conf = "media" if conf == "alta" else conf
        notas.append(f"Mismo SKU 8 díg. que {', '.join(others)}")
    if {o["page"]["n"] for o in lst} <= BLURRY:
        conf = "media" if conf == "alta" else conf
        notas.append("Solo aparece en una foto borrosa")
    if art in DOUBT_DESC:
        conf = "media" if conf == "alta" else conf
        notas.append("Nombre dudoso: " + DOUBT_DESC[art])
    if art in SIC:
        notas.append(f"'{SIC[art]}' tal cual en el manual")
    if p["mod"] != "*" and mod == "Other":
        notas.append("Sección manual: " + p["sec"])
    secs = []
    for o in lst[1:]:
        s = o["page"]["sec"]
        if s != p["sec"] and s not in secs: secs.append(s)
    if secs:
        notas.append("También en: " + ", ".join(s.split(" ")[0] for s in secs))

    rows.append(dict(sku=art, sku_8dig=sku8, nombre_en=en, nombre_es=tr_es(art, en), modulo=mod,
                     subconjunto=p["sec"], precio_cad="", imagen_origen=p["img"],
                     posicion_en_diagrama=f"tabla fila {first['fila']}; diagrama {diagram_for(p['n'])}",
                     confianza=conf, notas="; ".join(notas)))

with open(os.path.join(HERE, "parts.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)

# ---- reporte ----
by_mod = collections.Counter(r["modulo"] for r in rows)
by_conf = collections.Counter(r["confianza"] for r in rows)
rev = [r for r in rows if r["confianza"] in ("media", "baja")]
L = ["# Reporte de extracción: catálogo Mastrena II 230V", "",
     f"Fuente: Thermoplan *Spare parts catalogue Mastrena II - 230V* (07.08.2023_EN), {len(pages)} páginas con tabla.", "",
     f"Total de piezas únicas: **{len(rows)}** (de {sum(len(v) for v in occ.values())} filas leídas; las repetidas se juntaron en una fila).", "",
     "## Por módulo", ""] + [f"- {m}: {by_mod.get(m, 0)}" for m in ["Mechanical", "Steam", "Hydraulic", "Chassis", "Other"]] + [
     "", "## Por confianza", ""] + [f"- {c}: {by_conf.get(c, 0)}" for c in ["alta", "media", "baja", "ilegible"]] + [
     "", f"## Filas para revisar contra el papel ({len(rev)})", "",
     "| SKU (Article no.) | SKU 8 díg. | Nombre | Imagen | Confianza | Motivo |", "|---|---|---|---|---|---|"]
for r in rev:
    motivo = "; ".join(x for x in r["notas"].split("; ") if not x.startswith(("nombre_es", "Sección", "También")))
    L.append(f"| {r['sku']} | {r['sku_8dig']} | {r['nombre_en']} | {r['imagen_origen']} | {r['confianza']} | {motivo} |")
open(os.path.join(HERE, "reporte_extraccion.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(rows), dict(by_mod), dict(by_conf))
