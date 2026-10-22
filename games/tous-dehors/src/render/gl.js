/** Utilitaires WebGL partagés. */
export function getGL(canvas, opts) {
  try { return canvas.getContext('webgl', opts) || canvas.getContext('experimental-webgl', opts) || null; } catch (e) { return null; }
}

export function linkProgram(gl, vsSrc, fsSrc) {
  const compile = (type, src) => {
    const s = gl.createShader(type);
    gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s) || 'shader');
    return s;
  };
  const p = gl.createProgram();
  gl.attachShader(p, compile(gl.VERTEX_SHADER, vsSrc));
  gl.attachShader(p, compile(gl.FRAGMENT_SHADER, fsSrc));
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p) || 'link');
  return p;
}

export function hexToRgb(h) {
  const n = parseInt(h.slice(1), 16);
  return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255];
}

/** Éclaircit (amt > 0) ou assombrit (amt < 0) une couleur hexadécimale. */
export function shade(h, amt) {
  const [r, g, b] = hexToRgb(h), t = amt > 0 ? 1 : 0, k = Math.abs(amt);
  const m = v => Math.round((v + (t - v) * k) * 255);
  return `rgb(${m(r)},${m(g)},${m(b)})`;
}
