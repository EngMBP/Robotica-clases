#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del sitio de Robótica (UNAB).

Lee herramientas/clases.json y reconstruye, en TODAS las páginas del sitio,
las partes repetidas: el menú, el encabezado de cada clase, la navegación
anterior/siguiente, el listado de la portada y el pie.

Lo que vos escribís a mano NUNCA se toca: todo lo que está entre los
marcadores <!-- CONTENIDO:INICIO --> y <!-- CONTENIDO:FIN --> se conserva
tal cual.

Uso:
    python herramientas/generar.py               regenera el sitio completo
    python herramientas/generar.py --nueva "Título de la clase"
                                                 agrega una clase al final
                                                 de clases.json y regenera
"""

import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "herramientas" / "clases.json"
PLANTILLA = RAIZ / "_plantilla" / "contenido-clase.html"


# --------------------------------------------------------------------------
# Utilidades de regiones generadas
# --------------------------------------------------------------------------

def marcadores(nombre):
    return f"<!-- {nombre}:INICIO -->", f"<!-- {nombre}:FIN -->"


def reemplazar_region(texto, nombre, contenido):
    """Reemplaza el bloque entre marcadores. Devuelve (texto, se_encontro)."""
    ini, fin = marcadores(nombre)
    patron = re.compile(re.escape(ini) + r".*?" + re.escape(fin), re.S)
    if not patron.search(texto):
        return texto, False
    nuevo = f"{ini}\n{contenido}\n{fin}"
    return patron.sub(lambda _: nuevo, texto, count=1), True


def extraer_region(texto, nombre):
    """Devuelve el contenido entre marcadores, o None si no está."""
    ini, fin = marcadores(nombre)
    m = re.search(re.escape(ini) + r"(.*?)" + re.escape(fin), texto, re.S)
    return m.group(1).strip("\n") if m else None


def e(valor):
    return html.escape(str(valor or ""), quote=True)


# --------------------------------------------------------------------------
# Bloques comunes
# --------------------------------------------------------------------------

def bloque_cabecera(cfg, prefijo, pagina_actual):
    curso = cfg["curso"]
    enlaces = []
    for item in cfg["menu"]:
        actual = ' aria-current="page"' if item["url"] == pagina_actual else ""
        enlaces.append(
            f'      <a href="{prefijo}{e(item["url"])}"{actual}>{e(item["texto"])}</a>'
        )
    menu = "\n".join(enlaces)
    return f"""<header class="cabecera">
  <div class="cabecera__interior">
    <a class="marca" href="{prefijo}index.html">
      <span class="marca__materia">{e(curso["materia"])}</span>
      <span class="marca__uni">{e(curso["universidad"])} · {e(curso["ciclo"])}</span>
    </a>
    <nav class="menu">
{menu}
    </nav>
  </div>
</header>"""


def bloque_pie(cfg, prefijo):
    curso = cfg["curso"]
    izquierda = [f'{e(curso["materia"])} · {e(curso["universidad_larga"])}']
    if curso.get("comision"):
        izquierda.append(f'Comisión {e(curso["comision"])}')
    if curso.get("docente"):
        izquierda.append(e(curso["docente"]))
    izquierda.append(e(curso["ciclo"]))

    derecha = []
    if curso.get("aula_virtual"):
        derecha.append(f'<a href="{e(curso["aula_virtual"])}">Aula virtual</a>')
    if curso.get("repositorio"):
        derecha.append(f'<a href="{e(curso["repositorio"])}">Repositorio</a>')

    return f"""<footer class="pie">
  <div class="pie__interior">
    <span>{" · ".join(izquierda)}</span>
    <span>{" · ".join(derecha)}</span>
  </div>
</footer>"""


def bloque_encabezado_clase(clase, prefijo):
    modos = {"virtual": "Encuentro virtual sincrónico",
             "presencial": "Encuentro presencial"}
    meta = []
    if clase.get("fecha"):
        meta.append(f'<span>Fecha: {e(clase["fecha"])}</span>')
    if clase.get("modalidad") in modos:
        meta.append(f'<span>{modos[clase["modalidad"]]}</span>')
    if clase.get("duracion"):
        meta.append(f'<span>Duración: {e(clase["duracion"])}</span>')
    if clase.get("estado") == "publicada":
        meta.append('<span class="etiqueta etiqueta--publicada">Publicada</span>')
    else:
        meta.append('<span class="etiqueta">Pendiente</span>')

    unidad = f' · {e(clase["unidad"])}' if clase.get("unidad") else ""
    numero = f'Clase {clase["numero"]:02d}'

    return f"""  <header class="clase__cabecera">
    <p class="clase__migas"><a href="{prefijo}index.html">Clases</a> / {numero}</p>
    <p class="clase__numero">{numero}{unidad}</p>
    <h1>{e(clase["titulo"])}</h1>
    <div class="clase__meta">
      {chr(10).join("      " + m for m in meta).strip()}
    </div>
  </header>"""


def bloque_navclases(clases, i):
    anterior = clases[i - 1] if i > 0 else None
    siguiente = clases[i + 1] if i < len(clases) - 1 else None
    partes = []
    if anterior:
        partes.append(
            f'  <a class="anterior" href="../{e(anterior["slug"])}/">'
            f'<span>Clase anterior</span>'
            f'<strong>{anterior["numero"]:02d} · {e(anterior["titulo"])}</strong></a>'
        )
    if siguiente:
        partes.append(
            f'  <a class="siguiente" href="../{e(siguiente["slug"])}/">'
            f'<span>Clase siguiente</span>'
            f'<strong>{siguiente["numero"]:02d} · {e(siguiente["titulo"])}</strong></a>'
        )
    if not partes:
        return '<nav class="navclases"></nav>'
    return '<nav class="navclases">\n' + "\n".join(partes) + "\n</nav>"


def bloque_listado(clases):
    """Tarjetas de la portada, agrupadas por unidad."""
    salida = []
    unidad_actual = None
    abierta = False
    for c in clases:
        unidad = c.get("unidad", "")
        if unidad != unidad_actual:
            if abierta:
                salida.append("</div>")
            unidad_actual = unidad
            if unidad:
                salida.append(f'<h2 class="unidad">{e(unidad)}</h2>')
            salida.append('<div class="grilla">')
            abierta = True

        publicada = c.get("estado") == "publicada"
        clase_css = "tarjeta" if publicada else "tarjeta tarjeta--pendiente"
        etiqueta = (
            '<span class="etiqueta etiqueta--publicada">Publicada</span>'
            if publicada else '<span class="etiqueta">Pendiente</span>'
        )
        fecha = f'<span>{e(c["fecha"])}</span>' if c.get("fecha") else ""
        salida.append(
            f'  <a class="{clase_css}" href="clases/{e(c["slug"])}/">\n'
            f'    <span class="tarjeta__numero">Clase {c["numero"]:02d}</span>\n'
            f'    <h3 class="tarjeta__titulo">{e(c["titulo"])}</h3>\n'
            f'    <p class="tarjeta__resumen">{e(c.get("resumen", ""))}</p>\n'
            f'    <span class="tarjeta__pie">{etiqueta}{fecha}</span>\n'
            f'  </a>'
        )
    if abierta:
        salida.append("</div>")
    return "\n".join(salida)


# --------------------------------------------------------------------------
# Escritura de páginas
# --------------------------------------------------------------------------

def pagina_clase(cfg, clases, i, contenido):
    c = clases[i]
    curso = cfg["curso"]
    prefijo = "../../"
    titulo = f'Clase {c["numero"]:02d} · {c["titulo"]} — {curso["materia"]} {curso["universidad"]}'
    ini, fin = marcadores("CONTENIDO")
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(c.get('resumen', ''))}">
<link rel="stylesheet" href="{prefijo}assets/css/estilos.css">
</head>
<body>

<!-- CABECERA:INICIO -->
{bloque_cabecera(cfg, prefijo, "index.html")}
<!-- CABECERA:FIN -->

<main>
<article class="clase">

<!-- ENCABEZADO:INICIO -->
{bloque_encabezado_clase(c, prefijo)}
<!-- ENCABEZADO:FIN -->

{ini}
{contenido}
{fin}

</article>

<!-- NAVCLASES:INICIO -->
{bloque_navclases(clases, i)}
<!-- NAVCLASES:FIN -->
</main>

<!-- PIE:INICIO -->
{bloque_pie(cfg, prefijo)}
<!-- PIE:FIN -->

</body>
</html>
"""


def contenido_inicial(clase):
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    return (plantilla
            .replace("{{NUMERO}}", f'{clase["numero"]:02d}')
            .replace("{{TITULO}}", clase["titulo"])
            .replace("{{SLUG}}", clase["slug"])
            .rstrip("\n"))


def generar():
    cfg = json.loads(DATOS.read_text(encoding="utf-8"))
    clases = sorted(cfg["clases"], key=lambda c: c["numero"])
    novedades, actualizadas = [], []

    # --- páginas de clase ---
    for i, c in enumerate(clases):
        carpeta = RAIZ / "clases" / c["slug"]
        archivos = carpeta / "archivos"
        archivos.mkdir(parents=True, exist_ok=True)
        gitkeep = archivos / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")

        destino = carpeta / "index.html"
        if destino.exists():
            previo = destino.read_text(encoding="utf-8")
            contenido = extraer_region(previo, "CONTENIDO")
            if contenido is None:
                print(f"  ! {destino.relative_to(RAIZ)}: faltan los marcadores "
                      f"CONTENIDO, no se toca")
                continue
            actualizadas.append(c["slug"])
        else:
            contenido = contenido_inicial(c)
            novedades.append(c["slug"])

        destino.write_text(pagina_clase(cfg, clases, i, contenido), encoding="utf-8")

    # --- páginas sueltas de la raíz ---
    for pagina in sorted(RAIZ.glob("*.html")):
        texto = pagina.read_text(encoding="utf-8")
        original = texto
        # GitHub Pages sirve 404.html desde cualquier ruta, así que sus enlaces
        # no pueden ser relativos: usan la base_url configurada en clases.json.
        prefijo = cfg["curso"].get("base_url", "/") if pagina.name == "404.html" else ""
        texto, _ = reemplazar_region(
            texto, "CABECERA", bloque_cabecera(cfg, prefijo, pagina.name))
        texto, _ = reemplazar_region(texto, "PIE", bloque_pie(cfg, prefijo))
        texto, _ = reemplazar_region(
            texto, "CSS",
            f'<link rel="stylesheet" href="{prefijo}assets/css/estilos.css">')
        texto, _ = reemplazar_region(
            texto, "VOLVER",
            f'<p>Volvé al <a href="{prefijo}index.html">listado de clases</a> '
            f'para encontrar lo que buscabas.</p>')
        if pagina.name == "index.html":
            texto, ok = reemplazar_region(texto, "CLASES", bloque_listado(clases))
            if not ok:
                print("  ! index.html: faltan los marcadores CLASES")
        if texto != original:
            pagina.write_text(texto, encoding="utf-8")

    print(f"Sitio generado: {len(clases)} clases.")
    if novedades:
        print(f"  nuevas       : {', '.join(novedades)}")
    if actualizadas:
        print(f"  actualizadas : {len(actualizadas)} (contenido conservado)")


def agregar_clase(titulo):
    cfg = json.loads(DATOS.read_text(encoding="utf-8"))
    numero = max((c["numero"] for c in cfg["clases"]), default=0) + 1
    ultima = max(cfg["clases"], key=lambda c: c["numero"], default=None)
    cfg["clases"].append({
        "numero": numero,
        "slug": f"clase-{numero:02d}",
        "titulo": titulo,
        "resumen": "",
        "unidad": ultima["unidad"] if ultima else "",
        "fecha": "",
        "duracion": ultima.get("duracion", "") if ultima else "",
        "estado": "pendiente",
    })
    DATOS.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    print(f"Agregada la clase {numero:02d}: {titulo}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--nueva":
        if len(sys.argv) < 3:
            sys.exit('Falta el título: python herramientas/generar.py --nueva "Título"')
        agregar_clase(" ".join(sys.argv[2:]))
    generar()
