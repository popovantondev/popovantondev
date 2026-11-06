/* Catalog: category tabs + platform filter + search work together; without this script every card stays visible. */
(()=>{'use strict';
const controls=document.querySelector('.catalog-controls'),cards=[...document.querySelectorAll('.project')],input=document.getElementById('project-search'),count=document.getElementById('result-count'),empty=document.getElementById('empty'),panel=document.getElementById('projects'),tabs=[...document.querySelectorAll('.ppk-tabs [role="tab"]')];
let category='all',platform='all';
if(!controls||!input)return;
const norm=s=>{s=String(s).toLocaleLowerCase().replace(/ß/g,'ss');try{s=s.normalize('NFD').replace(/[\u0300-\u036f]/g,'')}catch(e){}return s};
const hay=new Map(cards.map(c=>[c,norm(c.textContent+' '+(c.dataset.keywords||''))]));
controls.hidden=false;
function update(){
 const tokens=norm(input.value.trim()).split(/\s+/).filter(Boolean);let shown=0;
 for(const card of cards){
  const match=(category==='all'||card.dataset.category===category)&&(platform==='all'||card.dataset.platform===platform)&&tokens.every(t=>hay.get(card).includes(t));
  card.hidden=!match;if(match)shown++;
 }
 count.textContent=shown+' / '+cards.length;empty.hidden=shown!==0;
}
for(const tab of tabs)tab.addEventListener('click',()=>{
 category=tab.dataset.category;
 for(const other of tabs)other.setAttribute('aria-selected',String(other===tab));
 if(panel)panel.setAttribute('aria-labelledby',tab.id);
 update();
});
for(const button of controls.querySelectorAll('[data-filter]'))button.addEventListener('click',()=>{
 platform=button.dataset.filter;
 for(const other of controls.querySelectorAll('[data-filter]'))other.setAttribute('aria-pressed',String(other===button));
 update();
});
input.addEventListener('input',update);
})();

// Keep the original photograph and screen planes on the same coordinate system.
(()=>{const art=document.querySelector(".hero-studio .studio-art");if(!art)return;const resize=()=>art.style.setProperty("--scale",art.clientWidth/2048);new ResizeObserver(resize).observe(art);resize();
// Show the scene only when the photograph and all window pictures are decoded (otherwise the windows pop in over a half-drawn studio).
const imgs=[...art.querySelectorAll("img")],show=()=>art.classList.add("is-ready");
Promise.race([Promise.all(imgs.map(i=>i.decode?i.decode().catch(()=>{}):Promise.resolve())),new Promise(r=>setTimeout(r,20000))]).then(show,show)})();
