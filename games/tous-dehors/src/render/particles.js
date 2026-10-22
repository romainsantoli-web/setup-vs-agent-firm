/**
 * Particules en WebGL (points) : traînées, étincelles, confettis.
 * Pool d'objets préalloué et tampon unique réutilisé : aucune allocation par image.
 * Coordonnées en pixels CSS de la fenêtre.
 */
import { getGL, linkProgram } from './gl.js';

export const SHAPE = Object.freeze({ glow: 0, confetti: 1, bead: 2 });
const STRIDE = 8;

const VS = `attribute vec4 a0;attribute vec4 a1;uniform vec2 uR;uniform float uD;varying vec4 vC;varying float vS;
void main(){vec2 p=a0.xy/uR*2.-1.;p.y=-p.y;gl_Position=vec4(p,0.,1.);gl_PointSize=a0.z*uD;vC=a1;vS=a0.w;}`;
const FS = `precision mediump float;varying vec4 vC;varying float vS;
void main(){vec2 d=gl_PointCoord-.5;float a;
if(vS<.5){a=smoothstep(.5,0.,length(d));a*=a;}
else if(vS<1.5){a=1.-smoothstep(.36,.5,max(abs(d.x),abs(d.y)*1.7));}
else{float r=length(d);a=1.-smoothstep(.42,.5,r);a=max(a*(.55+.45*smoothstep(.5,.1,r)),0.);}
gl_FragColor=vec4(vC.rgb*vC.a*a,vC.a*a);}`;

export function createParticles(canvas, { max = 2400 } = {}) {
  const gl = getGL(canvas, { antialias: false, alpha: true, premultipliedAlpha: true });
  let prog = null, buf = null, dpr = 1, live = 0, cursor = 0;
  const loc = {};
  if (gl) {
    try {
      prog = linkProgram(gl, VS, FS);
      buf = gl.createBuffer();
      loc.a0 = gl.getAttribLocation(prog, 'a0'); loc.a1 = gl.getAttribLocation(prog, 'a1');
      loc.uR = gl.getUniformLocation(prog, 'uR'); loc.uD = gl.getUniformLocation(prog, 'uD');
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    } catch (e) { prog = null; }
  }
  const ok = !!(gl && prog);
  const data = new Float32Array(max * STRIDE);
  const pool = Array.from({ length: max }, () => ({ on: false, x: 0, y: 0, vx: 0, vy: 0, life: 0, max: 1, size: 1, c: null, a: 1, shape: 0, g: 0, drag: 0, grow: 0, wob: 0 }));

  function emit(x, y, vx, vy, life, size, color, alpha = 1, shape = SHAPE.glow, grav = 0, drag = 0, grow = 0) {
    if (!ok || live >= max) return;
    for (let n = 0; n < max; n++) {
      const p = pool[cursor]; cursor = (cursor + 1) % max;
      if (p.on) continue;
      p.on = true; p.x = x; p.y = y; p.vx = vx; p.vy = vy; p.life = life; p.max = life; p.size = size;
      p.c = color; p.a = alpha; p.shape = shape; p.g = grav; p.drag = drag; p.grow = grow; p.wob = Math.random() * 6;
      live++; return;
    }
  }

  function update(dt) {
    if (!live) return;
    for (const p of pool) {
      if (!p.on) continue;
      p.life -= dt;
      if (p.life <= 0) { p.on = false; live--; continue; }
      const k = Math.max(0, 1 - p.drag * dt);
      p.vx *= k; p.vy = p.vy * k + p.g * dt;
      p.x += p.vx * dt; p.y += p.vy * dt; p.size += p.grow * dt; p.wob += dt * 9;
    }
  }

  function render() {
    if (!ok) return;
    gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
    if (!live) return;
    let n = 0;
    for (const p of pool) {
      if (!p.on) continue;
      const o = n * STRIDE, f = p.life / p.max;
      data[o] = p.x; data[o + 1] = p.y;
      data[o + 2] = Math.max(0, p.shape === SHAPE.confetti ? p.size * (0.6 + 0.4 * Math.abs(Math.sin(p.wob))) : p.size);
      data[o + 3] = p.shape;
      data[o + 4] = p.c[0]; data[o + 5] = p.c[1]; data[o + 6] = p.c[2];
      data[o + 7] = p.a * (p.shape === SHAPE.confetti ? Math.min(1, f * 3) : f);
      n++;
    }
    gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, data.subarray(0, n * STRIDE), gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(loc.a0); gl.vertexAttribPointer(loc.a0, 4, gl.FLOAT, false, STRIDE * 4, 0);
    gl.enableVertexAttribArray(loc.a1); gl.vertexAttribPointer(loc.a1, 4, gl.FLOAT, false, STRIDE * 4, 16);
    gl.uniform2f(loc.uR, innerWidth, innerHeight); gl.uniform1f(loc.uD, dpr);
    gl.drawArrays(gl.POINTS, 0, n);
  }

  return {
    ok,
    emit, update, render,
    resize() {
      dpr = Math.min(devicePixelRatio || 1, 2);
      canvas.width = Math.round(innerWidth * dpr); canvas.height = Math.round(innerHeight * dpr);
      if (ok) gl.viewport(0, 0, canvas.width, canvas.height);
    },
    clear() { for (const p of pool) p.on = false; live = 0; },
  };
}
