/* ===== Version web (Netlify) d'Instantané Pro =====
   Ce fichier est inséré par build_netlify.py à la fin de l'index.html de la version Claude.
   Aucun appel à Claude : les trois boutons qui appelaient Claude copient une demande
   que le journaliste colle dans son IA (ChatGPT, Claude, Le Chat...). La réponse revient
   par Import IA (bloc #ATELIER IA 1) ou par un simple coller (légende). */
(() => {
  const $ = id => document.getElementById(id);

  /* 5. brouillons protégés : le navigateur ne vide pas la base 'atelier-instantane-pro' quand il manque de place */
  try { if (navigator.storage && navigator.storage.persist) navigator.storage.persisted().then(p => p || navigator.storage.persist()).catch(() => {}); } catch(e){}

  /* ---------- copie dans le presse-papiers, avec une fenêtre de secours ---------- */
  function sheetCopy(text){
    const o = document.createElement('div'); o.className = 'overlay';
    const s = document.createElement('div'); s.className = 'sheet';
    const h = document.createElement('strong'); h.textContent = 'Demande pour votre IA'; h.style.fontSize = '20px';
    const p = document.createElement('p'); p.textContent = 'La copie automatique a été refusée. Touchez la case, choisissez « Tout sélectionner », puis « Copier ».';
    const ta = document.createElement('textarea'); ta.readOnly = true; ta.value = text; ta.rows = 10; ta.style.cssText = 'width:100%;font-size:16px;min-height:220px';
    const c = document.createElement('button'); c.type = 'button'; c.textContent = 'Fermer'; c.onclick = () => o.remove();
    s.append(h, p, ta, c); o.append(s); o.onclick = e => { if (e.target === o) o.remove(); }; document.body.append(o);
    setTimeout(() => { try { ta.focus(); ta.select(); } catch(e){} }, 50);
  }
  function copyIA(text, okMsg){
    window.__iaLastCopy = text; /* pour les tests */
    const fallback = () => {
      try {
        const ta = document.createElement('textarea'); ta.value = text; ta.readOnly = true;
        ta.style.cssText = 'position:fixed;left:-9999px;top:0;font-size:16px'; document.body.append(ta);
        ta.select(); ta.setSelectionRange(0, text.length);
        const ok = document.execCommand && document.execCommand('copy'); ta.remove();
        if (ok){ toast(okMsg); return; }
      } catch(e){}
      sheetCopy(text);
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(text).then(() => toast(okMsg), fallback); return; }
    } catch(e){}
    fallback();
  }

  /* ---------- règles communes ---------- */
  const FMT = `FORMAT DU BLOC (l’outil le lit automatiquement et refuse un bloc mal formé)
- Première ligne : #ATELIER IA 1
- Puis les sections demandées, chacune seule sur sa ligne, entre crochets, numérotées sans trou, avec une ligne vide entre deux sections.
- Une ligne par champ : « clé : valeur ». Clés en minuscules, sans accent, exactement celles indiquées. Aucune autre clé.
- Une valeur tient sur une seule ligne. Seul le champ « texte » de [WHATSAPP] et de [LEGENDE] peut avoir plusieurs paragraphes, séparés par une ligne vide ; aucune de ces lignes ne commence par un mot suivi de « : » ni par « [ ».
- Ni gras, ni puce, ni émoji. Information absente de l’article : clé omise, jamais inventée.
- couleur : 1 à 3 passages courts à mettre en couleur (noms propres, chiffres clés), séparés par « / », recopiés caractère pour caractère depuis le texte de la même section, sans ponctuation autour.
- Jamais de clé lieu : le journaliste choisit le lieu lui-même.
- Longueurs comptées espaces et ponctuation compris : un dépassement bloque l’outil. Compte avant de répondre.`;
  const TITRES = `[TITRE 1], [TITRE 2], [TITRE 3] : trois titres, trois angles différents, toujours sur l’information principale.
bande1 :
bande2 :
bande3 :
couleur :
Les trois bandes forment une seule phrase lue à la suite, sur trois lignes équilibrées : 30 caractères au plus chacune (vise 24), sans couper un nom propre ni un groupe nominal court, sans ponctuation finale. couleur : 1 ou 2 passages du titre.`;
  const VERB = `Règles des verbatims : mots exacts de la personne interrogée, dans leur ordre. Permis seulement : retirer les hésitations et tics de langage (euh, ben, hein), les bégaiements et les répétitions ; corriger l’orthographe et la ponctuation d’une transcription ; couper à une limite de phrase ; […] pour un passage retiré au milieu. Jamais de reformulation, de résumé, de mot ajouté ni de changement de temps ; créole gardé tel quel ; pas de guillemets autour. Jamais les questions du journaliste ni un propos rapporté au discours indirect. Chaque verbatim se comprend seul et commence par une phrase, jamais par la suite du précédent.`;
  const LEG = () => `[LEGENDE]
texte : la légende de publication pour Instagram et Facebook, 700 à 1 400 caractères, en paragraphes courts séparés par une ligne vide, sans liste. Première phrase factuelle, formulée autrement que les titres. Ni signature ni hashtag dans le texte.
hashtags : trois hashtags sans accent ni espace, séparés par une espace, dont la commune principale si elle est citée.`;
  const AUCUNE_REDONDANCE = '- Aucune redondance : titres, couverture, premier sous-titre et première phrase de la légende ont des formulations et des amorces différentes.';

  /* ---------- 1. « Préparer avec mon IA » (remplace « Créer la story ») ---------- */
  function prepPrompt(){
    const keep = $('keepTitle').checked && !$('keepWrap').hidden;
    const S = ['[COMMUN]\ndate : JJ/MM/AAAA, la date des faits ; clé omise si l’article n’en donne pas.'];
    let quoi = '';
    if (wa()){
      quoi = 'un visuel unique pour un post WhatsApp';
      S[0] += '\nthematique : la rubrique du sujet en 1 à 3 mots, 30 caractères au plus (ex. : Faits divers, Économie, Culture).';
      S.push(`[WHATSAPP]
titre : le titre à la une du visuel, informatif et fort, 130 caractères au plus (vise 80).
couleur : 1 à 3 passages du titre.
texte : une seule phrase de 100 caractères au plus, un second titre formulé autrement que le titre. Si l’article contient le lien de l’article publié, recopie-le à l’identique, seul sur une dernière ligne, après une ligne vide.`);
    } else if (car()){
      const n = imported.length > 1 ? imported.length : parseInt($('nPages').value, 10) || 5;
      quoi = `un carrousel Instagram de ${n} pages`;
      S.push(`[CARROUSEL 1] à [CARROUSEL ${n}] : exactement ${n} sections, chacune avec
texte :
couleur :
[CARROUSEL 1] est la couverture : titre à la une, 90 caractères au plus. Les suivantes : une information nouvelle par page, dans l’ordre du récit, 100 caractères au plus (vise 85), une phrase qui tient sur 3 lignes courtes ; la dernière page conclut (échéance, suite attendue ou chiffre clé). couleur : 1 à 3 passages du texte ; clé omise s’il n’y a ni nom ni chiffre marquant.`);
      S.push(LEG());
    } else if (vb()){
      const n = vbCount();
      quoi = 'une série de stories « verbatim » : une couverture avec le titre, puis une page par verbatim';
      if (!keep) S.push(TITRES);
      S.push(`[VERBATIM 1] à [VERBATIM ${n || 'n'}] : ${n ? `exactement ${n} verbatims, un par page, dans l’ordre de l’article` : 'les passages les plus forts, 6 au plus, un seul par personne de préférence, dans l’ordre de l’article'}, chacun avec
citation : 220 caractères au plus (vise 150 à 190), une seule idée, la phrase la plus forte.
couleur : 1 ou 2 passages courts de la citation (2 à 5 mots chacun).
nom : Prénom NOM (nom de famille en majuscules), 40 caractères au plus ; clé omise s’il n’est pas dans l’article.
fonction : sa fonction ou sa qualité, 90 caractères au plus ; clé omise si elle n’est pas dans l’article.
${VERB}
S’il n’y a pas assez de propos de personnes interrogées, rends seulement ceux qui existent.`);
      S.push(LEG());
    } else {
      const nN = story() ? (narrWanted() || 0) : 0;
      quoi = story() ? 'une story Instagram (format vertical) : un titre, puis des sous-titres qui racontent les faits' : 'un visuel unique (one-shot) pour Instagram';
      if (!keep) S.push(TITRES);
      if (story()) S.push(`[SOUS-TITRE 1] à [SOUS-TITRE ${nN || 8}] : ${nN ? `exactement ${nN} sous-titre${nN > 1 ? 's' : ''}` : '4 à 8 sous-titres'}, chacun avec
texte : une phrase factuelle complète, 100 caractères au plus (vise 85), qui fait avancer le récit dans l’ordre de l’article, sans répéter le titre.
couleur : 0 à 2 passages du texte (noms propres, chiffres clés) ; clé omise sinon.

[SYNTHE] : seulement si une personne interrogée est nommée dans l’article ; la personne principale.
nom : Prénom NOM, 40 caractères au plus, exactement comme dans l’article.
fonction : 60 caractères au plus, avec les mots exacts de l’article.

[GENERIQUE] : seulement si l’article nomme qui a fait les images ou le montage ; sinon, pas de section.
images :
montage :`);
      S.push(LEG());
    }
    const keepTxt = keep ? `\nLE TITRE EST DÉJÀ CHOISI par le journaliste et reste tel quel : « ${curTitle()} ». Ne rends aucune section [TITRE]. Écris le reste en cohérence avec ce titre.` : '';
    return `Tu es journaliste web à Guyane la 1ère. À partir de l’ARTICLE ci-dessous, prépare les textes de ${quoi}, pour l’outil Instantané Pro. Ta réponse sera collée dans l’Import IA de l’outil.

${RULES}${consignesBlock()}
${AUCUNE_REDONDANCE}${keepTxt}

${FMT}

SECTIONS À RENDRE, dans cet ordre
${S.join('\n\n')}

CE QUE TU RENDS : uniquement le bloc, qui commence par #ATELIER IA 1, dans un seul bloc de code, sans phrase avant ni après.

ARTICLE
${articleText()}`;
  }
  $('btnGen').onclick = () => {
    if ($('article').value.trim().length < 80){ status('Collez l’article ou vos informations brutes dans la case « Article ou informations brutes ».', 'err'); return; }
    copyIA(prepPrompt(), 'Demande copiée pour votre IA.');
    status('Demande copiée. Collez-la dans votre IA (ChatGPT, Claude, Le Chat…), puis collez sa réponse dans Import IA. Relisez avant de publier.', 'good');
  };

  /* ---------- 2. « Demander un autre titre à mon IA » (remplace « Affiner le titre avec Claude ») ---------- */
  function titlePrompt(ask){
    const src = articleText();
    const what = wa() ? 'le titre à la une de mon post WhatsApp (visuel unique)' : car() ? 'le titre à la une de la couverture de mon carrousel Instagram' : vb() ? 'le titre de la couverture de mes stories « verbatim »' : story() ? 'le titre de ma story Instagram (format vertical)' : 'le titre de mon visuel one-shot pour Instagram';
    /* carrousel : l’Import IA demande 2 pages au moins ; les pages suivantes sont recopiées telles quelles */
    const suite = car() && !wa() ? pages.slice(1).map((p, i) => ({ n:i + 2, t:String(p.text || '').trim(), h:String(p.hl || '').split('\n').map(x => x.trim()).filter(Boolean).join(' / ') })).filter(x => x.t && x.n <= 10) : [];
    const bloc = wa() ? `#ATELIER IA 1
[WHATSAPP]
titre : 130 caractères au plus (vise 80), informatif et fort.
couleur : 1 à 3 passages du titre.` : car() ? `#ATELIER IA 1
[CARROUSEL 1]
texte : 90 caractères au plus, informatif et fort.
couleur : 1 à 3 passages du texte.${suite.length ? `

${suite.map(x => `[CARROUSEL ${x.n}]\ntexte : ${x.t}${x.h ? `\ncouleur : ${x.h}` : ''}`).join('\n\n')}

Les sections [CARROUSEL 2] et suivantes sont les autres pages du carrousel : recopie-les caractère pour caractère, sans rien changer.` : ''}` : `#ATELIER IA 1
[TITRE 1]
bande1 :
bande2 :
bande3 :
couleur :
Les trois bandes forment une seule phrase lue à la suite, sur trois lignes équilibrées : 30 caractères au plus chacune (vise 24), sans couper un nom propre ni un groupe nominal court, sans ponctuation finale. couleur : 1 ou 2 passages du titre.`;
    const source = src ? 'ARTICLE\n' + src : 'SOURCE (aucun article collé : seuls ces textes du visuel sont utilisables comme faits)\n' + (car() ? pages.map(p => String(p.text || '').trim()).filter(Boolean).join('\n') : curTitle());
    return `Tu es journaliste web à Guyane la 1ère. Je veux un nouveau titre pour ${what}. Propose un titre qui applique ma demande.

${RULES}${consignesBlock()}
- Applique ma demande tant qu’elle respecte les règles de fond. Si elle suppose un fait absent de la source, n’invente rien : propose le meilleur titre possible avec les faits disponibles et dis-le.

TITRE ACTUEL
${curTitle() || '(vide)'}

MA DEMANDE
${ask || 'Un autre titre : autre formulation ou autre angle, toujours sur l’information principale.'}

${FMT}

CE QUE TU RENDS : une phrase courte qui dit ce que tu as changé, puis le bloc seul, dans un seul bloc de code :
${bloc}

${source}`;
  }
  $('btnRefine').onclick = () => {
    const ask = $('refineIn').value.trim();
    if (!articleText() && !curTitle()){ refineNote('Collez d’abord l’article, ou écrivez un premier titre.', 'err'); return; }
    copyIA(titlePrompt(ask), 'Demande de titre copiée.');
    refineNote('Demande copiée. Collez-la dans votre IA, puis collez son bloc dans Import IA pour remplacer le titre.', 'good');
    $('refineIn').value = '';
  };

  /* ---------- 3. Légende : « Copier la demande pour mon IA » (remplace « Générer ») ---------- */
  function capPrompt(){
    const fromPages = car() ? pages.map(p => p.text).filter(Boolean).join('\n') : [pages[0].b1, pages[0].b2, pages[0].b3].filter(Boolean).join(' ');
    const src = $('article').value.trim() || fromPages;
    const sig = String(settings.capSig || '').trim();
    const spec = wa() ? 'le texte du post WhatsApp : 400 à 900 caractères, en paragraphes courts séparés par une ligne vide, sans liste à puces ni émoji. Première phrase factuelle, formulée autrement que le titre du visuel. Ni signature ni hashtag.' : 'la légende de publication pour Instagram et Facebook : 700 à 1 400 caractères, en paragraphes courts séparés par une ligne vide, sans liste à puces ni émoji. Première phrase factuelle, formulée autrement que le titre du visuel. Ni signature ni hashtag dans les paragraphes.';
    const fin = [];
    if (sig && !wa()) fin.push(`puis, après une ligne vide, cette signature recopiée telle quelle : ${sig}`);
    if (!wa()) fin.push('puis, après une ligne vide, trois hashtags pertinents sur une seule ligne, séparés par une espace, sans accent ni espace dans un hashtag (ex. : #Guyane), dont la commune principale du sujet si elle est citée');
    return `Tu es journaliste web à Guyane la 1ère. Écris ${spec}

${RULES}${consignesBlock()}
Titre du visuel, à ne pas répéter en première phrase : ${car() ? (pages[0].text || '') : fromPages}

CE QUE TU RENDS : uniquement le texte, prêt à coller tel quel sous le post, sans guillemets, sans titre, sans phrase avant ni après : les paragraphes${fin.length ? ', ' + fin.join(', ') : ''}.

SOURCE
${src.slice(0, 30000)}`;
  }
  $('btnCapGen').onclick = () => {
    const fromPages = car() ? pages.map(p => p.text).filter(Boolean).join('\n') : [pages[0].b1, pages[0].b2, pages[0].b3].filter(Boolean).join(' ');
    if (!$('article').value.trim() && !fromPages.trim()){ toast('Collez d’abord l’article, ou écrivez le titre du visuel.'); return; }
    copyIA(capPrompt(), 'Demande copiée : collez-la dans votre IA, puis collez sa réponse dans la case « Texte sous le post ».');
  };

  /* pour les tests */
  window.__nl = { prepPrompt, titlePrompt, capPrompt };
})();
