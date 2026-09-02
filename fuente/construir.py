"""
Generador de esta pagina: el precio de la alquiler.

    python -m fuente.construir

Si la fuente falla y no hay copia en cache, no se genera nada: no se
publica una pagina con datos inventados.
"""

from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import datos
from .enlaces import HUB, MENU

AQUI = Path(__file__).parent
PROYECTO = AQUI.parent
SALIDA = PROYECTO / "docs"

BASE_URL = "https://adrianezd.github.io/proyecciones-alquiler"

entorno = Environment(
    loader=FileSystemLoader(AQUI / "plantillas"),
    autoescape=select_autoescape(["html"]),
)

HOY = dt.date.today().isoformat()


def json_seguro(obj) -> str:
    texto = json.dumps(obj, ensure_ascii=False)
    return (texto
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
            .replace(" ", "\\u2028")
            .replace(" ", "\\u2029"))


def escribir(plantilla: str, **contexto) -> None:
    destino = SALIDA / "index.html"
    destino.parent.mkdir(parents=True, exist_ok=True)

    contexto.setdefault("raiz", "./")
    contexto.setdefault("menu", MENU)
    contexto.setdefault("hub", HUB)
    contexto.setdefault("base_url", BASE_URL)
    contexto.setdefault("ruta", "")
    contexto.setdefault("generado", HOY)

    destino.write_text(entorno.get_template(plantilla).render(**contexto), encoding="utf-8")
    print("  escrito     index.html")


def main() -> None:
    print("Construyendo: alquiler\n")

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir(parents=True)
    shutil.copytree(PROYECTO / "estatico", SALIDA / "estatico")

    codigo = datos.localizar_serie()
    if not codigo:
        print("  SALTADA     alquiler (no se localizo la serie)")
        (SALIDA / ".nojekyll").write_text("", encoding="utf-8")
        return

    tasas = datos.tasas_anuales(codigo)
    if len(tasas) < 4:
        print(f"  SALTADA     alquiler (la serie {codigo} devolvio {len(tasas)} datos)")
        (SALIDA / ".nojekyll").write_text("", encoding="utf-8")
        return

    tasas = tasas[-30:]

    escribir(
        "proyeccion.html",
        acento="alquiler",
        codigo_serie=codigo,
        titulo="Precio del alquiler: proyeccion a partir del INE",
        descripcion="Como evolucionaria una renta mensual si el indice de alquiler del INE "
                    "se comportara como hasta ahora.",
        encabezado="Precio del alquiler",
        bajada="La misma mecanica que la vivienda en compra, aplicada a la renta mensual. "
               "Ojo: la serie oficial de alquiler es corta, hay menos historico del que "
               "seria deseable.",
        etiqueta_valor="Alquiler mensual hoy",
        valor_defecto=900,
        datos_json=json_seguro({"tasas": tasas, "valor_defecto": 900}),
    )

    (SALIDA / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8"
    )
    (SALIDA / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'\n  <url><loc>{BASE_URL}/</loc><lastmod>{HOY}</lastmod></url>\n</urlset>\n',
        encoding="utf-8",
    )
    # Sin esto GitHub Pages pasa la carpeta por Jekyll y se come archivos.
    (SALIDA / ".nojekyll").write_text("", encoding="utf-8")

    print("\nListo.")


if __name__ == "__main__":
    main()
