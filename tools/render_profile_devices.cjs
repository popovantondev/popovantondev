// Render each complete laptop with one CSS perspective rotation. Screen contents
// share the device's transform; there is no independent window distortion.
// Requires Playwright, an installed Edge browser, and sharp for WebP output.
const {chromium}=require('playwright');
const sharp=require('sharp');
const fs=require('fs');
const path=require('path');
const source=path.resolve(__dirname,'../assets/banner-sources');
const data=name=>'data:image/webp;base64,'+fs.readFileSync(path.join(source,name)).toString('base64');

(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:340,height:340},deviceScaleFactor:2});
  for(const lang of ['ru','de','en']){
   for(const device of ['mac','windows']){
    if(device==='mac'&&lang!=='ru')continue;
    const windows=device==='windows';
    const content=`<svg xmlns="http://www.w3.org/2000/svg" width="${windows?355:365}" height="355" viewBox="${windows?365:0} 70 ${windows?355:365} 355">
<image width="720" height="480" href="${data('laptops.webp')}"/>
${windows?`<rect x="382" y="94" width="310" height="204" rx="3" fill="#101a2d"/>
<image x="388" y="98" width="128" height="196" preserveAspectRatio="xMidYMid meet" href="${data('peakmp3-'+lang+'.webp')}"/>
<image x="524" y="98" width="160" height="196" preserveAspectRatio="xMidYMid meet" href="${data('quickanswer-'+lang+'.webp')}"/>`:''}</svg>`;
    await page.setContent(`<style>html,body{margin:0;width:340px;height:340px;background:transparent}body{perspective:1000px;perspective-origin:50% 50%}.device{position:absolute;left:25px;top:29px;width:290px;height:282px;transform:rotateY(${windows?-10:10}deg);transform-origin:center}.device svg{display:block;width:100%;height:100%}</style><div class="device">${content}</div>`);
    await page.evaluate(async()=>{await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
    const png=await page.screenshot({omitBackground:true});
    const name=windows?'windows-perspective-'+lang+'.webp':'mac-perspective.webp';
    await sharp(png).webp({quality:94,effort:6}).toFile(path.join(source,name));
    console.log(name);
   }
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
