#!/usr/bin/env python3
"""Génère le site de Over9 dans ses neuf langues.

    python3 _src/build.py

**Une seule mise en page, un fichier de textes par langue** (`_src/textes/<code>.json`) : les neuf
versions ne peuvent pas diverger de structure, et une correction de gabarit les touche toutes. Le
site produit est statique — aucun script, aucune requête vers un tiers — et c'est lui que Netlify
sert ; ce dossier `_src` n'est que sa source, jamais publiée (`_src/publier.sh`).

L'anglais vit à la racine (`/`), chaque autre langue sous son code (`/fr/`, `/de/`…). Les captures
sont propres à chaque langue (`assets/img/<code>-<écran>.webp`) ; la bande des niveaux, faite des
illustrations de l'app, est commune.
"""

import html
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
TEXTES = RACINE / "_src" / "textes"
ORDRE = ["en", "fr", "de", "es", "it", "pt", "ja", "ko", "zh"]
DOMAINE = "https://over9fit.com"
NIVEAUX_MONTRES = [1, 9, 13, 18, 24, 25, 26]
PAGES = {"accueil": "", "support": "support/", "privacy": "privacy/"}

GLOBE = ('<svg class="globe" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="9.5" '
         'fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M2.5 12h19M12 2.5c3 3 3 16 0 19M12 2.5c-3 3-3 16 0 19" '
         'fill="none" stroke="currentColor" stroke-width="1.6"/></svg>')


def e(texte):
    return html.escape(texte, quote=True)


def charger():
    langues = {}
    for code in ORDRE:
        chemin = TEXTES / f"{code}.json"
        if chemin.exists():
            langues[code] = json.loads(chemin.read_text(encoding="utf-8"))
    if "en" not in langues:
        sys.exit("✗ _src/textes/en.json manque : l'anglais est la langue racine.")
    return langues


def url(langues, code, page):
    return langues[code]["meta"]["prefixe"] + PAGES[page]


def tete(langues, code, page, titre, description):
    alternatives = "\n".join(
        f'<link rel="alternate" hreflang="{langues[c]["meta"]["html_lang"]}" href="{DOMAINE}{url(langues, c, page)}">'
        for c in langues
    )
    return f"""<!doctype html>
<html lang="{langues[code]["meta"]["html_lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{DOMAINE}{url(langues, code, page)}">
{alternatives}
<link rel="alternate" hreflang="x-default" href="{DOMAINE}{url(langues, "en", page)}">
<link rel="icon" href="/assets/img/icone-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/icone-192.png">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="page">"""


def selecteur(langues, code, page):
    t = langues[code]
    actuel = ' aria-current="true"'
    items = "\n".join(
        f'        <li><a href="{url(langues, c, page)}" hreflang="{langues[c]["meta"]["html_lang"]}" '
        f'lang="{langues[c]["meta"]["html_lang"]}"{actuel if c == code else ""}>{e(langues[c]["meta"]["nom"])}</a></li>'
        for c in langues
    )
    return f"""    <details class="langue">
      <summary aria-label="{e(t["commun"]["langue"])}">{GLOBE}<span>{e(t["meta"]["nom"])}</span></summary>
      <ul>
{items}
      </ul>
    </details>"""


def entete(langues, code, page):
    t = langues[code]
    c = t["commun"]
    courant = lambda p: ' aria-current="page"' if p == page else ""
    return f"""  <header class="tete">
    <a class="marque" href="{url(langues, code, "accueil")}"><img src="/assets/img/icone-192.png" alt="" width="32" height="32">Over9</a>
    <nav aria-label="{e(c["aria_nav"])}">
      <a href="{url(langues, code, "support")}"{courant("support")}>{e(c["nav_support"])}</a>
      <a href="{url(langues, code, "privacy")}"{courant("privacy")}>{e(c["nav_privacy"])}</a>
{selecteur(langues, code, page)}
    </nav>
  </header>"""


def pied(langues, code):
    t = langues[code]
    c = t["commun"]
    mentions = f'\n      <a href="/fr/mentions-legales/">{e(c["mentions"])}</a>' if "mentions" in c else ""
    return f"""  <footer class="pied">
    <span>© 2026 Over9 · <a href="mailto:contact@over9fit.com">contact@over9fit.com</a></span>
    <nav aria-label="{e(c["aria_pied"])}">
      <a href="{url(langues, code, "accueil")}">{e(c["nav_home"])}</a>
      <a href="{url(langues, code, "support")}">{e(c["nav_support"])}</a>
      <a href="{url(langues, code, "privacy")}">{e(c["nav_privacy"])}</a>{mentions}
    </nav>
  </footer>
</div>
</body>
</html>
"""


def capture(code, ecran, alt):
    return (f'<img class="capture" src="/assets/img/{code}-{ecran}.webp" alt="{e(alt)}" '
            f'width="540" height="1066" loading="lazy">')


def accueil(langues, code):
    t = langues[code]
    a = t["accueil"]
    niveaux = "\n".join(
        f'        <figure><img src="/assets/img/niveau-{n}.webp" alt="" width="300" height="233" loading="lazy">'
        f'<figcaption>{e(a["auras"]["legende"].replace("{n}", str(n)))}</figcaption></figure>'
        for n in NIVEAUX_MONTRES
    )
    promesses = "\n".join(
        f'      <div class="promesse"><h3>{e(p["h3"])}</h3><p>{e(p["p"])}</p></div>' for p in a["promesses"]
    )
    bloc = lambda cle, ecran, inverse=False: f"""    <section class="bloc{" inverse" if inverse else ""}">
      <div class="texte">
        <h2>{e(a[cle]["h2"])}</h2>
        <p>{e(a[cle]["p"])}</p>
      </div>
      {capture(code, ecran, a[cle]["alt"])}
    </section>"""
    return f"""{tete(langues, code, "accueil", a["title"], a["description"])}
{entete(langues, code, "accueil")}

  <main>
    <section class="ouverture">
      <div class="titre-bloc">
        <div class="titre-feu">
          <img class="feu-fixe" src="/assets/img/feu.webp" alt="" width="960" height="540">
          <video class="feu" autoplay muted loop playsinline preload="auto" aria-hidden="true" poster="/assets/img/feu.webp">
            <source src="/assets/video/feu.mp4" type="video/mp4">
          </video>
          <img class="titre" src="/assets/img/titre.webp" alt="Over9" width="1080" height="599">
        </div>
        <img class="logo-k" src="/assets/img/logo-k.webp" alt="" width="400" height="426">
      </div>
      <h1>{e(a["h1"])}</h1>
      <p class="chapeau">{e(a["chapeau"])}</p>
      <p class="bientot">{e(a["bientot"])}</p>
    </section>

    <section class="seance">
      <div class="texte">
        <h2>{e(a["seance"]["h2"])}</h2>
        <p>{e(a["seance"]["p"])}</p>
      </div>
      <div class="duo">
        {capture(code, "seance", a["seance"]["alt_seance"])}
        {capture(code, "disques", a["seance"]["alt_disques"])}
      </div>
    </section>

{bloc("niveau", "accueil", inverse=True)}

    <section class="auras">
      <h2>{e(a["auras"]["h2"])}</h2>
      <p>{e(a["auras"]["p"])}</p>
      <div class="bande">
{niveaux}
      </div>
    </section>

{bloc("records", "statistiques")}

    <section class="corps3d">
      <div class="texte">
        <h2>{e(a["corps"]["h2"])}</h2>
        <p>{e(a["corps"]["p"])}</p>
      </div>
      <div class="trio">
        {capture(code, "corps-volume", a["corps"]["alt_volume"])}
        {capture(code, "corps-progression", a["corps"]["alt_progression"])}
        {capture(code, "corps-seance", a["corps"]["alt_seance"])}
      </div>
    </section>

{bloc("historique", "historique", inverse=True)}

    <section class="promesses" aria-label="{e(a["aria_promesses"])}">
{promesses}
    </section>
  </main>

{pied(langues, code)}"""


def texte_long(langues, code, page):
    t = langues[code]
    p = t[page]
    maj = f'\n    <p class="maj">{e(p["maj"])}</p>' if "maj" in p else ""
    corps = p["corps_html"].replace("{prefixe}", t["meta"]["prefixe"])
    return f"""{tete(langues, code, page, p["title"], p["description"])}
{entete(langues, code, page)}

  <main class="texte-long">
    <h1>{e(p["h1"])}</h1>{maj}
{corps}
  </main>

{pied(langues, code)}"""


def ecrire(chemin, contenu):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")
    return chemin.relative_to(RACINE)


def main():
    langues = charger()
    ecrits = []
    for code in langues:
        base = RACINE / langues[code]["meta"]["prefixe"].strip("/")
        ecrits.append(ecrire(base / "index.html", accueil(langues, code)))
        ecrits.append(ecrire(base / "support" / "index.html", texte_long(langues, code, "support")))
        ecrits.append(ecrire(base / "privacy" / "index.html", texte_long(langues, code, "privacy")))
    print(f"✓ {len(ecrits)} pages, {len(langues)} langues : {', '.join(langues)}")
    manquantes = [c for c in ORDRE if c not in langues]
    if manquantes:
        print(f"· langues sans textes encore : {', '.join(manquantes)}")


if __name__ == "__main__":
    main()
