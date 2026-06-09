# -*- coding: utf-8 -*-
"""
MOTEUR DE NOUVELLES — Amigo Karting
===================================
Ratisse LARGE l'actualite (karting, F1, evenements Gatineau/Outaouais, sorties
famille, tendances) via les fils d'actualite RSS de Google News, garde les
nouvelles les plus recentes, et les transforme en idees de publications
(categorie "Actualite") directement dans idees.json, puis reconstruit le tableau.

METHODE PROPRE ET LEGALE : on lit des fils RSS publics (faits pour ca), avec une
petite pause entre les requetes. Pas de scraping agressif qui ferait bannir.

Aucune dependance externe : Python standard seulement.
Usage :  python chercher_nouvelles.py
(Besoin d'une connexion internet. Sinon, le script le dira et ne casse rien.)
"""
import json, os, re, time, ssl, html as ihtml
import urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "idees.json")
BUILD = os.path.join(HERE, "build_html.py")
HIST_PATH = os.path.join(HERE, "historique_nouvelles.json")  # memoire anti-repetition

# --- Sujets a ratisser (FR, Canada). On peut en ajouter librement. ---
REQUETES = [
    "karting",
    "go-kart",
    "course de karting",
    "Formule 1 Grand Prix Canada",
    "Gatineau evenement",
    "Gatineau famille activite",
    "Outaouais festival",
    "Outaouais sortie famille",
    "sortie famille Quebec ete",
    "activite plein air Outaouais",
    "Gatineau ete",
    "loisir famille Gatineau",
]

MAX_PAR_REQUETE = 2     # nb max de nouvelles gardees par sujet
MAX_TOTAL = 15          # nb max de nouvelles ajoutees par execution
JOURS_RECENTS = 40      # on ne garde que les nouvelles des X derniers jours
PAUSE = 0.7             # pause (sec) entre les requetes = poli
PRUNE_JOURS = 25        # une actualite auto disparait du tableau apres X jours
HIST_JOURS = 180        # on se souvient des nouvelles vues pendant X jours
MAX_AFFICHE_ACTU = 18   # nb max d'actualites auto affichees en meme temps

# Mots qui trahissent une nouvelle "bruit" (pas utile pour des publications).
BRUIT = ["épisode", "balado", "podcast", "horoscope", "météo", "meteo",
         "lotto", "loterie", "résultats du tirage", "nécrologie", "avis de décès",
         "votre journée", "en rappel", "bulletin de nouvelles"]


def est_bruit(titre):
    t = titre.lower()
    return any(b in t for b in BRUIT)

# --- Intelligence : score de PERTINENCE d'une nouvelle pour Amigo Karting ---
PERTINENCE_MIN = 3   # en dessous = hors-sujet, on ignore
MOTS_FORTS = ["karting", "kart ", "go-kart", "gokart", "karts", "formule 1", "formule1",
              " f1 ", "grand prix", "course automobile", "circuit", "autodrome", "pilote",
              "vitesse", "moteur", "racing"]          # 3 pts chacun
MOTS_MOYENS = ["festival", "événement", "evenement", "famille", "sortie", "activité", "activite",
               "vacances", "relâche", "relache", "ado", "jeunes", "anniversaire", "plein air",
               "attraction", "tourisme", "week-end", "fin de semaine", "loisir", "parc",
               "gatineau", "outaouais", "ottawa", "aylmer", "hull"]   # 1 pt chacun

def score_pertinence(titre):
    """Score la nouvelle : fort si liee au karting/course, moyen si evenement/famille/region."""
    t = " " + titre.lower() + " "
    s = 0
    for m in MOTS_FORTS:
        if m in t:
            s += 3
    for m in MOTS_MOYENS:
        if m in t:
            s += 1
    return s

UA = "Mozilla/5.0 (compatible; AmigoKartingNews/1.0)"
CTX = ssl.create_default_context()


def fil_rss(query):
    q = urllib.parse.quote(query + " when:%dd" % JOURS_RECENTS)
    return "https://news.google.com/rss/search?q=%s&hl=fr-CA&gl=CA&ceid=CA:fr" % q


def chercher(query):
    url = fil_rss(query)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15, context=CTX) as r:
        data = r.read()
    root = ET.fromstring(data)
    items = []
    for it in root.iter("item"):
        titre = (it.findtext("title") or "").strip()
        lien = (it.findtext("link") or "").strip()
        pub = it.findtext("pubDate")
        src_el = it.find("source")
        source = (src_el.text.strip() if src_el is not None and src_el.text else "")
        try:
            dt = parsedate_to_datetime(pub) if pub else None
            if dt and dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except Exception:
            dt = None
        if titre and lien:
            items.append({"titre": titre, "lien": lien, "date": dt, "source": source})
    return items


def nettoyer_titre(t):
    # Google News finit souvent par " - Source" : on enleve, et on raccourcit.
    t = ihtml.unescape(t)
    t = re.sub(r"\s+-\s+[^-]+$", "", t).strip()
    return t


def fabriquer_idee(n):
    titre_court = nettoyer_titre(n["titre"])
    if len(titre_court) > 80:
        titre_court = titre_court[:77].rstrip() + "..."
    src = (" (" + n["source"] + ")") if n["source"] else ""
    mois = (n["date"].month if n["date"] else datetime.now(timezone.utc).month)
    sc = n.get("score", 0)
    pertinence = "tres liee au karting/course" if sc >= 6 else "liee a ta region / aux sorties"
    legende = (
        "📣 Dans l'actualité : « %s ». "
        "Chez Amigo Karting, on rebondit dessus ! 🏁 "
        "[Adapte ce post à la nouvelle.] Viens vivre l'action sur notre piste "
        "éclairée de 1,1 km à Gatineau — karting, mini-golf et trampolines pour toute la gang."
        % titre_court
    )
    return {
        "titre": "À chaud : " + titre_court,
        "cat": "Actualite",
        "format": "Réactif (Story / Reel)",
        "mois": [mois],
        "pourquoi": "Nouvelle %s%s (score pertinence %d) : rebondir dessus rend ta publication d'actualite et augmente la portee." % (pertinence, src, sc),
        "legende": legende,
        "hashtags": "#AmigoKarting #Actualite #Karting #Gatineau #Outaouais",
        "exemple_url": n["lien"],
        "exemple_label": "Lire la nouvelle : " + titre_court + src,
        "objectif": "Notoriete",
        "angle": "Rebondir sur une actualite chaude met ta page dans une conversation qui a deja l'attention de tous : c'est de la portee empruntee, a cout zero.",
        "momentideal": "Le plus vite possible apres la parution : une actu se perime en quelques jours.",
        "variantes": ["Donne TON point de vue de pro du karting sur la nouvelle",
                      "Relie la nouvelle a une offre ou un defi chez Amigo"],
        "ajoute_le": datetime.now().strftime("%Y-%m-%d"),   # pour retirer les vieilles
        "cle_actu": nettoyer_titre(n["titre"]).lower(),      # pour ne jamais re-proposer
    }


def est_actu_auto(i):
    return str(i.get("titre", "")).startswith("À chaud :")


def reconstruire():
    try:
        import subprocess, sys
        subprocess.run([sys.executable, BUILD], check=True)
    except Exception as e:
        print("(!) N'a pas pu relancer build_html.py automatiquement : %s" % e)
        print("    Lance-le toi-meme :  python build_html.py")


def main():
    today = datetime.now()
    today_s = today.strftime("%Y-%m-%d")

    def age_jours(d):
        try:
            return (today - datetime.strptime(d, "%Y-%m-%d")).days
        except Exception:
            return 0

    data = json.load(open(JSON_PATH, encoding="utf-8"))
    idees = data.get("idees", [])

    # --- Memoire : nouvelles deja proposees une fois (pour ne JAMAIS repeter) ---
    hist = {}
    if os.path.exists(HIST_PATH):
        try:
            hist = json.load(open(HIST_PATH, encoding="utf-8"))
        except Exception:
            hist = {}

    # 1) Retirer les actualites AUTO devenues vieilles ( > PRUNE_JOURS jours ).
    #    (On garde les idees d'actualite ecrites a la main + toutes les autres.)
    retirees = 0
    gardees = []
    for i in idees:
        if est_actu_auto(i):
            aj = i.get("ajoute_le")
            if (not aj) or age_jours(aj) > PRUNE_JOURS:   # pas de date connue OU trop vieille
                retirees += 1
                continue
        gardees.append(i)
    idees = gardees

    # Cles a ne pas reproposer = historique + actualites encore affichees.
    cles_bloquees = set(hist.keys())
    for i in idees:
        if i.get("cle_actu"):
            cles_bloquees.add(i["cle_actu"])
    titres_existants = set(str(i.get("titre", "")).lower() for i in idees)

    # 2) Chercher les nouvelles, sauter le deja-vu ET le hors-sujet (score de pertinence).
    trouvees, vues, deja, horsujet = [], set(), 0, 0
    print("Recherche d'actualites sur %d sujets (tri par pertinence)...\n" % len(REQUETES))
    for q in REQUETES:
        try:
            res = chercher(q)
        except Exception as e:
            print("  - %-34s : pas accessible (%s)" % (q, type(e).__name__))
            continue
        gardees_q = 0
        for n in res:
            cle = nettoyer_titre(n["titre"]).lower()
            if cle in vues:
                continue
            if est_bruit(n["titre"]):
                continue
            if cle in cles_bloquees:        # deja proposee une autre fois -> on saute
                deja += 1
                continue
            if n["date"]:
                age = datetime.now(timezone.utc) - n["date"]
                if age > timedelta(days=JOURS_RECENTS):
                    continue
            sc = score_pertinence(n["titre"])
            if sc < PERTINENCE_MIN:         # hors-sujet (pas lie au karting/region/famille)
                horsujet += 1
                continue
            n["score"] = sc
            vues.add(cle)
            trouvees.append(n)
            gardees_q += 1
        print("  - %-34s : %d pertinente(s)" % (q, gardees_q))
        time.sleep(PAUSE)

    # 3) Classement INTELLIGENT : pertinence d'abord, puis fraicheur. Garde le top.
    vieux = datetime.min.replace(tzinfo=timezone.utc)
    trouvees.sort(key=lambda n: (n.get("score", 0), n["date"] or vieux), reverse=True)
    trouvees = trouvees[:MAX_TOTAL]
    nouvelles_idees, ajoutees = [], 0
    for n in trouvees:
        idee = fabriquer_idee(n)
        if idee["titre"].lower() in titres_existants:
            continue
        titres_existants.add(idee["titre"].lower())
        nouvelles_idees.append(idee)
        hist[idee["cle_actu"]] = today_s
        ajoutees += 1

    # 4) Assembler : nouvelles actualites en tete, puis on plafonne les actu auto.
    combine = nouvelles_idees + idees
    auto = [i for i in combine if est_actu_auto(i)][:MAX_AFFICHE_ACTU]  # recentes d'abord
    autres = [i for i in combine if not est_actu_auto(i)]
    data["idees"] = auto + autres

    # 5) Nettoyer la memoire (oublier ce qui est trop vieux) et tout sauvegarder.
    hist = {k: v for k, v in hist.items() if age_jours(v) <= HIST_JOURS}
    data["genere_le"] = today_s
    json.dump(data, open(JSON_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(hist, open(HIST_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("")
    print("  Nouveautes pertinentes ajoutees : %d" % ajoutees)
    print("  Deja vues (ignorees)            : %d" % deja)
    print("  Hors-sujet ecartees             : %d" % horsujet)
    print("  Vieilles retirees               : %d" % retirees)
    if ajoutees == 0 and (deja > 0 or horsujet > 0):
        print("\n  -> Rien de neuf ET pertinent depuis la derniere fois : le tableau est deja a jour.")

    reconstruire()


if __name__ == "__main__":
    main()
