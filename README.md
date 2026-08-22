# Robótica Industrial · UNAB 2026

Sitio de la asignatura **Robótica Industrial** (Universidad Nacional de Almirante
Brown, Tecnicatura, ciclo 2026). Cada clase tiene su propia página HTML con URL
propia, pensada para enlazarse desde el aula virtual.

Toda la materia gira alrededor de un proyecto integrador grupal: el diseño de una
celda robotizada de fin de línea para *pick and place* de empaque.

Es HTML estático puro: GitHub Pages lo publica tal cual, sin proceso de build.

---

## Estructura

```
.
├── index.html              Portada: listado de las 16 clases por unidad
├── proyecto.html           El TP integrador: alcance, entregables e informe
├── cursada.html            Modalidad semipresencial y condiciones de aprobación
├── programa.html           Objetivos, bloques A-N y normas de referencia
├── recursos.html           Software, catálogos de fabricantes y normas
├── 404.html                Página de error
├── .nojekyll               Le dice a GitHub Pages que no procese con Jekyll
│
├── clases/
│   ├── clase-01/
│   │   ├── index.html      La clase
│   │   └── archivos/       PDF, slides, código y datos DE esa clase
│   ├── clase-02/
│   └── ... hasta clase-16/
│
├── assets/
│   ├── css/estilos.css     Único archivo de estilos del sitio
│   ├── js/                 (vacío por ahora)
│   └── img/                Imágenes generales del sitio
│
├── _plantilla/
│   └── contenido-clase.html    Punto de partida de una clase nueva
│
└── herramientas/
    ├── clases.json         Fuente de verdad: títulos, fechas, estados
    └── generar.py          Reconstruye menús, índice y navegación
```

Cada clase queda en una URL limpia, sin `.html` a la vista:

```
https://USUARIO.github.io/REPOSITORIO/clases/clase-01/
```

Ese es el link que pegás en el aula virtual.

---

## Flujo de trabajo, clase a clase

1. **Escribís la clase.** Abrís `clases/clase-NN/index.html` y editás
   únicamente lo que está entre estas dos líneas:

   ```html
   <!-- CONTENIDO:INICIO -->
   ... acá va todo lo tuyo ...
   <!-- CONTENIDO:FIN -->
   ```

   Todo lo que está fuera de esos marcadores lo maneja el generador. No hace
   falta que toques el menú, el encabezado ni la navegación.

2. **Subís el material.** Los PDF, slides y código van en
   `clases/clase-NN/archivos/`, y los enlazás con rutas relativas:

   ```html
   <a href="archivos/presentacion.pdf">Presentación de la clase (PDF)</a>
   ```

3. **Marcás la clase como publicada.** En `herramientas/clases.json`, en la
   entrada de esa clase, poné la fecha y cambiá el estado:

   ```json
   "fecha": "12/03/2026",
   "modalidad": "presencial",
   "estado": "publicada"
   ```

   `modalidad` acepta `virtual`, `presencial` o vacío, y aparece en el
   encabezado de la clase. `estado` solo cambia la etiqueta y el atenuado de
   la tarjeta en la portada: una clase `pendiente` igual es visible si alguien
   entra a su URL.

4. **Regenerás y publicás:**

   ```bash
   python herramientas/generar.py
   git add .
   git commit -m "Clase 01 publicada"
   git push
   ```

   Un minuto después ya está en línea.

### Agregar una clase nueva (más allá de la 16)

```bash
python herramientas/generar.py --nueva "Título de la clase"
```

Crea la entrada en `clases.json`, la carpeta `clases/clase-17/` con su
`archivos/`, la página a partir de la plantilla y la agrega al índice.

---

## Qué hace `generar.py`

Lee `herramientas/clases.json` y reescribe, en todas las páginas, solo las
regiones marcadas:

| Marcador | Qué contiene | Dónde aparece |
|---|---|---|
| `CABECERA` | Menú y marca del sitio | Todas las páginas |
| `ENCABEZADO` | Número, título, unidad, fecha y estado de la clase | Páginas de clase |
| `NAVCLASES` | Botones de clase anterior / siguiente | Páginas de clase |
| `CLASES` | Grilla de tarjetas agrupada por unidad | `index.html` |
| `VOLVER` y `CSS` | Enlaces absolutos con `base_url` | `404.html` |
| `PIE` | Pie de página | Todas las páginas |

**`CONTENIDO` nunca se toca.** Correr el generador dos veces seguidas no cambia
nada: es seguro ejecutarlo siempre que edites `clases.json`.

Si cambiás el nombre de la materia, la comisión, el docente o los links al aula
virtual, editás el bloque `curso` de `clases.json`, corrés el generador y se
actualiza en las 21 páginas de una.

### Contenido ya escrito

Las 16 clases tienen contenido redactado a partir de la estructura de bloques
A-N de la materia: teoría, ejercicios y un bloque **Avance del proyecto** que
indica qué entrega el grupo esa semana. Está pensado como base para editar, no
como texto definitivo — sobre todo los ejemplos numéricos y las listas de
documentación esperada.

---

## Publicar en GitHub Pages

Una sola vez:

```bash
git init
git add .
git commit -m "Sitio inicial de la materia"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```

Después, en GitHub: **Settings → Pages → Source: Deploy from a branch →
Branch: `main` / `(root)` → Save**. En un par de minutos el sitio queda en
`https://USUARIO.github.io/REPOSITORIO/`.

No hace falta configurar ninguna GitHub Action: al ser HTML estático, Pages lo
sirve directamente.

### Un ajuste obligatorio después del primer deploy

Si el sitio queda en `usuario.github.io/robotica/` (repositorio de proyecto, no
de usuario), abrí `herramientas/clases.json` y poné:

```json
"base_url": "/robotica/"
```

Después corré `python herramientas/generar.py`. Eso solo afecta a `404.html`,
que GitHub Pages sirve desde cualquier ruta y por eso no puede usar enlaces
relativos. El resto del sitio funciona con rutas relativas y no depende de esto.

---

## Cómo se ve en el aula virtual

Conviene enlazar dos cosas distintas:

- **En la portada del aula virtual:** el link a la raíz del sitio, como índice
  general de la materia.
- **En cada unidad o sección del aula virtual:** el link directo a la clase
  correspondiente (`.../clases/clase-05/`), para que el estudiante caiga
  exactamente en el material de ese día.

---

## Recursos de maquetado disponibles

Dentro del bloque de contenido podés usar estos componentes ya estilados:

```html
<div class="caja caja--nota">   <!-- verde: concepto clave -->
<div class="caja caja--aviso">  <!-- naranja: advertencia o error frecuente -->
<div class="caja caja--tarea">  <!-- violeta: consigna a entregar -->

<ul class="materiales">         <!-- lista de descargas -->
<div class="tabla-scroll">      <!-- envolver tablas anchas -->
<div class="video">             <!-- envolver un iframe de YouTube -->
<pre><code>...</code></pre>      <!-- bloque de código -->
```

Además, `<span class="completar">…</span>` marca en naranja un dato todavía
sin confirmar (fechas, porcentajes de asistencia, nota de promoción). Para
encontrarlos todos antes de publicar:

```bash
grep -rn 'class="completar"' --include=*.html .
```

El ejemplo completo de los componentes está en `_plantilla/contenido-clase.html`,
y una clase real ya escrita en `clases/clase-01/index.html`.
