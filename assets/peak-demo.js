/* PeakMP3 demo for the "Über mich" pages.
   Copy of PeakMP3/website/demo.js with minimal changes: images, VU timelines and button sounds load
   from assets/about/peak/ (own files, converted to WebP; before, 19 images and all timelines were fetched
   from the published PeakMP3 site on every visit and one failed request disabled the whole demo).
   The music clips (24 s, about 1 MB each, 33 files) still come from the published PeakMP3 site, with two retries.
   The language comes from #demo[data-lang], the VU reference stays in memory (no browser storage),
   the export link is kept (the hidden #demo-export link is created here, the hotspot of the button clicks it), the language buttons open the about pages, CSS classes use the peak- prefix,
   and everything starts only when #demo comes near the viewport.
   The audio and VU timelines are rendered by the unmodified Windows engine.
   This page only plays the selected example and draws its physical controls. */
(()=>{
const BASE='assets/about/peak/';
const AUDIO='https://popovantondev.github.io/PeakMP3/music/';
let retries=0;
const section=document.querySelector('#demo');if(!section)return;
const start=()=>(async()=>{
 const canvas=document.querySelector('#peak-demo');if(!canvas)return;
 const s=JSON.parse(document.querySelector('#demo-strings').textContent),audio=document.querySelector('#demo-audio'),ctx=canvas.getContext('2d');
 const range=document.querySelector('#density-range'),volumeRange=document.querySelector('#demo-volume'),status=document.querySelector('#demo-state'),playButton=document.querySelector('#demo-play');
 const lang=section.dataset.lang;
 const names=['turntable_plate','arm-base','arm-moving','spindle',...['base-'+lang,'knob','transport','comparison','volume','speaker','presets-'+lang,'caption-'+lang,'file-'+lang,'queue-'+lang,'export-'+lang,'label-techno','label-electronic','label-pop'].map(x=>'native/'+x)];
 const load=name=>new Promise((resolve,reject)=>{let tries=0;const im=new Image();im.onload=()=>{const done=()=>resolve([name,im]);if(im.decode){im.decode().then(done,done);}else done();};im.onerror=()=>{if(tries++<1){im.src=BASE+'img/'+name+'.webp?r=1';}else reject(Error('Image unavailable: '+name));};im.src=BASE+'img/'+name+'.webp';});
 const [pairs,tracks]=await Promise.all([Promise.all(names.map(load)),fetch(BASE+'music/tracks.json').then(r=>{if(!r.ok)throw Error('Tracks unavailable');return r.json();})]);
 const art=Object.fromEntries(pairs),timelineCache=new Map();let trackIndex=0,density=7,mode='b',volume=60,selection=0,meter=null,drag=null,frame=0,last=0,angle=0,speed=0,arm=-16,lift=1,pendingSeek=0,visible=true,loading=false,hover='';
 let reference=0,previousVolume=60,transportState=0;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 audio.volume=volume/100;audio.loop=false;
 const track=()=>tracks[trackIndex],strength=()=>mode==='a'?0:density;
 const position=()=>Math.min(24,Math.max(0,audio.currentTime||0));
 function clipUrl(){return AUDIO+track().id+'/density-'+strength()+'.mp3';}
 function setStatus(text){status.textContent=text;}
 const exportLink=document.createElement('a');exportLink.id='demo-export';exportLink.hidden=true;exportLink.target='_blank';exportLink.rel='noopener';exportLink.tabIndex=-1;exportLink.setAttribute('aria-hidden','true');section.append(exportLink);
 async function selectClip(keepTime=true){
  const id=++selection,playing=!audio.paused;pendingSeek=keepTime?position():0;audio.pause();retries=0;audio.src=clipUrl();audio.load();loading=true;setStatus(s.loading);updateControls();
  const key=track().id+'/'+strength();
  try{if(!timelineCache.has(key))timelineCache.set(key,fetch(BASE+'music/'+key.replace('/','/density-')+'.json').then(r=>{if(!r.ok)throw Error('Timeline unavailable');return r.json();}));
   const data=await timelineCache.get(key);if(id!==selection)return;meter=data;loading=false;setStatus(s.ready);if(playing)await audio.play();draw();schedule();
  }catch(e){if(id===selection){loading=false;setStatus(s.error);updateControls();}}
 }
 audio.addEventListener('loadedmetadata',()=>{if(pendingSeek>0)audio.currentTime=Math.min(pendingSeek,audio.duration||24);pendingSeek=0;});
 audio.addEventListener('play',()=>{updateControls();setStatus(s.ready);schedule();});audio.addEventListener('pause',()=>{updateControls();schedule();});
 audio.addEventListener('error',()=>{if(!audio.currentSrc)return;if(retries++<2){setTimeout(()=>{if(audio.error)audio.load();},700*retries);return;}setStatus(s.error);});
 audio.addEventListener('ended',()=>changeTrack((trackIndex+1)%tracks.length,true));
 async function toggle(){if(loading)return;try{if(audio.paused){transportState=1;await audio.play();}else {transportState=2;audio.pause();}}catch(e){setStatus(s.error);}schedule();}
 function stop(){transportState=0;audio.pause();audio.currentTime=0;pendingSeek=0;updateControls();schedule();}
 async function changeTrack(index,autoplay=false){const wasPlaying=!audio.paused||autoplay;audio.pause();trackIndex=index;pendingSeek=0;await selectClip(false);if(wasPlaying&&!loading)try{await audio.play();}catch(e){setStatus(s.error);}updateControls();schedule();}
 function updateControls(){range.value=density;volumeRange.value=volume;document.querySelector('#density-number').value=density;document.querySelectorAll('[data-compare]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.compare===mode)));document.querySelectorAll('[data-track]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.track===track().id)));playButton.textContent=(audio.paused?'▶ ':'Ⅱ ')+(audio.paused?s.play:s.pause);playButton.setAttribute('aria-pressed',String(!audio.paused));exportLink.href=clipUrl();exportLink.download=track().title+' - PeakMP3 '+strength()+'.mp3';draw();}
 const sounds=[0,1,2].map(i=>{const a=new Audio(BASE+'sound/sound-'+i+'.wav');a.preload='auto';return a;});let lastSound=0;function sound(i){if(i===1&&performance.now()-lastSound<24)return;lastSound=performance.now();sounds[i].currentTime=0;sounds[i].play().catch(()=>{});}
 let densityTimer;
 function setDensity(value,delay=false){const next=Math.max(0,Math.min(10,Math.round(value)));if(next!==density)sound(1);density=next;updateControls();clearTimeout(densityTimer);if(delay)densityTimer=setTimeout(()=>selectClip(),140);else selectClip();}
 function setVolume(value){volume=Math.max(0,Math.min(100,Math.round(value)));audio.volume=volume/100;updateControls();}
 function schedule(){if(!frame&&visible&&!document.hidden&&(!audio.paused||speed>.01||Math.abs(arm+16)>.02||lift<.99))frame=requestAnimationFrame(tick);}
 function approach(a,b,n){return a<b?Math.min(b,a+n):Math.max(b,a-n);}
 let phase='parked',motionTrack='',previousProgress=0,returnFirst=false;
 function tick(now){frame=0;const dt=Math.min(.1,(now-(last||now))/1000);last=now;const requested=!audio.paused,progress=position()/24,key=track().id;
  if(key!==motionTrack){motionTrack=key;returnFirst=true;phase='lifting';}if(requested&&Math.abs(progress-previousProgress)>.035&&phase==='tracking')phase='lifting-seek';previousProgress=progress;
  speed=approach(speed,requested?200:0,(requested?420:360)*dt);if(!reduced)angle=(angle+speed*dt)%360;
  if(!requested&&!['parked','lifting','returning'].includes(phase))phase='lifting';if(phase==='parked'&&requested){returnFirst=false;phase='positioning';}
  if(phase==='lifting'||phase==='lifting-seek'){lift=approach(lift,1,7*dt);if(lift>=1)phase=phase==='lifting-seek'&&requested&&!returnFirst?'positioning':'returning';}
  else if(phase==='returning'){arm=approach(arm,-16,80*dt);if(arm<=-16){returnFirst=false;phase=requested?'positioning':'parked';}}
  else if(phase==='positioning'){const target=5+19*progress;arm=approach(arm,target,85*dt);if(Math.abs(arm-target)<.01)phase='lowering';}
  else if(phase==='lowering'){lift=approach(lift,0,6*dt);if(lift<=0)phase='tracking';}else if(phase==='tracking'){arm=approach(arm,5+19*progress,30*dt);lift=0;}draw();schedule();}
 function needleEnd(db){const labels=[-20,-10,-7,-5,-3,-2,-1,0,1,2,3],points=[[155,310],[232,258],[307,234],[367,218],[447,210],[489,213],[543,219],[604,234],[663,260],[720,290],[783,322]];db=Math.max(-20,Math.min(3,db));let i=0;while(i<labels.length-2&&db>labels[i+1])i++;const f=(10**(db/20)-10**(labels[i]/20))/(10**(labels[i+1]/20)-10**(labels[i]/20));return [points[i][0]+(points[i+1][0]-points[i][0])*f,points[i][1]+(points[i+1][1]-points[i][1])*f];}
 function patch(x,y,w,h){ctx.drawImage(art.turntable_plate,x,y,w,h,x,y,w,h);}
 function sprite(name,index,x,y,w,h,cols){const im=art['native/'+name];ctx.drawImage(im,(index%cols)*w,Math.floor(index/cols)*h,w,h,x,y,w,h);}
 let calibrated=null,calibrationKey='';
 function vu(){if(audio.paused||!meter)return -20;if(reference===0)return meter.vu[Math.min(meter.vu.length-1,Math.floor(position()*meter.fps))];
  const key=selection+':'+reference;if(calibrationKey!==key){calibrationKey=key;const channels=[{level:0,target:0,delta:0},{level:0,target:0,delta:0}],f=Math.fround,gain=10**(-reference/20);calibrated=(meter.peaks||[]).map(pair=>{for(let n=0;n<2;n++){const c=channels[n],peak=f(Math.max(.1,Math.min(1.4125375747680664,pair[n]*gain))),epsilon=f(Math.max(1,Math.min(Math.abs(peak),Math.abs(c.target)))*f(.0001));if(Math.abs(peak-c.target)>epsilon){c.target=peak;c.delta=f(Math.exp(peak-1)*(peak<c.level?-f(.05):f(.1)));}c.level=c.delta>0?Math.min(f(c.level+c.delta),c.target):Math.max(f(c.level+c.delta),c.target);}return Math.max(-20,Math.min(3,20*Math.log10(Math.max(channels[0].level,channels[1].level))));});}
  return calibrated[Math.min(calibrated.length-1,Math.floor(position()*meter.fps))]??-20;
 }
 function draw(){if(!ctx||!art.turntable_plate)return;ctx.setTransform(canvas.width/973,0,0,canvas.height/1616,0,0);ctx.clearRect(0,0,973,1616);ctx.drawImage(art['native/base-'+lang],0,0,973,1616);
  patch(65,190,841,277);const end=needleEnd(vu());ctx.lineCap='round';for(const [color,width,a,b] of [['rgba(92,44,25,.255)',6,[482,437],[end[0]+1,end[1]+2]],['#e04225',3.8,[481,435],end],['#ffb191',1,[480.7,434.7],[end[0]-.3,end[1]-.3]]]){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke();}
  ctx.save();ctx.beginPath();ctx.moveTo(355,465);ctx.bezierCurveTo(415,377,550,377,610,465);ctx.closePath();ctx.clip();ctx.drawImage(art.turntable_plate,0,0,973,1616);ctx.restore();
  [[50,529,2],[50,667,5],[726,529,8],[726,667,10]].forEach(([x,y,value],i)=>sprite('presets-'+lang,i*2+(density===value?1:0),x,y,194,102,8));
  sprite('knob',density,342,524,278,278,11);sprite('caption-'+lang,density,280,799,403,42,11);sprite('file-'+lang,trackIndex,174,859,728,88,3);
  patch(55,954,863,99);const p=position(),wave=meter?.wave||[],maximum=Math.max(.001,...wave);ctx.lineWidth=3;ctx.lineCap='round';for(let x=0;x<820;x+=5){let peak=0;for(let i=Math.floor(x*wave.length/820);i<Math.min(wave.length,Math.floor((x+5)*wave.length/820)+1);i++)peak=Math.max(peak,wave[i]);const h=Math.max(1,peak/maximum*25);ctx.strokeStyle=x/820<p/24?'#cb772f':'#918875';ctx.beginPath();ctx.moveTo(77+x,988-h);ctx.lineTo(77+x,988+h);ctx.stroke();}
  ctx.strokeStyle='#e37e21';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(77+820*p/24,962);ctx.lineTo(77+820*p/24,1014);ctx.stroke();ctx.font='24px Tahoma, sans-serif';ctx.fillStyle='#918875';ctx.textAlign='left';ctx.textBaseline='middle';ctx.fillText('0:'+String(Math.floor(p)).padStart(2,'0'),76,1032);ctx.fillText('0:24',816,1032);
  patch(175,1060,762,505);ctx.save();ctx.translate(471.5,1233.5);ctx.scale(1,.735);ctx.rotate(angle*Math.PI/180);ctx.drawImage(art['native/label-'+track().id],-88.7,-88.7,177.4,177.4);ctx.restore();ctx.drawImage(art.spindle,458,1211,28,36);
  ctx.drawImage(art['arm-base'],559,1086,378,372);ctx.save();const radians=arm*Math.PI/180,tipY=1180-260*Math.sin(radians)+254*Math.cos(radians),rock=reduced?0:Math.sin(angle*Math.PI/180)*Math.min(1,speed/200);ctx.translate(839,1180+(tipY-1233.5)*rock/240*(1-lift)-lift*7);ctx.rotate(arm*Math.PI/180);ctx.drawImage(art['arm-moving'],559-839,1086-1180,378,372);ctx.restore();
  sprite('transport',!audio.paused?1:transportState===2?2:0,52,1088,124,214,3);sprite('comparison',mode==='b'?1:0,48,1404,204,90,2);sprite('volume',volume,835,1276,100,210,10);sprite('speaker',volume===0?0:volume<=33?1:volume<=66?2:3,860,1490,70,55,4);sprite('queue-'+lang,trackIndex,638,1509,218,44,3);sprite('export-'+lang,hover==='export'?1:0,337,1490,300,75,2);
 }
 const copy={ru:{cal:'Калибровка VU',hint:'0 VU соответствует выбранному уровню dBFS. Звуковая обработка при этом не меняется.',density:'Плотность',limit:'Для трёх демо-треков подготовлены уровни 0–10.',cancel:'Отмена',choose:'Выбрать демо-трек'},de:{cal:'VU-Kalibrierung',hint:'0 VU entspricht dem gewählten dBFS-Pegel. Die Audiobearbeitung bleibt unverändert.',density:'Dichte',limit:'Für die drei Demos stehen die Werte 0–10 bereit.',cancel:'Abbrechen',choose:'Demo auswählen'},en:{cal:'VU calibration',hint:'0 VU corresponds to the selected dBFS level. Audio processing is unchanged.',density:'Density',limit:'The three demos include prepared levels 0–10.',cancel:'Cancel',choose:'Choose demo'}}[lang];
 const dialog=document.createElement('dialog');dialog.className='peak-dialog';document.body.append(dialog);
 function showDialog(kind){dialog.replaceChildren();dialog.className='peak-dialog '+(kind==='tracks'?'peak-track-dialog':'peak-pixel-dialog');dialog.dataset.kind=kind;
  if(kind==='tracks'){const title=document.createElement('h2');title.textContent=copy.choose;dialog.append(title);tracks.forEach((t,i)=>{const b=document.createElement('button');b.textContent=t.title;b.onclick=()=>{changeTrack(i);dialog.close();};dialog.append(b);});const close=document.createElement('button');close.textContent=copy.cancel;close.onclick=()=>dialog.close();dialog.append(close);dialog.showModal();return;}
  const cal=kind==='cal',w=cal?400:440,h=cal?246:245;dialog.style.setProperty('--dialog-w',w+'px');dialog.style.setProperty('--dialog-h',h+'px');dialog.style.backgroundImage='url("'+BASE+'img/native/'+(cal?'calibration-':'density-')+lang+'.webp")';dialog.setAttribute('aria-label',cal?copy.cal:copy.density);
  const input=document.createElement('input');input.type='number';input.step='1';input.min=cal?'-24':'0';input.max=cal?'3':'10';input.value=cal?reference:density;input.setAttribute('aria-label',cal?copy.cal:copy.density);dialog.append(input);
  function button(label,box,action){const b=document.createElement('button');b.setAttribute('aria-label',label);b.title=label;const[x,y,bw,bh]=box;Object.assign(b.style,{left:x/w*100+'%',top:y/h*100+'%',width:bw/w*100+'%',height:bh/h*100+'%'});b.onclick=action;dialog.append(b);}
  const apply=()=>{if(!input.reportValidity()||!Number.isInteger(Number(input.value)))return false;if(cal){reference=Number(input.value);draw();}else setDensity(Number(input.value));return true;};
  button('×',cal?[351,11,35,32]:[391,11,35,32],()=>dialog.close());
  if(cal){const unit=document.createElement('span');unit.className='peak-dbfs-unit';unit.textContent='dBFS';dialog.append(unit);for(const delta of [-1,1])button(delta<0?'−':'+',[delta<0?22:332,67,46,43],()=>{input.value=Math.max(-24,Math.min(3,Number(input.value)+delta));apply();});button('0 dBFS',[22,190,145,39],()=>{input.value=0;apply();});button('OK',[231,190,147,39],()=>{if(apply())dialog.close();});}
  else{const hint=document.createElement('p');hint.className='peak-density-limit';hint.textContent=copy.limit;dialog.append(hint);button(copy.cancel,[26,190,178,36],()=>dialog.close());button('OK',[226,190,188,36],()=>{if(apply())dialog.close();});}
  dialog.showModal();input.focus();input.select();
 }
 function switchLanguage(next){if(next===lang)return;location.href={de:'about-de.html',ru:'about-ru.html',en:'about.html'}[next]+'#demo';}
 function recordRadius(p){const c=-.0860215054,a=1435*(1+c)-1233.5,v=(1233.5-p.y)/(p.y*c-a),u=(p.x-471.5)*(c*v+1)/261;return Math.hypot(u,v);}
 range.addEventListener('input',()=>setDensity(+range.value,true));volumeRange.addEventListener('input',()=>setVolume(+volumeRange.value));
 playButton.addEventListener('click',toggle);document.querySelector('#demo-stop').addEventListener('click',stop);
 document.querySelectorAll('[data-compare]').forEach(b=>b.addEventListener('click',()=>{mode=b.dataset.compare;updateControls();selectClip();}));document.querySelectorAll('[data-track]').forEach(b=>b.addEventListener('click',()=>changeTrack(tracks.findIndex(t=>t.id===b.dataset.track))));
 const surface=document.createElement('div');surface.className='peak-surface';canvas.before(surface);surface.append(canvas);const hotspots=document.createElement('div');hotspots.className='peak-hotspots';surface.append(hotspots);
 function hot(label,box,action){const b=document.createElement('button');b.type='button';b.setAttribute('aria-label',label);b.title=label;const [x,y,w,h]=box;Object.assign(b.style,{left:x/9.73+'%',top:y/16.16+'%',width:w/9.73+'%',height:h/16.16+'%'});b.onclick=()=>{sound(label==='A / B'?2:0);action();};if(box[0]===347){const set=v=>()=>{hover=v;draw();};b.onpointerenter=set('export');b.onpointerleave=set('');b.onfocus=set('export');b.onblur=set('');}hotspots.append(b);}
 ['ru','de','en'].forEach((l,i)=>hot(l.toUpperCase(),[[439,23,78,58],[529,23,78,58],[616,23,78,58]][i],()=>switchLanguage(l)));
 [[50,529,2],[50,667,5],[726,529,8],[726,667,10]].forEach(([x,y,v],i)=>hot(s.presets[i],[x,y,194,102],()=>setDensity(v)));
 hot(copy.cal,[452,407,58,58],()=>showDialog('cal'));hot(copy.choose,[61,858,830,90],()=>showDialog('tracks'));
 hot(s.play+' / '+s.pause,[63,1090,113,112],toggle);hot(s.stop,[72,1200,86,95],stop);
 hot(lang==='ru'?'Предыдущий трек':lang==='de'?'Vorheriger Titel':'Previous track',[49,1304,59,66],()=>changeTrack((trackIndex+2)%3));hot(lang==='ru'?'Следующий трек':lang==='de'?'Nächster Titel':'Next track',[119,1304,59,66],()=>changeTrack((trackIndex+1)%3));
 hot('A / B',[48,1404,204,90],()=>{mode=mode==='a'?'b':'a';updateControls();selectClip();});hot(s.save,[347,1496,280,62],()=>exportLink.click());
 hot(lang==='ru'?'Включить / выключить звук':lang==='de'?'Ton ein / aus':'Mute / unmute',[860,1490,70,55],()=>{if(volume){previousVolume=volume;setVolume(0);}else setVolume(previousVolume||60);});
 function densityAt(p){let a=Math.atan2(p.y-663,p.x-481)*180/Math.PI;if(a<0)a+=360;if(a>30&&a<150)return a<90?10:0;if(a<150)a+=360;return Math.max(0,Math.min(10,Math.round((a-150)/24)));}
 const point=e=>{const r=canvas.getBoundingClientRect();return {x:(e.clientX-r.left)*973/r.width,y:(e.clientY-r.top)*1616/r.height};};
 function seek(p){if(Number.isFinite(audio.duration))audio.currentTime=Math.max(0,Math.min(audio.duration,p*24));draw();}
 canvas.addEventListener('pointerdown',e=>{const p=point(e);if(Math.hypot(p.x-481,p.y-663)<150){drag={kind:'density',y:e.clientY,value:density,angular:Math.hypot(p.x-481,p.y-663)>45};if(drag.angular)setDensity(densityAt(p),true);canvas.setPointerCapture(e.pointerId);e.preventDefault();}else if(p.x>835&&p.x<922&&p.y>1280&&p.y<1490){drag={kind:'volume'};canvas.setPointerCapture(e.pointerId);setVolume((1443-p.y)*100/119);e.preventDefault();}else if(p.y>954&&p.y<1050){seek((p.x-77)/820);}else if(Math.hypot(p.x-115,p.y-1143)<60)toggle();else if(Math.hypot(p.x-115,p.y-1247)<48)stop();else if(p.x<111&&p.y>1300&&p.y<1380)changeTrack((trackIndex+tracks.length-1)%tracks.length);else if(p.x<190&&p.y>1300&&p.y<1380)changeTrack((trackIndex+1)%tracks.length);else if(p.x<250&&p.y>1400&&p.y<1495){mode=mode==='a'?'b':'a';updateControls();selectClip();}else if(p.x>347&&p.x<627&&p.y>1496&&p.y<1560)exportLink.click();else if(p.y<90&&p.x>439&&p.x<694){switchLanguage(p.x<523?'ru':p.x<612?'de':'en');}else if(Math.hypot(p.x-481,p.y-435)<35)showDialog('cal');else if(p.x>860&&p.x<930&&p.y>1490&&p.y<1545){if(volume){previousVolume=volume;setVolume(0);}else setVolume(previousVolume||60);}else if(p.y>855&&p.y<950)showDialog('tracks');else if(recordRadius(p)<=1.04)seek(Math.max(0,Math.min(1,(1-recordRadius(p))/.65)));else {for(const [x,y,value] of [[50,529,2],[50,667,5],[726,529,8],[726,667,10]])if(p.x>x&&p.x<x+194&&p.y>y&&p.y<y+102)setDensity(value);}});
 canvas.addEventListener('wheel',e=>{const p=point(e);if(Math.hypot(p.x-481,p.y-663)<150){e.preventDefault();setDensity(density+(e.deltaY<0?1:-1),true);}},{passive:false});
 canvas.addEventListener('dblclick',e=>{const p=point(e);if(Math.hypot(p.x-481,p.y-663)<150)showDialog('density');});
 canvas.addEventListener('lostpointercapture',()=>drag=null);
 canvas.addEventListener('pointermove',e=>{if(!e.buttons)drag=null;const p=point(e);if(drag?.kind==='density')setDensity(drag.angular?densityAt(p):drag.value+(drag.y-e.clientY)/9,true);else if(drag?.kind==='volume')setVolume((1443-p.y)*100/119);});canvas.addEventListener('pointerup',()=>drag=null);canvas.addEventListener('pointercancel',()=>drag=null);
 canvas.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight',' ','Escape'].includes(e.key)){e.preventDefault();if(e.key===' ')toggle();else if(e.key==='Escape')stop();else setDensity(density+(e.key==='ArrowRight'?1:-1));}});
 new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;last=0;if(visible){draw();schedule();}},{rootMargin:'80px'}).observe(canvas);document.addEventListener('visibilitychange',()=>{last=0;schedule();});
 audio.addEventListener('timeupdate',()=>{if(visible&&audio.paused)draw();});updateControls();await selectClip(false);
})().catch(e=>{console.error('Music demo unavailable',e);const el=document.querySelector('#demo-state');if(el)el.textContent=JSON.parse(document.querySelector('#demo-strings').textContent).error;});
/* Lazy start: nothing loads from BASE until #demo is close to the viewport. */
if(!('IntersectionObserver' in window)){start();return;}
/* The images are fetched and decoded while the browser is idle, before the visitor scrolls here (decoding during the scroll caused the long frames); the start is guarded so it runs once. */
let started=false;const go=()=>{if(started)return;started=true;lazy.disconnect();start();};
const lazy=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting))go();},{rootMargin:'200px'});
lazy.observe(section);
const idle=()=>(window.requestIdleCallback||(f=>setTimeout(f,1500)))(go,{timeout:5000});
if(document.readyState==='complete')idle();else window.addEventListener('load',idle,{once:true});
})();
