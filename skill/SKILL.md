---
name: amigo-karting-publications
description: "Trouve des idees de publications (posts) pour les reseaux sociaux d'Amigo Karting en analysant le web. Declenche ce skill quand l'utilisateur veut des idees de contenu, des sujets de publication, des posts Facebook/Instagram/TikTok pour Amigo Karting, ou dit des choses comme 'trouve des idees de publications pour Amigo', 'idees de contenu karting', 'quoi publier sur les reseaux', 'nouvelles idees de posts', 'des sujets pour Amigo Karting', 'analyse internet pour des publications', ou toute variation. Le skill cherche sur le web (tendances, marronniers/dates saisonnieres, evenements a Gatineau/Outaouais, tendances karting), genere des idees avec un lien d'exemple par categorie, les ajoute a idees.json, et reconstruit le tableau HTML."
---

# Amigo Karting - Generateur d'idees de publications

Ce skill enrichit un outil **autonome** : le tableau `Idees-Publications-Amigo.html` est
un generateur qui fonctionne **tout seul** dans le navigateur (hors-ligne, sans installation,
sur n'importe quel ordinateur). L'utilisateur clique « Generer de nouvelles idees » et l'outil
sort une vague d'idees adaptee au mois courant, **sans Claude**.

Le role de ce skill = **ajouter de NOUVELLES idees fraiches/d'actualite** a la banque
(via une vraie recherche web), puis les injecter dans le tableau. L'utilisateur est
**francophone et non technique** : agir directement, pas de jargon.

## Contexte de l'entreprise (pour des idees pertinentes)

- **Amigo Karting** = centre de karting **exterieur** a **Gatineau, Quebec** (Outaouais).
- Piste **eclairee de 1,1 km** (soirees possibles).
- **Super-karts** haute performance, **chronometrage par transpondeurs** (type F1, jusqu'a 18 karts).
- **Mini-karts / go-karts** (max 40 km/h, securitaire). **Kiddy kars**, **trampolines**, **mini-golf Wacky Putt** => angle FAMILLE fort.
- Saison : **ouvert d'avril a mi-novembre**. Hors saison = teasing / cartes-cadeaux / retrospective.
- Pages : facebook.com/amigokarting , instagram.com/amigokarting , amigokarting.com

## Emplacement des fichiers

Dossier : `C:\Users\xavpo\OneDrive\Desktop\MonApp\Amigo-Publications\` (OneDrive => synchro auto).

| Fichier | Role |
|---------|------|
| `idees.json` | **Source de verite** : `{ exemples:{...}, idees:[...] }`. C'est ce que tu modifies. |
| `Idees-Publications-Amigo.html` | Le generateur autonome. Contient un bloc `<script id="lib">` rempli par le builder. NE PAS reecrire le reste. |
| `build_html.py` | Injecte `idees.json` dans le bloc `<script id="lib">` du HTML. Python standard, aucune dependance. |
| `chercher_nouvelles.py` | **Moteur de nouvelles** : RSS Google News (FR-CA) sur ~12 sujets, filtre anti-bruit, transforme en idees `cat:"Actualite"` (titre `À chaud :`, `exemple_url`=lien). ANTI-REPETITION via `historique_nouvelles.json` (cle=titre normalise) : ne re-propose jamais une nouvelle vue. Retire les actu auto de + de 25 jours (`ajoute_le`), plafonne a 18 affichees, puis relance build_html.py. Chaque idee auto porte `ajoute_le` + `cle_actu`. |
| `historique_nouvelles.json` | Memoire `{cle: date}` des nouvelles deja proposees (oubliees apres 180 j). Dans OneDrive => l'anti-repetition se synchronise entre ordinateurs. |
| `Chercher-de-nouvelles-idees.bat` | Double-clic Windows qui lance `chercher_nouvelles.py` (pour l'utilisateur non technique). |
| `LISEZMOI.txt` | Mode d'emploi pour l'utilisateur. |
| `skill/` | Copie de ce skill + scripts (pour reinstaller ailleurs). |

**Lien d'exemple par idee** : une idee peut avoir `exemple_url` + `exemple_label` (prioritaire). Sinon le HTML prend le lien de la map `exemples` selon `cat`. Les idees d'actualite utilisent `exemple_url` (le lien de la nouvelle).

**Deux facons d'ajouter de l'actualite** : (a) lancer `python chercher_nouvelles.py` pour un ramassage automatique rapide (textes a personnaliser) ; (b) MIEUX — faire la recherche web toi-meme (WebSearch) et ECRIRE des idees soignees ancrees dans l'actu (ex. GP du Canada F1, Festival L'Outaouais en fete, tendances TikTok), avec `exemple_url` = la source reelle. Privilegie (b) pour la qualite.

## Schema d'une idee (dans `idees.json` -> tableau `idees`)
```json
{
  "titre": "...",            // court, accrocheur, francais
  "cat": "...",              // Saisonnier, Marronnier, Video, Competition, Concours, Coulisses,
                             //   Promotion, Famille, Engagement, Temoignage, Educatif, UGC, Ambiance
                             //   (si nouvelle categorie, ajoute son lien dans "exemples")
  "format": "...",           // ex: Reel video, Carrousel, Story (sondage), Image, Live
  "mois": [6,7],             // mois ou l'idee est "du moment" (1=janv..12=dec). [] = toute saison.
                             //   Le generateur met ces idees en avant au bon moment.
  "pourquoi": "...",         // 1-2 phrases : pourquoi ca marche POUR AMIGO
  "objectif": "...",         // but marketing : Reservations | Notoriete | Vente | Fidelisation |
                             //   Engagement | Communaute | Image de marque   (s'affiche en badge 🎯)
  "angle": "...",            // LE twist malin/strategique (la "couche intelligente" de l'idee)
  "momentideal": "...",      // quand publier (jour/saison/heure)
  "variantes": ["...","..."],// 2-3 declinaisons a tester (affichees dans la recette)
  "script": [                // OPTIONNEL (idees video phares) : script mot a mot, scene par scene.
    {"t":"0-3s","plan":"ce qu'on filme","ecran":"texte a l'ecran","voix":"replique exacte a dire"}
  ],                         // s'affiche dans un bloc repliable "🎥 Script video mot a mot"
  "legende": "...",          // legende prete a publier, francais quebecois naturel, emojis ok
  "hashtags": "#AmigoKarting #Karting #Gatineau #Outaouais ...",
  "recette": {               // OPTIONNEL. Si absent, le HTML genere une recette auto selon le format.
                             //   N'en ecris une a la main que pour une idee phare (mieux ciblee).
    "type": "...", "duree": "...", "accroche": "...",
    "etapes": ["...", "..."], "texte_ecran": ["..."], "son": "...",
    "cta": "...", "astuce": "...", "materiel": "..."
  }
}
```
**Recettes "Comment la realiser"** : le HTML affiche pour CHAQUE idee une recette repliable
(accroche 3 sec, plan de tournage, texte a l'ecran, son, appel a l'action, astuce, materiel).
Si l'idee n'a pas de champ `recette`, `recettePour(it)` en genere une selon le `format`/les mots-cles
(video POV, reaction, Mario Kart, coulisses, chrono ; carrousel ; story ; image ; live ; publication).
Ecris un `recette` a la main seulement pour les idees phares ou tu veux un contenu sur-mesure.

Le **lien d'exemple** n'est PAS par idee : il vient de la map `exemples` selon `cat`.
Si tu crees une nouvelle categorie, ajoute une entree dans `exemples` avec un `url` + `label`
**reel** (vu dans tes resultats de recherche — ne jamais inventer d'URL).

## Procedure

### Etape 1 - Recherche web (le coeur du skill)
Fais **plusieurs WebSearch** pour des angles frais et actuels, selon la date du jour :
1. **Marronniers / saison du moment** (Fete des Peres, Saint-Jean, Fete du Canada, Fete des
   Meres, rentree, Halloween, longs week-ends, fin de saison...). Cherche "marronniers marketing [mois] [annee]".
2. **Evenements locaux Gatineau / Outaouais / Ottawa** a venir.
3. **Tendances de contenu karting / loisir** ([annee]). Cherche "karting social media content
   ideas [annee]" et "idees publications Facebook Quebec [annee]".

### Etape 2 - Generer les idees
Vise **6 a 12 nouvelles idees** par execution, au format ci-dessus.
- **Pas de doublon** : compare les `titre` aux idees deja dans `idees.json`.
- Ancre dans les **vrais atouts** d'Amigo. Mets le bon `mois`.

### Etape 3 - Mettre a jour idees.json
Ajoute les nouvelles idees au tableau `idees` (et toute nouvelle entree `exemples` au besoin).
Mets a jour `genere_le`. Reecris en UTF-8.

### Etape 4 - Reconstruire le tableau
```
python build_html.py
```
(ou `py` / `python3`). Le builder ne touche QUE le bloc `<script id="lib">` : le generateur
reste intact. **Ne reecris jamais le HTML a la main.** Sans Python : edite directement le bloc
`<script type="application/json" id="lib">` du HTML en y collant l'objet `{ "exemples":{...}, "idees":[...] }`.

### Etape 5 - Presenter le resultat
En francais simple : nb de nouvelles idees (+ total), dire de double-cliquer le HTML et de
cliquer « Generer de nouvelles idees », donner 2-3 exemples, + lien cliquable vers le HTML.

## Note
Tout reste dans OneDrive => deja portable sur les autres ordinateurs de l'utilisateur.
