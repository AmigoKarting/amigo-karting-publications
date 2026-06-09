# -*- coding: utf-8 -*-
"""
Met a jour le tableau (Idees-Publications-Amigo.html) a partir de idees.json.

Le tableau HTML est un GENERATEUR autonome : il contient un bloc de donnees
   <script type="application/json" id="lib"> ... </script>
Ce script ne fait que reinjecter le contenu de idees.json (exemples + idees)
dans ce bloc. Le reste du tableau (le generateur) reste intact.

Aucune dependance externe : Python standard seulement.
Usage :  python build_html.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "idees.json")
HTML_PATH = os.path.join(HERE, "Idees-Publications-Amigo.html")

DEBUT = '<script type="application/json" id="lib">'
FIN = "</script>"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

lib = {"exemples": data.get("exemples", {}), "idees": data.get("idees", [])}
lib_json = json.dumps(lib, ensure_ascii=False, indent=1)

if not os.path.exists(HTML_PATH):
    raise SystemExit(
        "ERREUR : Idees-Publications-Amigo.html est introuvable. "
        "Ce fichier est le generateur et doit exister (il est dans OneDrive)."
    )

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

i = html.find(DEBUT)
if i == -1:
    raise SystemExit("ERREUR : bloc de donnees '<script id=\"lib\">' introuvable dans le HTML.")
j = html.find(FIN, i)
if j == -1:
    raise SystemExit("ERREUR : fin du bloc de donnees introuvable dans le HTML.")

nouveau = DEBUT + "\n" + lib_json + "\n" + html[j:]
html = html[:i] + nouveau

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("OK -> " + HTML_PATH)
print(str(len(lib["idees"])) + " idees injectees dans le tableau.")
