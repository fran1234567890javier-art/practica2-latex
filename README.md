# Práctica 2 · Quemar libros para alimentar máquinas

Documento LaTeX (clase `book`) sobre la IA y el escaneo destructivo de libros (*Project Panama*).

| Archivo | Contenido |
|---|---|
| `main.tex` | Documento principal |
| `referencias.bib` | Bibliografía BibTeX |
| `figuras/` | Imágenes en PDF (se regeneran con `python3 scripts/generar_figuras.py`) |
| `figuras/logo-umu.png` | Logo de la Universidad de Murcia que aparece en la portada (súbelo con este nombre exacto) |

## Compilar en Overleaf
1. *New Project → Upload Project* y sube un ZIP de este repositorio.
2. Compilador: **pdfLaTeX**. Overleaf ejecuta BibTeX automáticamente.
3. Descarga el PDF: es el tercer archivo del entregable.

En TeXstudio: `pdflatex main` → `bibtex main` → `pdflatex main` → `pdflatex main`.

Antes de entregar, cambia `\newcommand{\autor}{Nombre y Apellidos}` en `main.tex` por tu nombre.
