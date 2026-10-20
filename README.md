# Octagon · Mastrena Parts Catalog

Internal catalog of Mastrena II spare parts for Octagon Services (Vancouver, BC). The app is a single `index.html` file, with no build step and no server. Its data comes from `data/parts.csv`.

## What it does

- Shows only parts that have been verified (see below). The header counts them.
- Shows the catalog as a compact list: a sketch, the English and Spanish names, SKU and price. Tap a row to open its details; the actions (edit, label, remove) live there.
- Searches by name or SKU. Module tabs show counts, and you can also filter by subassembly (the manual's numbering, for example 1.10.2 Brew module), "No price".
- Sorts by manual order, SKU, name or price.
- Adds, edits (including price) and removes parts. Removing asks for confirmation inside the page.
- Selects several parts at once and sets or clears their price in one step.
- Shows two quantities per part in the opened row, as a sample for the database stage: **On hand** (a counter with - and + buttons) and **Per machine** (how many the machine uses). The header shows the total number of parts. Per-machine values are filled only for the 19 main assemblies listed on page 3 of the manual; everything else is blank until the next stage. Both numbers are saved in this browser only and travel in the CSV (`conteo`, `cant_por_maquina`).
- Exports and imports the catalog as CSV. Import checks the columns and duplicate SKUs before it replaces anything.
- Prints barcode labels (CODE128 of the SKU).
- Draws a hand-style sketch for each part. These are representative drawings by part type (screw, O-ring, valve, ...), chosen by keywords in the English name. They are not photos of the exact part.
- Works on phones (designed for 400px wide) and follows the device's light or dark mode.

**Important:** changes are saved in this browser only (localStorage, key `octagon-inv-v1`). Each device keeps its own copy, so export the CSV after editing.

## Publish on GitHub Pages

1. Create a GitHub repository and push this project (`git remote add origin ...`, then `git push -u origin master`).
2. On GitHub, go to **Settings → Pages**.
3. Under **Source**, choose *Deploy from a branch*, branch `master`, folder `/ (root)`, and save.
4. After about a minute the app is live at `https://<user>.github.io/<repo>/`.

The first time someone opens the page, the app loads `data/parts.csv`. From then on it uses that person's local copy.

> Opening `index.html` by double-clicking it (`file://`) won't work: the browser blocks reading `data/parts.csv`, so the app starts empty. Use **Import CSV** and pick `data/parts.csv`, or test locally with `python -m http.server` and open `http://localhost:8000`.

## How parts become verified

The published catalog contains only verified parts. A part is verified when a second, independent source agrees with the first reading. `data/build_parts.py` applies this rule:

1. The same Article no., 8-digit SKU and name were read identically on 2 or more clear pages, or
2. The name equals the title of the part's own chapter in the manual (the SKU was read once).

In both cases the Article no. must look like `NNN.NNN`, the 8-digit SKU must look like `11xxxxxx` and belong to no other article, and the manual must not have a typo flagged on that part. This is a cross-check of the reading, not a guarantee: the paper manual is still the final authority.

Everything else waits to be validated. That list is internal and is not published: the build writes it to `data/internal/` (ignored by git), together with a report of the rows to check. To work through it:

- Run the app locally (`python -m http.server`) and open `http://localhost:8000/?validate`. That mode shows the **Catalog** and **To validate** views, the evidence for each part, and the **Mark verified** buttons. It keeps its own saved copy, separate from the normal one.
- After checking a part against the paper manual, add its Article no. to `data/manual_validations.txt` and run `build_parts.py`. The part moves into `data/parts.csv`, and the next push publishes it.

The CSV carries the status in two columns: `validacion` (`validada` or `pendiente`) and `evidencia` (a short sentence).

## Update the catalog

**Changes made in the app** (prices, corrections):
1. In the app, click **Export CSV**.
2. Replace `data/parts.csv` with the exported file and commit it. People opening the page for the first time will see the new version.
3. Anyone who already has a local copy updates it with **Import CSV**.

**Re-extract from the manuals:**
1. Fix `data/transcription_A.txt`. Each page starts with `## image_no|file|section|module` and each row is `article|sku8|description`.
2. If you add a new part, add its Spanish name to `data/translations_es.py`.
3. Run `cd data && python build_parts.py`. This regenerates `parts.csv` (verified parts only) and, in `data/internal/`, `parts_all.csv` and `extraction_report.md`.

Re-extracting overwrites any prices in `parts.csv`. Once prices are loaded, edit them in the app instead.

## Files

- `index.html`: the app.
- `data/parts.csv`: the catalog (UTF-8 with BOM so Excel shows accents correctly). Column names are kept from the spec (`nombre_en`, `modulo`, `precio_cad`, ...). `nombre_es` is a translation made by Claude, not text from the manual. `imagen_origen` and `posicion_en_diagrama` point back to the source photo (they are in the CSV and the edit form, not on the card).
- `data/transcription_A.txt`: the manual's parts tables, transcribed page by page.
- `data/build_parts.py` and `data/translations_es.py`: build the CSV files and the report.
- `data/manual_validations.txt`: Article numbers checked by hand against the paper manual.
- `data/internal/`: local only, not committed (all parts, the report and the pilot).
- `IDEAS.md`: ideas outside the current scope.

The manual images are not committed to the repository.
