# Octagon · Catálogo de partes Mastrena

Catálogo interno de repuestos Mastrena II para Octagon Services (Vancouver, BC). Es un solo archivo `index.html`, sin build ni servidor. Los datos vienen de `data/parts.csv`.

## Qué hace

- Lista las piezas con SKU (Article no. de Thermoplan), SKU de 8 dígitos, nombre EN/ES, módulo, subconjunto y precio en CAD (opcional; si falta se muestra "sin precio").
- Busca por nombre o SKU y filtra por módulo (Mechanical, Steam, Hydraulic, Chassis, Other).
- Permite agregar, editar (precio incluido) y quitar piezas. Para quitar una pieza se confirma dentro de la página.
- Exporta e importa el catálogo en CSV. Antes de reemplazar los datos, la importación revisa las columnas y los SKU duplicados.
- Genera etiquetas con código de barras (CODE128 del SKU) para imprimir.

**Importante:** los cambios se guardan solo en el navegador (localStorage, clave `octagon-inv-v1`). Cada dispositivo tiene su propia copia, así que hay que exportar el CSV después de editar.

## Publicar en GitHub Pages

1. Crea un repositorio en GitHub y sube este proyecto (`git remote add origin ...` y luego `git push -u origin main`).
2. En GitHub, ve a **Settings → Pages**.
3. En **Source** elige *Deploy from a branch*, la rama `main` y la carpeta `/ (root)`. Guarda.
4. Al minuto la app queda en `https://<usuario>.github.io/<repo>/`.

La primera vez que alguien abre la página, la app carga `data/parts.csv`. Desde ahí trabaja con su copia local.

> Si abres `index.html` con doble clic (`file://`), el navegador no deja leer `data/parts.csv` y la app parte vacía. En ese caso usa **Importar CSV** y elige `data/parts.csv`. También puedes probarla localmente con `python -m http.server` y abrir `http://localhost:8000`.

## Actualizar el catálogo

**Cambios hechos en la app** (precios, correcciones):
1. En la app, toca **Exportar CSV**.
2. Reemplaza `data/parts.csv` con el archivo exportado y haz commit. Desde ahí, quien abra la página por primera vez verá la versión nueva.
3. Quien ya tiene una copia local la actualiza con **Importar CSV**.

**Re-extraer desde los manuales:**
1. Corrige `data/transcripcion_A.txt`. Cada página empieza con `## nro|imagen|sección|módulo` y cada fila es `article|sku8|descripción`.
2. Si hay una pieza nueva, agrega su traducción en `data/traducciones.py`.
3. Ejecuta `cd data && python build_parts.py`. Esto regenera `parts.csv` y `reporte_extraccion.md`.

Ojo: re-extraer pisa los precios que haya en `parts.csv`. Si ya hay precios cargados, edítalos en la app.

## Archivos

- `index.html`: la app.
- `data/parts.csv`: el catálogo (UTF-8 con BOM para que Excel muestre bien los acentos).
- `data/transcripcion_A.txt`: la transcripción de las tablas del manual, página por página.
- `data/build_parts.py` y `data/traducciones.py`: generan el CSV y el reporte.
- `data/reporte_extraccion.md`: totales y filas para revisar contra el papel.
- `data/pilot_parts.csv`: el piloto de 3 imágenes que validó Francisco.
- `IDEAS.md`: ideas fuera del alcance actual.

Las imágenes de los manuales no se suben al repositorio.
