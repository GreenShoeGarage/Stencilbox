/* Small orthographic WebGL viewer for the SAME triangle mesh written to STL. */
(function(root){'use strict';
 class StencilViewer{
  constructor(canvas){this.canvas=canvas;this.gl=canvas.getContext('webgl',{antialias:true,alpha:true,preserveDrawingBuffer:true});this.software=!this.gl;if(this.software){this.ctx=canvas.getContext('2d');if(!this.ctx)throw Error('Canvas rendering is unavailable. Use the 2D preview.');}this.yaw=-.3;this.tilt=.85;this.zoom=1;this.pan=[0,0];this.model=null;this.active=false;this.drag=null;if(this.gl)this._init();
   canvas.addEventListener('pointerdown',e=>{if(e.button!==0&&e.button!==1)return;canvas.setPointerCapture(e.pointerId);this.drag={x:e.clientX,y:e.clientY,yaw:this.yaw,tilt:this.tilt,pan:[...this.pan],shift:e.shiftKey||e.button===1};});
   canvas.addEventListener('pointermove',e=>{if(!this.drag)return;const d=this.drag,dx=e.clientX-d.x,dy=e.clientY-d.y;if(d.shift){this.pan=[d.pan[0]+dx/this.canvas.clientWidth*2,d.pan[1]-dy/this.canvas.clientHeight*2];}else{this.yaw=d.yaw+dx*.008;this.tilt=Math.max(-PI,Math.min(PI,d.tilt+dy*.008));}this.draw();});
   const end=()=>{this.drag=null;};canvas.addEventListener('pointerup',end);canvas.addEventListener('pointercancel',end);canvas.addEventListener('wheel',e=>{e.preventDefault();this.zoomBy(Math.exp(-e.deltaY*.0015));},{passive:false});
   canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();this.lost=true;});canvas.addEventListener('webglcontextrestored',()=>{this.lost=false;this._init();if(this.model)this.setMesh(this.model,this.params);});
   this.observer=new ResizeObserver(()=>{if(this.active)this.draw();});this.observer.observe(canvas);
  }
  _init(){const gl=this.gl,compile=(type,src)=>{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error('3D shader compilation failed.');return s;};const vs=compile(gl.VERTEX_SHADER,`attribute vec3 aP;attribute vec3 aN;uniform vec3 center;uniform vec4 camera;uniform vec4 screen;uniform vec2 pan;varying float light;vec3 turn(vec3 v){float c=cos(camera.x),s=sin(camera.x);v=vec3(c*v.x-s*v.y,s*v.x+c*v.y,v.z);c=cos(camera.y);s=sin(camera.y);return vec3(v.x,c*v.y-s*v.z,s*v.y+c*v.z);}void main(){vec3 p=turn(aP-center);vec3 n=normalize(turn(aN));gl_Position=vec4(p.x*screen.x+pan.x,p.y*screen.y+pan.y,-p.z*screen.z,1.0);light=0.45+0.48*max(0.0,dot(n,normalize(vec3(-0.4,-0.6,1.0))))+0.12*max(0.0,dot(n,vec3(0.5,-0.6,-0.5)));}`),fs=compile(gl.FRAGMENT_SHADER,`precision mediump float;varying float light;void main(){vec3 color=vec3(0.54,0.71,0.35);gl_FragColor=vec4(color*light,1.0);}`);this.program=gl.createProgram();gl.attachShader(this.program,vs);gl.attachShader(this.program,fs);gl.linkProgram(this.program);if(!gl.getProgramParameter(this.program,gl.LINK_STATUS))throw Error('3D shader linking failed.');gl.deleteShader(vs);gl.deleteShader(fs);this.buffer=gl.createBuffer();this.uniforms={};for(const k of ['center','camera','screen','pan'])this.uniforms[k]=gl.getUniformLocation(this.program,k);this.locP=gl.getAttribLocation(this.program,'aP');this.locN=gl.getAttribLocation(this.program,'aN');}
  setMesh(m,p){this.model=m;this.params=p;const data=new Float32Array(m.faces.length*18);let i=0;for(const f of m.faces){const points=f.map(k=>m.vertices[k]),n=root.TraceEngine.normal(...points);for(const pt of points){data.set(pt,i);data.set(n,i+3);i+=6;}}const gl=this.gl;if(gl){gl.bindBuffer(gl.ARRAY_BUFFER,this.buffer);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);}this.faceNormals=m.faces.map(f=>root.TraceEngine.normal(...f.map(i=>m.vertices[i])));this.count=m.faces.length*3;if(this.active)this.draw();}
  draw(){if(!this.model||!this.active||this.lost)return;if(this.software){this.drawSoftware();return;}const gl=this.gl,c=this.canvas,dpr=Math.min(devicePixelRatio||1,2),w=Math.max(1,c.clientWidth),h=Math.max(1,c.clientHeight);if(c.width!==Math.round(w*dpr)||c.height!==Math.round(h*dpr)){c.width=Math.round(w*dpr);c.height=Math.round(h*dpr);}gl.viewport(0,0,c.width,c.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.useProgram(this.program);gl.bindBuffer(gl.ARRAY_BUFFER,this.buffer);gl.enableVertexAttribArray(this.locP);gl.enableVertexAttribArray(this.locN);gl.vertexAttribPointer(this.locP,3,gl.FLOAT,false,24,0);gl.vertexAttribPointer(this.locN,3,gl.FLOAT,false,24,12);const p=this.params,fit=Math.min((w-90)/p.width,(h-120)/p.height)*this.zoom;gl.uniform3f(this.uniforms.center,p.width/2,p.height/2,p.thickness/2);gl.uniform4f(this.uniforms.camera,this.yaw,this.tilt,0,0);gl.uniform4f(this.uniforms.screen,2*fit/w,2*fit/h,1/(Math.max(p.width,p.height)*2),0);gl.uniform2f(this.uniforms.pan,...this.pan);gl.drawArrays(gl.TRIANGLES,0,this.count);}
  drawSoftware(){
   // True depth-buffered 3D fallback. It renders the export triangles, not a 2D stand-in.
   const c=this.canvas,cssW=Math.max(1,c.clientWidth),cssH=Math.max(1,c.clientHeight),ratio=Math.min(1.25,1400/cssW,1000/cssH),w=Math.round(cssW*ratio),h=Math.round(cssH*ratio);
   if(c.width!==w||c.height!==h){c.width=w;c.height=h;}const image=this.ctx.createImageData(w,h),pix=image.data,depth=new Float32Array(w*h);depth.fill(-Infinity);
   const p=this.params,fit=Math.max(.01,Math.min((cssW-90)/p.width,(cssH-120)/p.height))*this.zoom*ratio,cy=Math.cos(this.yaw),sy=Math.sin(this.yaw),ct=Math.cos(this.tilt),st=Math.sin(this.tilt);
   const turn=v=>{const x=cy*v[0]-sy*v[1],y=sy*v[0]+cy*v[1];return[x,ct*y-st*v[2],st*y+ct*v[2]];};
   const verts=this.model.vertices.map(v=>{const q=turn([v[0]-p.width/2,v[1]-p.height/2,v[2]-p.thickness/2]);return[w/2+q[0]*fit+this.pan[0]*w/2,h/2-q[1]*fit-this.pan[1]*h/2,q[2]];});
   const light=[-.324443,-.486664,.811107];
   for(let fi=0;fi<this.model.faces.length;fi++){
    const f=this.model.faces[fi],a=verts[f[0]],b=verts[f[1]],d=verts[f[2]],den=(b[1]-d[1])*(a[0]-d[0])+(d[0]-b[0])*(a[1]-d[1]);if(Math.abs(den)<1e-9)continue;
    const x0=Math.max(0,Math.floor(Math.min(a[0],b[0],d[0]))),x1=Math.min(w-1,Math.ceil(Math.max(a[0],b[0],d[0]))),y0=Math.max(0,Math.floor(Math.min(a[1],b[1],d[1]))),y1=Math.min(h-1,Math.ceil(Math.max(a[1],b[1],d[1])));
    const n=turn(this.faceNormals[fi]),shade=.45+.48*Math.max(0,n[0]*light[0]+n[1]*light[1]+n[2]*light[2])+.12*Math.max(0,n[0]*.5-n[1]*.6-n[2]*.5),color=[138*shade,181*shade,89*shade];
    for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++){
     const px=x+.5,py=y+.5,u=((b[1]-d[1])*(px-d[0])+(d[0]-b[0])*(py-d[1]))/den,v=((d[1]-a[1])*(px-d[0])+(a[0]-d[0])*(py-d[1]))/den,k=1-u-v;if(u<-.00001||v<-.00001||k<-.00001)continue;
     const z=u*a[2]+v*b[2]+k*d[2],idx=y*w+x;if(z>depth[idx]){depth[idx]=z;const o=idx*4;pix[o]=color[0];pix[o+1]=color[1];pix[o+2]=color[2];pix[o+3]=255;}
    }
   }
   this.ctx.putImageData(image,0,0);
  }
  zoomBy(f){this.zoom=Math.max(.2,Math.min(8,this.zoom*f));this.draw();}
  fit(){this.zoom=1;this.pan=[0,0];this.draw();}
  iso(){this.yaw=-.3;this.tilt=.85;this.fit();}
 }
 const PI=Math.PI;root.StencilViewer=StencilViewer;
})(window);
