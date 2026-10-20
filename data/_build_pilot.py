# Builds data/pilot_parts.csv from the double manual read of 3 images (pilot).
import csv, re, os
COLS = ["sku","sku_8dig","nombre_en","nombre_es","modulo","subconjunto","precio_cad",
        "imagen_origen","posicion_en_diagrama","confianza","notas"]
I3, I5, I9 = "IMG_20260923_194949.jpg", "IMG_20260923_195002.jpg", "IMG_20260923_195112.jpg"
D3, D5, D9 = "IMG_20260923_194955.jpg", "IMG_20260923_195005.jpg", "IMG_20260923_195116.jpg"
# (article, sku8, en, es, modulo)
t3 = [
("110.533","11133893","Water pump Mastrena CE assy","Bomba de agua Mastrena CE (conjunto)","Other"),
("116.093","","Water pump power cord CE","Cable de alimentación bomba de agua CE","Other"),
("127.028","","Mechanic module Mastrena II","Módulo mecánico Mastrena II","Mechanical"),
("127.734","11086418","Hydraulic module Mastrena II assy.","Módulo hidráulico Mastrena II (conjunto)","Hydraulic"),
("127.950","11086417","Steam module 230V-400V Mastrena II","Módulo de vapor 230V-400V Mastrena II","Steam"),
("128.036","11086548","Chassis assy. Mastrena II","Chasis Mastrena II (conjunto)","Chassis"),
("128.037","11086472","Hood assy. Mastrena II","Capota Mastrena II (conjunto)","Other"),
("128.047","11086446","Coffee outlet assy. Mastrena II","Salida de café Mastrena II (conjunto)","Other"),
("128.051","11086396","Drip tray assy. Mastrena II","Bandeja de goteo Mastrena II (conjunto)","Other"),
("128.065","","Reinf. water hose, coatad 3/8\"-3/8\"x2m","Manguera de agua reforzada, recubierta 3/8\"-3/8\" x 2 m","Other"),
("128.386","11086421","Steam outlet assy. Mastrena II","Salida de vapor Mastrena II (conjunto)","Other"),
("128.653","11101497","Steam cover front","Cubierta frontal de vapor","Other"),
("129.562","11080979","Ground drawer assy. Mastrena II","Cajón de borra Mastrena II (conjunto)","Other"),
("130.702","11080977","Bean hopper small assy. Mastrena II","Tolva de grano pequeña Mastrena II (conjunto)","Other"),
("130.704","11080978","Bean hopper big assy. Mastrena II","Tolva de grano grande Mastrena II (conjunto)","Other"),
("131.365","","Electric box Mastrena II 230V","Caja eléctrica Mastrena II 230V","Other"),
("133.029","11086501","Steam casing assy. Mastrena II","Carcasa de vapor Mastrena II (conjunto)","Other"),
("133.661","11101545","Drain pipe 2.5m assy.","Tubo de desagüe 2,5 m (conjunto)","Other"),
("133.690","11101547","Hood backwall assy. Mastrena II","Pared trasera de capota Mastrena II (conjunto)","Other"),
]
t5 = [
("103.239","","Cable tie 140...150 x 3.2/3.4/3.5/3.6","Amarra plástica 140...150 x 3,2/3,4/3,5/3,6"),
("104.024","","Lens head screw M04x10 Phillips","Tornillo cabeza lenteja M04x10 Phillips"),
("104.049","193491","Oval head screw M4x6 Phillips","Tornillo cabeza oval M4x6 Phillips"),
("116.106","11097244","PT screw lens head KA40x10","Tornillo PT cabeza lenteja KA40x10"),
("116.106","11097244","PT screw lens head KA40x10","Tornillo PT cabeza lenteja KA40x10"),
("121.464","11097249","PT screw KA30x10 philips","Tornillo PT KA30x10 Phillips"),
("122.913","11101490","Cable tie with clip 100mm","Amarra plástica con clip 100 mm"),
("127.442","11101491","micro SD-Card","Tarjeta micro SD"),
("127.814","11101494","Button cell battery CR2032","Pila botón CR2032"),
("128.040","11080972","Main user interface Mastrena II assy.","Interfaz de usuario principal Mastrena II (conjunto)"),
("130.835","11080974","Grinder protection assy.","Protección del molino (conjunto)"),
("130.894","11086444","Steam tower cover back assy.","Tapa trasera torre de vapor (conjunto)"),
("130.895","11101532","Magnet mount assy.","Soporte de imán (conjunto)"),
("130.981","11101534","Wiring harness Mastrena II hood","Arnés de cables capota Mastrena II"),
("131.572","11086427","Knob Main UI","Perilla interfaz principal"),
("132.494","11101537","Main user interface M2 display assy.","Pantalla interfaz principal M2 (conjunto)"),
("133.019","11101542","Fan set","Set de ventilador"),
("133.664","11080823","Reed switch assy.","Interruptor reed (conjunto)"),
("135.200","","Oval head screw Phillips M4x12","Tornillo cabeza oval Phillips M4x12"),
("142.122","011145617","Hood holder cpl.","Soporte de capota completo"),
("142.611","11145616","Elastic clip washer ø05","Arandela clip elástica ø05"),
]
t9 = [
("104.029","","Oval head screw Phillips M3x8","Tornillo cabeza oval Phillips M3x8"),
("104.049","193491","Oval head screw M4x6 Phillips","Tornillo cabeza oval M4x6 Phillips"),
("104.049","193491","Oval head screw M4x6 Phillips","Tornillo cabeza oval M4x6 Phillips"),
("115.666","11086411","Sleeve ø10/15x3.6","Manguito ø10/15x3,6"),
("116.106","11097244","PT screw lens head KA40x10","Tornillo PT cabeza lenteja KA40x10"),
("116.106","11097244","PT screw lens head KA40x10","Tornillo PT cabeza lenteja KA40x10"),
("120.859","11086409","O-Ring 5.60x2.40 FKM 75.5/VA75F","O-ring 5,60x2,40 FKM 75.5/VA75F"),
("121.359","11086410","O-Ring 7.60x2.40 FKM 75.5/VA75F","O-ring 7,60x2,40 FKM 75.5/VA75F"),
("128.798","11101498","Shaft","Eje"),
("128.815","11080944","Plunger","Émbolo"),
("128.948","11101500","Compression spring 1x6.3x21.5","Resorte de compresión 1x6,3x21,5"),
("129.210","11080941","Steam connection","Conexión de vapor"),
("129.788","11080939","Deep groove ball bearing 61800 2RS NS7","Rodamiento rígido de bolas 61800 2RS NS7"),
("129.907","11080965","Steam wand","Lanceta de vapor"),
("130.042","11086637","Lever","Palanca"),
("130.278","11086639","Housing","Carcasa"),
("130.287","11086638","Steam cover","Cubierta de vapor"),
("130.288","11086636","Adapter","Adaptador"),
("130.290","11086453","Valve assy.","Válvula (conjunto)"),
("130.292","11086412","Spring Plunger","Émbolo con resorte"),
("130.293","11086511","Support plate","Placa de soporte"),
("130.310","11080945","Connector assy.","Conector (conjunto)"),
("130.312","11086413","Bearing ring","Anillo de rodamiento"),
("130.734","11080943","Photoelectric sensors","Sensores fotoeléctricos"),
("131.170","11080966","Springplate steam wand","Placa resorte lanceta de vapor"),
("131.209","11086510","Specific screw ø6x14.2-M5","Tornillo específico ø6x14,2-M5"),
("131.228","11080942","Temperature sensor steam wand","Sensor de temperatura lanceta de vapor"),
("133.454","11080940","Gasket PE TS03F 15.1x10x3.5 (4)","Empaquetadura PE TS03F 15,1x10x3,5 (4)"),
("134.638","11118812","O-Ring 9.50x1.50 EPDM FDA","O-ring 9,50x1,50 EPDM FDA"),
("139.898","11133906","Shaft assy.","Eje (conjunto)"),
]
ART = re.compile(r"^\d{3}\.\d{3}$"); SKU8 = re.compile(r"^11\d{6}$")
rows, seen = [], {}
def add(art, sku8, en, es, mod, sub, img, dimg, fila):
    pos = f"table row {fila}; diagram {dimg}"
    if art in seen:
        r = seen[art]
        r["notas"] += f" | Repeated in {img} ({sub}) row {fila}"
        return
    notas, conf = ["nombre_es = translation"], "high"
    if not ART.match(art): conf = "low"; notas.append("Article no. does not match NNN.NNN")
    if sku8 and not SKU8.match(sku8):
        conf = "medium"; notas.append(f"8-digit SKU '{sku8}' does not match 11xxxxxx; check on paper")
    if mod == "Other": notas.append(f"Manual section: {sub}")
    r = dict(sku=art, sku_8dig=sku8, nombre_en=en, nombre_es=es, modulo=mod, subconjunto=sub,
             precio_cad="", imagen_origen=img, posicion_en_diagrama=pos, confianza=conf, notas="; ".join(notas))
    seen[art] = r; rows.append(r)
for i,(a,s,en,es,m) in enumerate(t3,1): add(a,s,en,es,m,"1 Mastrena II - 230V (main assemblies)",I3,D3,i)
for i,(a,s,en,es) in enumerate(t5,1): add(a,s,en,es,"Other","1.1 Hood assy.",I5,D5,i)
for i,(a,s,en,es) in enumerate(t9,1): add(a,s,en,es,"Other","1.2.1 Steam outlet",I9,D9,i)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pilot_parts.csv")
with open(out,"w",newline="",encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
print(len(rows), "rows;", sum(r["confianza"]!="high" for r in rows), "not high")
for r in rows:
    if r["confianza"]!="high" or "Repeated" in r["notas"]: print(r["sku"], r["sku_8dig"], r["confianza"], "|", r["notas"])
