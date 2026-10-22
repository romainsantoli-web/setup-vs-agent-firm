/**
 * Build de production sans dépendance : produit dist/ prêt pour un hébergement web
 * (GitHub Pages, Cloudflare Pages) ou un emballage TWA pour Google Play.
 * index.html du projet est un fragment (format Artifact) ; on l'entoure ici
 * d'un document HTML complet avec encodage, viewport et marges de sécurité.
 */
import { readFileSync, writeFileSync, rmSync, mkdirSync, cpSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dist = join(root, 'dist');
const fragment = readFileSync(join(root, 'index.html'), 'utf8');

const split = fragment.indexOf('<canvas id="bg"');
if (split < 0) throw new Error('index.html : marqueur <canvas id="bg"> introuvable');
const head = fragment.slice(0, split).trim();
const body = fragment.slice(split).trim();

const html = `<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>html{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
${head}
</head>
<body>
${body}
</body>
</html>
`;

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });
writeFileSync(join(dist, 'index.html'), html);
for (const p of ['src', 'styles', 'assets', 'manifest.webmanifest']) cpSync(join(root, p), join(dist, p), { recursive: true });
console.log(`dist/ prêt (${(html.length / 1024).toFixed(1)} Ko pour index.html)`);
