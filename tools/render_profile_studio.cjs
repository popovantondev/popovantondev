// Render the profile artwork from the same photograph, screenshots and geometry as the catalog.
// Requires Playwright and Edge; run after generating localized catalog pages.
const {chromium}=require('playwright');
const path=require('path');
const {pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..');
const labels={ru:'Каталог программ и руководств',de:'Anwendungen und Anleitungen',en:'Applications and guides'};
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const page=await browser.newPage({viewport:{width:2048,height:768},deviceScaleFactor:1});
 for(const lang of ['ru','de','en']){
  await page.goto(pathToFileURL(path.join(root,lang==='en'?'index.html':`index-${lang}.html`)).href);
  await page.locator('.hero-studio img').evaluateAll(xs=>Promise.all(xs.map(i=>i.decode())));
  await page.addStyleTag({content:'.shell{max-width:none;padding:0}.top{display:none}.hero.hero-studio{margin:0;width:2048px;box-shadow:none}.hero-studio .hero-actions{gap:0}.hero-studio .hero-actions a{font-size:24px}'});
  await page.locator('.hero-actions').evaluate((el,label)=>{el.replaceChildren();const a=document.createElement('a');a.className='primary';a.textContent=label+' ↗';a.href='#catalog';el.append(a)},labels[lang]);
  await page.locator('.hero-studio').screenshot({path:path.join(root,`assets/profile-studio-${lang}.png`)});
 }
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
