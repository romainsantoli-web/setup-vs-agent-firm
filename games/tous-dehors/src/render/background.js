/**
 * Fond animé en WebGL : dégradé et halos lumineux qui dérivent lentement.
 * Rendu à demi-résolution et une image sur deux pour économiser la batterie.
 * Sans WebGL, un dégradé CSS prend le relais.
 */
import { getGL, linkProgram, hexToRgb } from './gl.js';

const FS = `precision mediump float;
uniform vec2 uR;uniform float uT,uP;uniform vec3 c1,c2,c3,c4;
float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
void main(){vec2 uv=gl_FragCoord.xy/uR;float ar=uR.x/uR.y;vec2 q=vec2(uv.x*ar,uv.y);float t=uT*.06;
vec3 col=mix(c1,c2,smoothstep(-.1,1.1,uv.y+.12*sin(uv.x*3.1+t*3.)));
for(int i=0;i<4;i++){float f=float(i);vec2 c=vec2(ar*(.5+.42*sin(t*(1.2+f*.37)+f*2.1)),.5+.4*cos(t*(1.05+f*.29)+f*1.7));
float d=length(q-c);vec3 bc=mod(f,2.)<.5?c3:c4;col+=bc*(.16+.05*f)*smoothstep(.8,0.,d)*(1.+uP*1.2);}
col*=1.-.42*length(uv-vec2(.5,.55));col+=(h(gl_FragCoord.xy+fract(uT))-.5)*.03;gl_FragColor=vec4(col,1.);}`;

export function createBackground(canvas) {
  const gl = getGL(canvas, { antialias: false, alpha: false, powerPreference: 'low-power' });
  let prog = null, pulse = 0;
  const loc = {};
  if (gl) {
    try {
      prog = linkProgram(gl, 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}', FS);
      gl.useProgram(prog);
      gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
      const p = gl.getAttribLocation(prog, 'p');
      gl.enableVertexAttribArray(p); gl.vertexAttribPointer(p, 2, gl.FLOAT, false, 0, 0);
      for (const n of ['uR', 'uT', 'uP', 'c1', 'c2', 'c3', 'c4']) loc[n] = gl.getUniformLocation(prog, n);
    } catch (e) { prog = null; }
  }
  const ok = !!(gl && prog);

  return {
    ok,
    resize() {
      if (!ok) return;
      const s = 0.5 * Math.min(devicePixelRatio || 1, 2);
      canvas.width = Math.max(2, Math.round(innerWidth * s));
      canvas.height = Math.max(2, Math.round(innerHeight * s));
      gl.viewport(0, 0, canvas.width, canvas.height);
    },
    setTheme(theme) {
      if (!ok) { document.body.style.background = `radial-gradient(120% 80% at 50% 30%, ${theme.bg[1]}, ${theme.bg[0]})`; return; }
      gl.useProgram(prog);
      ['c1', 'c2', 'c3', 'c4'].forEach((n, i) => gl.uniform3fv(loc[n], hexToRgb(theme.bg[i])));
    },
    pulse(v) { pulse = Math.max(pulse, v); },
    render(time, dt) {
      pulse = Math.max(0, pulse - dt * 1.6);
      if (!ok) return;
      gl.uniform2f(loc.uR, canvas.width, canvas.height);
      gl.uniform1f(loc.uT, time); gl.uniform1f(loc.uP, pulse);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    },
  };
}
