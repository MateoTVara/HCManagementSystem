#dirStructureToText.py

import os

def listar_directorio_personalizado(ruta_base, archivo_salida="dirStructure.txt"):
    nombre_raiz = os.path.basename(ruta_base)
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(f"{nombre_raiz}/\n")

        for root, dirs, files in os.walk(ruta_base):
            rel_path = os.path.relpath(root, ruta_base)

            if rel_path == ".":
                continue 

            depth = rel_path.count(os.sep) + 1

            carpetas = root.split(os.sep)
            
            if any(ignorar in carpetas and depth >= 2 for ignorar in [".git", "static", "venv"]):
                continue

            sangria = "    " * depth
            f.write(f"{sangria}{os.path.basename(root)}/\n")
            for file in files:
                f.write(f"{sangria}    {file}\n")

ruta_proyecto = os.path.dirname(os.path.abspath(__file__))
listar_directorio_personalizado(ruta_proyecto)
