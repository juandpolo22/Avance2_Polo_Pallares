"""Genera el libro HTML: ejecutar con  python generar_html.py  (desde esta carpeta).

1) Comprueba que SQLAlchemy se pueda importar. En algunos equipos Windows, el Control de aplicaciones
   bloquea sus módulos compilados (*_cy.*.pyd) y jupyter-book falla. SQLAlchemy 2.1 incluye una copia en
   Python puro de cada módulo, así que, si están bloqueados, se eliminan los compilados y se usa esa copia.
2) Compila el libro (los notebooks ya vienen ejecutados) en _build/html.
3) Abre _build/html/index.html en el navegador.
"""
import importlib.util
import pathlib
import subprocess
import sys
import webbrowser

AQUI = pathlib.Path(__file__).resolve().parent


def sqlalchemy_importa() -> bool:
    r = subprocess.run([sys.executable, "-c", "import sqlalchemy.sql.cache_key"], capture_output=True, text=True)
    return r.returncode == 0


def reparar_sqlalchemy() -> None:
    spec = importlib.util.find_spec("sqlalchemy")
    if spec is None or not spec.submodule_search_locations:
        sys.exit("SQLAlchemy no está instalado: ejecuta  pip install -r requirements.txt")
    carpeta = pathlib.Path(list(spec.submodule_search_locations)[0])
    borrados = 0
    for patron in ("*_cy.*.pyd", "*_cy.*.so"):
        for f in carpeta.rglob(patron):
            f.unlink()
            borrados += 1
    print(f"Se eliminaron {borrados} módulos compilados de SQLAlchemy (se usará su versión en Python puro).")


if not sqlalchemy_importa():
    print("SQLAlchemy no se puede importar con sus módulos compilados; aplicando la reparación...")
    reparar_sqlalchemy()
    if not sqlalchemy_importa():
        sys.exit("SQLAlchemy sigue sin importarse. Ejecuta: pip install \"sqlalchemy<2.1\" y vuelve a intentar.")

print("Compilando el libro...")
r = subprocess.run([sys.executable, "-c", "from jupyter_book.cli.main import main; main()", "build", str(AQUI)], cwd=AQUI)
if r.returncode != 0:
    sys.exit("La compilación falló: revisa el mensaje de arriba.")

indice = AQUI / "_build" / "html" / "index.html"
print(f"Listo: {indice}")
try:
    webbrowser.open(indice.as_uri())
except Exception:
    pass
