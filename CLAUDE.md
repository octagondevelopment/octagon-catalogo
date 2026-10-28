# Octagon Parts Catalog: instructions for the development agent

This file is public (it lives in the repository). Keep names of people and of the client out of it. Private details stay in a private copy outside git.

## Who and how we work
- User: Francisco Aleuy, embedded PO at Octagon Services. He decides scope and priorities; the agent executes.
- Talk to Francisco in natural Chilean Spanish, direct and structured, no divider lines.
- Everything that ships is in English: app text, CSV column names, README, comments, commit messages. English is the base language; Spanish is secondary and appears only as the part name in `name_es`.
- Before a big change, show a short plan and wait for OK. Small, obvious changes: just do them.
- If something is ambiguous (an unreadable SKU, a part with no clear module), ask. Never invent data.
- Verify in the browser before saying something works, at 400 px wide, and say what was not verified.

## Business context
Octagon Services repairs Mastrena espresso machines for a coffee-chain client in Vancouver, BC. The owner decides scope and prices; administration and accounting handle money; technicians use parts in the field. Parts numbers live in printed manuals and hand-written bin labels. This project is the first digital catalog.

## Where things stand
- Live site: https://octagondevelopment.github.io/octagon-catalogo/ (GitHub Pages, branch `master`, root).
- Repository: https://github.com/octagondevelopment/octagon-catalogo (public). Push with the `octagondevelopment` account active in `gh`.
- 403 parts read from the Thermoplan *Spare parts catalogue Mastrena II 230V* (70 table pages). 137 are verified and published; 266 are pending (the count grows as parts are verified).
- Stage 1 (static site, no database) is built. Stage 2 is a shared database; Supabase was evaluated and is enough, with caveats: the free plan pauses after a week of inactivity and has no automatic backups, the public key is visible in the page so row-level security is mandatory, and offline use needs a local queue.

## Scope
Built: catalog list with sketches, search and filters, add/edit/remove with in-page confirmation, optional price in CAD (single and bulk), CSV export/import with validation, suggested EN/ES translation from a glossary, sample "On hand" and "Per machine" quantities, Thermoplan-style bag labels with barcode and the Octagon logo.

Next (stage 2, not started): shared database, login, two views (administrator or counter sees quantities and values; technician sees only what the owner and accounting define), loading real prices and stock.

Out of scope until stage 2: users, login, roles, truck stock and replenishment alerts, any backend, integrations (Vixxo, Infinity, QuickBooks, the Invoice app).

## Data rules
- Source: the manual photos, kept locally outside the repository. Read-only; never move, rename or delete them. Some Drive files may be cloud-only: report it and ask Francisco to mark the folder "Available offline". Photos are never committed.
- SKU = Thermoplan article number `NNN.NNN`. The 8-digit number `11xxxxxx` goes in `sku_8digit`. Some real SKUs have 6, 7 or 9 digits; keep them and mark the part pending.
- Never invent a SKU or complete characters that cannot be read. Watch OCR confusions: 0/O, 1/I/l, 5/S, 8/B, 2/Z.
- A part is published only when verified. Automatic rule (`data/build_parts.py`): same article, SKU and name read identically on 2+ clear pages, or the name equals its own chapter title; and the article is `NNN.NNN`, the SKU is `11xxxxxx` and unique, with no typo flagged. Parts Francisco checks by hand against the paper manual are listed in `data/manual_validations.txt`.
- The paper manual is the final authority. The automatic check is a cross-reading, not a guarantee.
- Published columns: `sku, sku_8digit, page, name_en, name_es, module, subassembly, price_cad, qty_per_machine, on_hand, notes, validation, evidence`. `data/parts.csv` has only verified parts; `data/parts_review.csv` has all 403 with their check state (owner's decision: everyone sees every part, colored by state: green hand-checked, amber auto-verified only, gray pending). `evidence` there is only the generic label "Validated against the paper manual" or empty. Module is Mechanical, Steam, Hydraulic, Chassis or Other. Price is optional and a part without price shows "No price", never $0.
- `name_es` is a translation, not manual text.

## Public versus internal
The repository is public. Never commit: `data/internal/` (the full extraction with source images and real evidence, the extraction report, the pilot, private copies of instructions), the manual photos, or names of people or of the client.
The page of the manual is public (owner's decision) so anyone can check a part quickly. Development-only fields (source image, diagram position, confidence, the real evidence text, the verify/unverify controls) are never shown to regular users and never exported in their CSV. They appear only in team mode, by opening a local copy with `?validate`.

## App rules
- One file, `index.html`, no build step. Scripts only from cdnjs (JsBarcode 3.11.6) and Google Fonts.
- localStorage key `octagon-inv-v1`, always in try/catch. The page must say, visibly, that data is saved in this browser only and that the CSV must be exported to keep or share changes.
- SKU is unique on add, edit and CSV import. Import shows a summary and errors before replacing anything.
- No `alert()`, `confirm()` or `prompt()`: confirmations are in the page.
- Mobile first: works at 400 px with no horizontal scroll; side gutters `max(16px, env(safe-area-inset-*))`; light and dark mode.
- Old saved copies and CSV files with Spanish column names must keep importing (`LEGACY_KEYS`).
- The translation hook `TRANSLATE_REMOTE_URL` is empty; an AI key must live on a server, never in the page.

## Git
- Small commits, messages in English, with the attribution lines the session asks for.
- Test locally (`python -m http.server`), then `git push`. Pages updates in about a minute; check the live URL.
- Anything outside the scope goes to `IDEAS.md`; do not build it.

## Definition of done for any change
- Works at 400 px and on desktop, light and dark, with no console errors.
- Search and filters still work together; add, edit and delete work without reload.
- The published CSV has English columns and only verified parts; no development fields leak.
- README updated if behavior changed.

## Open questions for the owner and accounting
- Do we have current prices and stock quantities (a spreadsheet)?
- What should the technician see?
- More than one truck or warehouse?
- Do technicians need the app without signal?
- Who loads and updates prices?
- Is there a file of the real Octagon logo?
