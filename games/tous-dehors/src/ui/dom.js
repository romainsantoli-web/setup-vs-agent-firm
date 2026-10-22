/** Petits utilitaires d'interface : sélection, fenêtres, toasts, pub simulée. */
export const $ = s => document.querySelector(s);
export const $$ = s => Array.from(document.querySelectorAll(s));

export const esc = s => String(s).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));

export function openModal(html, onAction) {
  const box = $('#modalBox');
  box.innerHTML = html;
  $('#modal').hidden = false;
  box.onclick = e => { const b = e.target.closest('[data-act]'); if (b) onAction(b.dataset.act, b); };
  const first = box.querySelector('button');
  if (first) setTimeout(() => first.focus({ preventScroll: true }), 60);
}
export const closeModal = () => { $('#modal').hidden = true; };

let toastTimer = 0;
export function toast(text) {
  const el = $('#toast');
  el.textContent = text; el.hidden = false;
  clearTimeout(toastTimer); toastTimer = setTimeout(() => { el.hidden = true; }, 2200);
}

/** Pub simulée : 5 secondes avant de pouvoir fermer ou récupérer la récompense. */
export function showAd({ reward, ad, onDone }) {
  $('#adBody').innerHTML = `${esc(ad[0])}<small>${esc(ad[1])}</small>`;
  $('#ad').hidden = false;
  const btn = $('#adBtn'); btn.disabled = true;
  let t = 5;
  const label = () => {
    btn.textContent = t > 0 ? (reward ? `Récompense dans ${t} s` : `Fermer dans ${t} s`) : (reward ? `Récupérer ${reward}` : 'Fermer ✕');
  };
  label();
  const iv = setInterval(() => { t--; label(); if (t <= 0) { clearInterval(iv); btn.disabled = false; } }, 1000);
  btn.onclick = () => { $('#ad').hidden = true; onDone(); };
}

export async function copyText(text, fallbackEl) {
  try { await navigator.clipboard.writeText(text); return true; } catch (e) { if (fallbackEl) fallbackEl.select(); return false; }
}
