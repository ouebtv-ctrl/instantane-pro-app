#!/usr/bin/env python3
"""Fabrique la version Netlify d'Instantané Pro à partir de l'index.html de la version Claude.

Usage : python3 build_netlify.py SOURCE_DIR SORTIE_DIR
  SOURCE_DIR : dossier qui contient l'index.html de la version Claude et son dossier accueil/
  SORTIE_DIR : dossier publié sur Netlify (index.html, accueil/, manifest.webmanifest, icônes)

Chaque remplacement est vérifié : si la version Claude a changé à cet endroit, le script
s'arrête et dit lequel, au lieu de produire une copie à moitié transformée.
Modifications (validées par Eric le 21 novembre 2026) :
 1. « Créer la story » devient « Préparer avec mon IA » (copie l'article et la consigne du bloc Import IA)
 2. « Affiner le titre avec Claude » devient « Demander un autre titre à mon IA »
 3. Légende : « Générer » devient « Copier la demande pour mon IA »
 4. Import IA inchangé
 5. navigator.storage.persist() au démarrage
 6. manifeste et icône •1 pour l'écran d'accueil de l'iPhone
 7. bouton « Aide » près du petit i de l'accueil
 Aucun appel à window.claude dans la copie.
"""
import os, re, shutil, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE = 'https://instantane-pro-presentation-ericleon.netlify.app/guide/'
VERT = '#007A97'


def rep(s, old, new, count=1, regex=False):
    n = len(re.findall(old, s)) if regex else s.count(old)
    if (count == 'any' and n == 0) or (count != 'any' and n != count):
        sys.exit(f'ÉCHEC : « {old[:70]} » trouvé {n} fois (attendu {count}). La version Claude a changé à cet endroit.')
    return re.sub(old, new, s) if regex else s.replace(old, new)


def build(src_dir, out_dir):
    s = open(os.path.join(src_dir, 'index.html'), encoding='utf-8').read()

    # 6. écran d'accueil de l'iPhone
    head = ('<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<link rel="manifest" href="manifest.webmanifest">'
            '<link rel="apple-touch-icon" href="icone-180.png">'
            '<link rel="icon" type="image/png" href="icone-192.png">'
            '<meta name="apple-mobile-web-app-capable" content="yes">'
            '<meta name="mobile-web-app-capable" content="yes">'
            '<meta name="apple-mobile-web-app-title" content="Instantané Pro">'
            '<meta name="apple-mobile-web-app-status-bar-style" content="default">'
            f'<meta name="theme-color" content="{VERT}">')
    s = rep(s, '<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">', head)

    # 1. Article source et génération
    s = rep(s, 'Claude en tire des titres journalistiques.', 'Votre IA en tirera le bloc à importer.')
    s = rep(s, '<button id="btnGen" class="primary" type="button">Créer le carrousel</button>',
               '<button id="btnGen" class="primary" type="button">Préparer avec mon IA</button>')
    s = rep(s, "$('btnGen').textContent = 'Créer ' + LE[mode];", "$('btnGen').textContent = 'Préparer avec mon IA';")
    s = rep(s, 'Remplir sans Claude', 'Remplir sans IA', count='any')
    s = rep(s, 'Garder le titre : Claude ne réécrit que le reste', 'Garder le titre : votre IA ne réécrit que le reste')
    s = rep(s, r"\n  status\(vb\(\) \? 'Claude écrit le titre de la couverture[^\n]*\n",
               "\n  status('L’application copie l’article et la consigne : collez-les dans votre IA, puis collez sa réponse dans Import IA. Relisez avant de publier.');\n",
               regex=True)

    s = rep(s, 'Collez l’article, puis « Créer le carrousel ».', 'Collez l’article, puis « Préparer avec mon IA ».')
    s = rep(s, 'ou collez l’article puis « Créer la story ».', 'ou collez l’article puis « Préparer avec mon IA ».')
    s = rep(s, 'Collez l’article, puis « Créer ${LE[mode]} ».', 'Collez l’article, puis « Préparer avec mon IA ».')

    # 2. Demander un autre titre à mon IA
    s = rep(s, '<strong style="font-size:16px">Affiner le titre avec Claude</strong>\n            <ol class="chat" id="refineLog" aria-live="polite"></ol>',
               '<p class="note" id="refineHelp" style="margin:0">Touchez un bouton ou écrivez votre demande : elle est copiée avec le titre actuel. Collez-la dans votre IA, puis collez son bloc dans Import IA.</p>\n'
               '            <ol class="chat" id="refineLog" aria-live="polite" style="display:none"></ol>')
    s = rep(s, '<label class="f">Votre demande<textarea id="refineIn"', '<label class="f">Votre demande (facultative)<textarea id="refineIn"')
    s = rep(s, '<button id="btnRefine" class="small primary" type="button">Envoyer à Claude</button>',
               '<button id="btnRefine" class="small primary" type="button">Copier la demande pour mon IA</button>')
    s = rep(s, '<button id="btnRefineUndo" class="small" type="button">', '<button id="btnRefineUndo" class="small" type="button" style="display:none">')
    s = rep(s, '<button id="btnRefineReset" class="small" type="button">', '<button id="btnRefineReset" class="small" type="button" style="display:none">')
    s = rep(s, '<div class="actions"><button id="btnAltPage"', '<div class="actions" style="display:none"><button id="btnAltPage"')
    s = rep(s, '<div class="actions"><button id="btnAltTitle"', '<div class="actions" style="display:none"><button id="btnAltTitle"')
    s = rep(s, '<p class="note" id="altPageNote"></p>', '<p class="note" id="altPageNote" style="display:none"></p>')
    s = rep(s, '<p class="note" id="altNote"></p>', '<p class="note" id="altNote" style="display:none"></p>')
    s = rep(s, "sec('Affiner le titre avec Claude', false, 'axAff')", "sec('Demander un autre titre à mon IA', false, 'axAff')")
    s = rep(s, "sAff.title(shown($('refine')) || shown(act('btnAltTitle')) ? 'Affiner le titre avec Claude' : 'Affiner le texte avec Claude');",
               "sAff.title('Demander un autre titre à mon IA');")

    # 3. Légende de publication
    s = rep(s, '<button id="btnCapGen" class="small" type="button">Générer</button>',
               '<button id="btnCapGen" class="small" type="button">Copier la demande pour mon IA</button>')
    s = rep(s, 'La légende apparaît ici après « Créer » ou « Générer ».', 'Collez ici la légende préparée par votre IA, ou écrivez-la.')

    # Réglages : les consignes partent désormais dans les demandes copiées
    s = rep(s, r'<p class="note" id="consNote">Claude applique ces consignes[^<]*</p>',
               '<p class="note" id="consNote">Ces consignes sont ajoutées à chaque demande copiée pour votre IA (« Préparer avec mon IA », autre titre, légende). Elles s’ajoutent aux règles de l’outil : aucun fait absent de la source, longueurs respectées.</p>',
               regex=True)

    # aucun appel à Claude
    s = rep(s, r"(?s)if \(window\.claude && window\.claude\.use\)\{\n.*?\n\} else claudeState = 'done';",
               "claudeState = 'done'; /* version web : aucun appel à Claude */", regex=True, count=1)
    s = rep(s, "  if (window.claude && window.claude.use) window.claude.use('downloads').then(d => { dl = d; }).catch(() => {});\n", '')
    # 7. bouton Aide près du petit i
    s = rep(s, r'(<button class="ic" id="hInfo" type="button" aria-label="Informations">.*?</button>)',
               r'<div class="hL">\1<a class="hAide" id="hAide" href="' + GUIDE + r'" target="_blank" rel="noopener">Aide</a></div>', regex=True)
    css = ('#home .hL{display:flex;align-items:center;gap:12px}'
           '#home .hAide{display:inline-flex;align-items:center;min-height:34px;padding:0 15px;border-radius:999px;'
           'border:1px solid var(--pAb);background:var(--pA);color:var(--ink);font:600 15px Poppins,sans-serif;'
           'text-decoration:none;-webkit-tap-highlight-color:transparent}'
           '#home .hAide:active{transform:translateY(1px);filter:brightness(.97)}'
           '#txBox{display:none!important}\n')
    s = rep(s, '#home .hTop{display:flex;', css + '#home .hTop{display:flex;')

    # 1, 2, 3, 5 : le code de la version web
    js = open(os.path.join(HERE, 'netlify-ia.js'), encoding='utf-8').read()
    # inséré à la fin du script principal (une fonction fermée) pour accéder à ses variables
    fin = "addEventListener('resize', () => setTimeout(() => { try { addUI(); } catch(e){} }, 30));\n}\n"
    s = rep(s, fin + '})();\n</script>', fin + js + '})();\n</script>')

    if 'window.claude' in s:
        sys.exit('ÉCHEC : il reste un appel à window.claude.')
    if '\u2014' in js:
        sys.exit('ÉCHEC : tiret cadratin dans le code ajouté.')

    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(s)
    if os.path.isdir(os.path.join(out_dir, 'accueil')):
        shutil.rmtree(os.path.join(out_dir, 'accueil'))
    shutil.copytree(os.path.join(src_dir, 'accueil'), os.path.join(out_dir, 'accueil'))

    manifest = {
        'name': 'Instantané Pro', 'short_name': 'Instantané Pro', 'lang': 'fr',
        'start_url': './', 'scope': './', 'display': 'standalone',
        'background_color': '#FFFFFF', 'theme_color': VERT,
        'icons': [{'src': 'icone-192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': 'icone-512.png', 'sizes': '512x512', 'type': 'image/png'},
                  {'src': 'icone-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]}
    open(os.path.join(out_dir, 'manifest.webmanifest'), 'w', encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False, indent=2))
    icons(out_dir)
    print('Version Netlify prête :', out_dir)


def icons(out_dir):
    """Icône •1 : le logo de l'outil (point jaune #FFC300, 1 blanc) sur le vert de la charte."""
    from PIL import Image, ImageDraw
    one = [(59, 0), (71, 0), (71, 63), (89, 63), (89, 75), (38, 75), (38, 63), (56, 63), (56, 17), (41, 25.5), (41, 12)]
    S = 2048
    im = Image.new('RGB', (S, S), VERT)
    d = ImageDraw.Draw(im)
    k = S * 0.56 / 89  # logo de 89 x 75, 56 % de la largeur
    ox, oy = (S - 89 * k) / 2, (S - 75 * k) / 2
    cx, cy, r = ox + 14.5 * k, oy + 49.5 * k, 14.5 * k
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill='#FFC300')
    d.polygon([(ox + x * k, oy + y * k) for x, y in one], fill='#FFFFFF')
    for n in (180, 192, 512):
        im.resize((n, n), Image.LANCZOS).save(os.path.join(out_dir, f'icone-{n}.png'))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
