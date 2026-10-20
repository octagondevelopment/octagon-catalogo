# Octagon · Mastrena Parts Catalog

Internal catalog of Mastrena II spare parts for Octagon Services (Vancouver, BC). The app is a single `index.html` file, with no build step and no server. Its data comes from `data/parts.csv`.

## What it does

- Shows the catalog as a compact list: a sketch, the English and Spanish names, SKU and price. Tap a row to open its details; the actions (edit, label, remove) live there.
- Searches by name or SKU. Module tabs show counts, and you can also filter by subassembly (the manual's numbering, for example 1.10.2 Brew module), "No price" and "Needs review" (the rows marked medium or low confidence).
- Sorts by manual order, SKU, name, price, or needs-review first.
- Adds, edits (including price) and removes parts. Removing asks for confirmation inside the page.
- Selects several parts at once and sets or clears their price in one step.
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

## Update the catalog

**Changes made in the app** (prices, corrections):
1. In the app, click **Export CSV**.
2. Replace `data/parts.csv` with the exported file and commit it. People opening the page for the first time will see the new version.
3. Anyone who already has a local copy updates it with **Import CSV**.

**Re-extract from the manuals:**
1. Fix `data/transcription_A.txt`. Each page starts with `## image_no|file|section|module` and each row is `article|sku8|description`.
2. If you add a new part, add its Spanish name to `data/translations_es.py`.
3. Run `cd data && python build_parts.py`. This regenerates `parts.csv` and `extraction_report.md`.

Re-extracting overwrites any prices in `parts.csv`. Once prices are loaded, edit them in the app instead.

## Files

- `index.html`: the app.
- `data/parts.csv`: the catalog (UTF-8 with BOM so Excel shows accents correctly). Column names are kept from the spec (`nombre_en`, `modulo`, `precio_cad`, ...). `nombre_es` is a translation made by Claude, not text from the manual. `imagen_origen` and `posicion_en_diagrama` point back to the source photo (they are in the CSV and the edit form, not on the card).
- `data/transcription_A.txt`: the manual's parts tables, transcribed page by page.
- `data/build_parts.py` and `data/translations_es.py`: build the CSV and the report.
- `data/extraction_report.md`: totals and the rows to check against the paper manual.
- `data/pilot_parts.csv` and `data/_build_pilot.py`: the 3-image pilot Francisco approved.
- `IDEAS.md`: ideas outside the current scope.

The manual images are not committed to the repository.
