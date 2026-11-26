/* ===== Version web (Netlify), Pro et perso : fenêtre « Vos fichiers » =====
   Sans Claude, l'outil ne peut pas enregistrer un fichier tout seul. Chaque fichier a donc un bouton
   « Enregistrer dans Photos » qui ouvre le menu de partage de l'iPhone (« Enregistrer la vidéo »,
   « Enregistrer l'image »). Ailleurs, ou si le partage est refusé : téléchargement classique.
   Inséré par les scripts de fabrication, dans le script principal (remplace showGallery). */
(() => {
  const extOf = b => { const t = (b && b.type) || ''; return /mp4/.test(t) ? 'mp4' : /quicktime/.test(t) ? 'mov' : /webm/.test(t) ? 'webm' : /png/.test(t) ? 'png' : 'jpg'; };
  const baseName = () => { try { return slug(); } catch(e){ return 'instantane'; } };
  const fileOf = (it, i, n) => new File([it.blob], `${baseName()}${n > 1 ? '_' + String(i + 1).padStart(2, '0') : ''}.${extOf(it.blob)}`,
    { type:(it.blob && it.blob.type) || (it.video ? 'video/mp4' : 'image/jpeg') });
  const canShare = fs => { try { return !!(navigator.share && navigator.canShare && navigator.canShare({ files:fs })); } catch(e){ return false; } };
  function download(f){
    const a = document.createElement('a'); a.href = URL.createObjectURL(f); a.download = f.name; a.style.display = 'none';
    document.body.append(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 8000);
  }
  function saveFiles(fs){ /* appelé directement par le toucher : le partage exige un geste de l'utilisateur */
    if (!canShare(fs)){ fs.forEach(download); return; }
    navigator.share({ files:fs }).catch(e => { if (!e || e.name !== 'AbortError') fs.forEach(download); });
  }
  window.__nlSave = saveFiles; /* pour les tests */
  showGallery = async function(items){
    const o = document.createElement('div'); o.className = 'overlay';
    const s = document.createElement('div'); s.className = 'sheet';
    const h = document.createElement('strong'); h.textContent = 'Vos fichiers'; h.style.fontSize = '20px';
    if (!items) items = await Promise.all([...Array(total()).keys()].map(async i => ({ blob:await pageBlob(i), video:false })));
    const files = items.map((it, i) => fileOf(it, i, items.length));
    const share = canShare(files.slice(0, 1)), hasVid = items.some(it => it.video);
    const p = document.createElement('p');
    p.textContent = share
      ? `Touchez « Enregistrer dans Photos », puis « ${hasVid ? 'Enregistrer la vidéo' : 'Enregistrer l’image'} » dans le menu qui s’ouvre.`
      : 'Touchez « Télécharger » pour enregistrer le fichier sur cet appareil.';
    s.style.textAlign = 'center';
    const kids = [h, p];
    if (items.length > 1){
      const all = document.createElement('button'); all.type = 'button'; all.className = 'primary';
      all.textContent = share && canShare(files) ? `Tout enregistrer dans Photos (${items.length})` : `Tout télécharger (${items.length})`;
      all.style.cssText = 'justify-self:center;text-align:center;justify-content:center;min-width:72%';
      all.onclick = () => saveFiles(files);
      kids.push(all);
    }
    const g = document.createElement('div'); g.style.cssText = 'display:grid;gap:14px;max-height:62vh;overflow:auto';
    items.forEach((it, i) => {
      const card = document.createElement('div'); card.style.cssText = 'display:grid;gap:10px;justify-items:center';
      const url = URL.createObjectURL(it.blob); let el;
      if (it.video){ el = document.createElement('video'); el.controls = true; el.playsInline = true; el.preload = 'metadata'; el.src = url + '#t=0.1'; }
      else { el = document.createElement('img'); el.alt = 'Page ' + (i + 1); el.src = url; }
      el.style.cssText = 'width:100%;max-height:46vh;object-fit:contain;border-radius:10px;background:#0003';
      const b = document.createElement('button'); b.type = 'button'; b.className = items.length > 1 ? '' : 'primary';
      b.textContent = (share ? 'Enregistrer dans Photos' : 'Télécharger') + (items.length > 1 ? ` (${i + 1})` : '');
      b.style.cssText = 'justify-self:center;text-align:center;justify-content:center;min-width:72%'; /* centré (demande d’Eric) */
      b.onclick = () => saveFiles([files[i]]);
      card.append(el, b); g.append(card);
    });
    kids.push(g);
    const close = document.createElement('button'); close.type = 'button'; close.textContent = 'Fermer'; close.style.cssText = 'text-align:center;justify-content:center;background:#fff;color:#14212A;border-color:#fff'; /* bouton blanc (demande d’Eric) */ close.onclick = () => o.remove();
    kids.push(close);
    s.append(...kids); o.append(s); o.onclick = e => { if (e.target === o) o.remove(); }; document.body.append(o);
  };
})();
