#!/usr/bin/env python3
"""Fabrique la version Netlify d'Instantané To Go (Atelier perso) à partir de la version Claude.

Usage : python3 build_netlify_perso.py SOURCE_DIR SORTIE_DIR
  SOURCE_DIR : dossier qui contient l'index.html du perso, son logo.png et son dossier accueil/
  SORTIE_DIR : dossier publié sur Netlify (index.html, logo.png, accueil/, manifest.webmanifest, icônes)

Même principe que build_netlify.py (Pro), validé par Eric le 25 novembre 2026 :
 1. « Créer » devient « Préparer avec mon IA » (copie l'article et la consigne du bloc Import IA, clés du perso)
 2. « Affiner avec Claude » devient « Demander un autre titre à mon IA »
 3. Légende : « Générer » devient « Copier la demande pour mon IA »
 4. Import IA inchangé
 5. navigator.storage.persist() au démarrage
 6. manifeste et icône (logo d'Eric sur le bleu de l'accueil) pour l'écran d'accueil de l'iPhone
 Pas de bouton Aide : le guide en ligne est celui du Pro.
 Aucun appel à window.claude dans la copie. Chaque remplacement est vérifié.
"""
import os, re, shutil, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
NOM = 'Instantané To Go'
BLEU = '#255F8E'   # --main de la page d'accueil du perso
FOND = '#FBF6EE'   # --bg de la page d'accueil du perso


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
            f'<meta name="apple-mobile-web-app-title" content="{NOM}">'
            '<meta name="apple-mobile-web-app-status-bar-style" content="default">'
            f'<meta name="theme-color" content="{FOND}">')
    s = rep(s, '<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">', head)

    # 1. Article source et génération
    s = rep(s, 'Claude n’utilise que ces faits.', 'Votre IA n’utilisera que ces faits.')
    s = rep(s, '<button id="btnGen" class="primary" type="button">Créer le carrousel</button>',
               '<button id="btnGen" class="primary" type="button">Préparer avec mon IA</button>')
    s = rep(s, "$('btnGen').textContent = 'Créer ' + LE[mode];", "$('btnGen').textContent = 'Préparer avec mon IA';")
    s = rep(s, 'Garder le titre : Claude ne réécrit que le reste', 'Garder le titre : votre IA ne réécrit que le reste')
    s = rep(s, r"\n  status\(vb\(\) \? 'Claude écrit la thématique[^\n]*\n",
               "\n  status('L’application copie l’article et la consigne : collez-les dans votre IA, puis collez sa réponse dans Import IA. Relisez avant de publier.');\n",
               regex=True)
    s = rep(s, 'Collez l’article, puis « Créer le carrousel ».', 'Collez l’article, puis « Préparer avec mon IA ».')
    s = rep(s, 'ou collez l’article puis « Créer la story ».', 'ou collez l’article puis « Préparer avec mon IA ».')
    s = rep(s, 'Collez l’article, puis « Créer ${LE[mode]} ».', 'Collez l’article, puis « Préparer avec mon IA ».')

    # 2. Demander un autre titre à mon IA
    s = rep(s, '<strong style="font-size:16px" id="refineTitle">Affiner le titre avec Claude</strong>\n            <ol class="chat" id="refineLog" aria-live="polite"></ol>',
               '<strong style="font-size:16px;display:none" id="refineTitle">Demander un autre titre à mon IA</strong>\n'
               '            <p class="note" id="refineHelp" style="margin:0">Touchez un bouton ou écrivez votre demande : elle est copiée avec le titre actuel. Collez-la dans votre IA, puis collez son bloc dans Import IA.</p>\n'
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
    s = rep(s, r"sAff\.title\(shown\(\$\('refine'\)\) \? [^;]*;",
               "sAff.title('Demander un autre titre à mon IA');", regex=True)

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
    s = rep(s, '#home .hTop{display:flex;', '#txBox{display:none!important}\n#home .hTop{display:flex;')

    # 1, 2, 3, 5 : le code de la version web, à la fin du script principal
    js = open(os.path.join(HERE, 'netlify-ia-perso.js'), encoding='utf-8').read()
    fin = "addEventListener('resize', () => setTimeout(() => { try { addUI(); } catch(e){} }, 30));\n}\n"
    s = rep(s, fin + '})();\n</script>', fin + js + '})();\n</script>')

    if 'window.claude' in s:
        sys.exit('ÉCHEC : il reste un appel à window.claude.')
    if '—' in js:
        sys.exit('ÉCHEC : tiret cadratin dans le code ajouté.')

    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(s)
    shutil.copy(os.path.join(src_dir, 'logo.png'), os.path.join(out_dir, 'logo.png'))
    if os.path.isdir(os.path.join(out_dir, 'accueil')):
        shutil.rmtree(os.path.join(out_dir, 'accueil'))
    shutil.copytree(os.path.join(src_dir, 'accueil'), os.path.join(out_dir, 'accueil'))

    manifest = {
        'name': NOM, 'short_name': 'To Go', 'lang': 'fr',
        'start_url': './', 'scope': './', 'display': 'standalone',
        'background_color': FOND, 'theme_color': FOND,
        'icons': [{'src': 'icone-192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': 'icone-512.png', 'sizes': '512x512', 'type': 'image/png'},
                  {'src': 'icone-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]}
    open(os.path.join(out_dir, 'manifest.webmanifest'), 'w', encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False, indent=2))
    icons(src_dir, out_dir)
    print('Version Netlify du perso prête :', out_dir)


def icons(src_dir, out_dir):
    """Icône : le logo d'Eric (logo.png, blanc) au centre, sur le bleu de l'accueil du perso."""
    from PIL import Image
    S = 2048
    im = Image.new('RGBA', (S, S), BLEU)
    lg = Image.open(os.path.join(src_dir, 'logo.png')).convert('RGBA')
    w = int(S * 0.54); h = round(lg.height * w / lg.width)
    lg = lg.resize((w, h), Image.LANCZOS)
    im.alpha_composite(lg, ((S - w) // 2, (S - h) // 2))
    im = im.convert('RGB')
    for n in (180, 192, 512):
        im.resize((n, n), Image.LANCZOS).save(os.path.join(out_dir, f'icone-{n}.png'))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
