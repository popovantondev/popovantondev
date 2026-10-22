// Reconstruct the display and keyboard as two hinged planes. The original
// photograph supplies their textures, so the reference proportions are kept.
const {chromium}=require('playwright');
const sharp=require('sharp');
const fs=require('fs');
const path=require('path');
const folder=path.resolve(__dirname,'../assets/banner-sources');
const uri=name=>'data:image/webp;base64,'+fs.readFileSync(path.join(folder,name)).toString('base64');

(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:340,height:360},deviceScaleFactor:2});
  for(const lang of ['ru','de','en'])for(const device of ['mac','windows']){
   if(device==='mac'&&lang!=='ru')continue;
   await page.setContent('<style>html,body{margin:0;background:transparent;width:340px;height:360px}canvas{width:340px;height:360px;display:block}</style><canvas width="680" height="720"></canvas>');
   await page.evaluate(async({device,laptop,peak,quick})=>{
    const load=src=>new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=reject;i.src=src;});
    const images=await Promise.all([load(laptop),load(peak),load(quick)]);
    const atlas=document.createElement('canvas');atlas.width=720;atlas.height=480;
    const paint=atlas.getContext('2d');paint.drawImage(images[0],0,0,720,480);
    const windows=device==='windows';
    if(windows){
     paint.fillStyle='#101a2d';paint.fillRect(382,94,310,204);
     const fit=(im,x,y,w,h)=>{const s=Math.min(w/im.width,h/im.height);paint.drawImage(im,x+(w-im.width*s)/2,y+(h-im.height*s)/2,im.width*s,im.height*s);};
     fit(images[1],388,98,128,196);fit(images[2],524,98,160,196);
    }
    const gl=document.querySelector('canvas').getContext('webgl',{alpha:true,antialias:true,premultipliedAlpha:false,preserveDrawingBuffer:true});
    if(!gl)throw Error('WebGL renderer unavailable');
    const vertex=`attribute vec3 position;attribute vec2 uv;uniform mat3 textureProjection;uniform float yaw;varying vec3 tex;varying vec2 face;
    void main(){float pitch=radians(25.0);vec3 p=vec3(cos(yaw)*position.x+sin(yaw)*position.z,position.y,-sin(yaw)*position.x+cos(yaw)*position.z);
    float vy=cos(pitch)*p.y-sin(pitch)*p.z;float vz=sin(pitch)*p.y+cos(pitch)*p.z;float w=2500.0-vz;
    gl_Position=vec4((2.0*170.0/340.0-1.0)*w+2.0*0.8*2500.0*p.x/340.0,(1.0-2.0*235.0/360.0)*w+2.0*0.8*2500.0*vy/360.0,0.0,w);tex=textureProjection*vec3(uv,1.0);face=uv;}`;
    const fragment='precision highp float;uniform sampler2D photo;uniform vec4 surface;varying vec3 tex;varying vec2 face;void main(){vec4 c=texture2D(photo,tex.xy/tex.z);vec2 q=abs(face-0.5)-vec2(0.482);float edge=length(max(q,0.0))+min(max(q.x,q.y),0.0)-0.018;c.a=smoothstep(0.75,0.98,c.a)*(1.0-smoothstep(-0.004,0.0,edge));if(surface.a>0.0)c=vec4(mix(surface.rgb*0.72,surface.rgb,face.y),c.a);gl_FragColor=c;}';
    function shader(kind,code){const s=gl.createShader(kind);gl.shaderSource(s,code);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
    const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
    gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.enable(gl.BLEND);gl.blendFuncSeparate(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA,gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
    const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,atlas);
    gl.uniform1f(gl.getUniformLocation(program,'yaw'),(windows?-8:8)*Math.PI/180);
    function matrix(q){
     const [p0,p1,p2,p3]=q.map(([x,y])=>[x/720,y/480]);
     const dx1=p1[0]-p2[0],dx2=p3[0]-p2[0],dx3=p0[0]-p1[0]+p2[0]-p3[0];
     const dy1=p1[1]-p2[1],dy2=p3[1]-p2[1],dy3=p0[1]-p1[1]+p2[1]-p3[1];
     const det=dx1*dy2-dx2*dy1,g=(dx3*dy2-dx2*dy3)/det,h=(dx1*dy3-dx3*dy1)/det;
     return new Float32Array([p1[0]-p0[0]+g*p1[0],p1[1]-p0[1]+g*p1[1],g,p3[0]-p0[0]+h*p3[0],p3[1]-p0[1]+h*p3[1],h,p0[0],p0[1],1]);
    }
    function panel(points,photoQuad,solid=null){
     gl.uniform4fv(gl.getUniformLocation(program,'surface'),solid||[0,0,0,0]);
     const indices=[0,1,2,0,2,3],coords=[[0,0],[1,0],[1,1],[0,1]];
     for(const [name,size,values] of [['position',3,indices.flatMap(i=>points[i])],['uv',2,indices.flatMap(i=>coords[i])]]){
      const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values),gl.STATIC_DRAW);const attr=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(attr);gl.vertexAttribPointer(attr,size,gl.FLOAT,false,0,0);
     }
     gl.uniformMatrix3fv(gl.getUniformLocation(program,'textureProjection'),false,matrix(photoQuad));gl.drawArrays(gl.TRIANGLES,0,6);
    }
    const pitch=25*Math.PI/180,H=228,W=windows?336:330;
    // A visible aluminum front and side give the MacBook a Pro-like base.
    if(!windows){
     const metal=[0.77,0.79,0.82,1],quad=[[44,391],[335,391],[335,402],[44,402]];
     panel([[-W/2,0,0],[-W/2,0,230],[-W/2,-11,230],[-W/2,-11,0]],quad,metal);
     panel([[-W/2,0,230],[W/2,0,230],[W/2,-11,230],[-W/2,-11,230]],quad,metal);
    }
    // Keyboard remains horizontal; display leans back by the original view angle.
    panel([[-W/2,0,0],[W/2,0,0],[W/2,0,230],[-W/2,0,230]],windows?[[369,307],[704,307],[719,416],[361,416]]:[[31,306],[360,306],[352,411],[5,409]]);
    panel([[-W/2,H*Math.cos(pitch),-H*Math.sin(pitch)],[W/2,H*Math.cos(pitch),-H*Math.sin(pitch)],[W/2,0,0],[-W/2,0,0]],windows?[[369,80],[703,80],[704,307],[368,307]]:[[31,79],[360,79],[360,307],[31,307]]);
    gl.finish();
   },{device,laptop:uri('laptops.webp'),peak:uri('peakmp3-'+lang+'.webp'),quick:uri('quickanswer-'+lang+'.webp')});
   const png=await page.screenshot({omitBackground:true});
   const name=device==='mac'?'mac-spatial.webp':'windows-spatial-'+lang+'.webp';
   await sharp(png).webp({quality:94,effort:6}).toFile(path.join(folder,name));console.log(name);
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
