#dirStructureToText.py

import os
from datetime import datetime

def listar_directorio_personalizado(ruta_base, archivo_salida="dirStructure.txt"):
    nombre_raiz = os.path.basename(ruta_base)
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(f"Fecha de creación: {fecha_actual}\n")
        f.write(f"{nombre_raiz}/\n")

        for root, dirs, files in os.walk(ruta_base):
            rel_path = os.path.relpath(root, ruta_base)

            if rel_path == ".":
                continue 

            depth = rel_path.count(os.sep) + 1

            carpetas = root.split(os.sep)

            #if "java_service" in carpetas and depth > 1:
            #    continue
            if any(ignorar in carpetas and depth >= 2 for ignorar in [".git", "static", "venv"]):
                continue

            sangria = "    " * depth
            f.write(f"{sangria}{os.path.basename(root)}/\n")
            for file in files:
                f.write(f"{sangria}    {file}\n")

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
archivo_salida = os.path.join(ruta_proyecto, "docs", "dirStructure.txt")
listar_directorio_personalizado(ruta_proyecto, archivo_salida)
