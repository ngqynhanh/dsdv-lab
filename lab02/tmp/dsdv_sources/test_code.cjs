const fs = require('fs');
const path = require('path');
const assert = require('assert');
const {chromium} = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=process.cwd();
const out=path.join(root,'output','DSDV_on_tap');
const library=fs.readFileSync(path.join(root,'tmp','dsdv_sources','d3.min.js'),'utf8');
const cars=[['A',90,14],['B',150,11],['C',120,13],['D',200,10],['E',null,12],['F',180,15]].map(([Name,Horsepower,Acceleration])=>({Name,Horsepower,Acceleration}));
const csv='Province/State,Country/Region,Lat,Long,3/2/23,3/3/23\nAlpha,Country A,0,0,80,100\nBeta,Country A,0,0,180,200\n,Country B,0,0,0,0\nGamma,Country C,0,0,40,50\n';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
 try{
  for(const [file,fixture] of [['cars_solution.html',JSON.stringify(cars)],['covid_solution.html',csv]]){
   const page=await browser.newPage({viewport:{width:1100,height:800}});const errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',async r=>{
    const url=r.request().url();
    if(url.endsWith(file))return r.fulfill({contentType:'text/html',body:fs.readFileSync(path.join(out,file),'utf8')});
    if(url.includes('d3@7'))return r.fulfill({contentType:'application/javascript',body:library});
    if(url.endsWith('cars.json'))return r.fulfill({contentType:'application/json',body:fixture});
    if(url.endsWith('covid_global.csv'))return r.fulfill({contentType:'text/csv',body:fixture});
    return r.abort();
   });
   await page.goto('http://dsdv.test/'+file);
   await page.locator('rect.bar').first().waitFor();
   const result=await page.evaluate(()=>({
    bars:[...document.querySelectorAll('rect.bar')].map(e=>({data:e.__data__,x:+e.getAttribute('x'),y:+e.getAttribute('y'),width:+e.getAttribute('width'),height:+e.getAttribute('height')})),
    labels:[...document.querySelectorAll('text.value')].map(e=>e.textContent),
    ticks:[...document.querySelectorAll('.tick text')].map(e=>e.textContent)
   }));
   assert.deepStrictEqual(errors,[]);
   assert(result.bars.every(b=>[b.x,b.y,b.width,b.height].every(Number.isFinite)&&b.height>=0&&b.width>=0));
   if(file.startsWith('cars')){
    assert.deepStrictEqual(result.bars.map(b=>b.data.Name),['D','F','B','C','A']);
    assert.deepStrictEqual(result.labels,['10','15','11','13','14']);
   }else{
    assert.strictEqual(result.bars.length,3);assert.deepStrictEqual(result.labels,['100','200','50']);
    assert(result.ticks.includes('Alpha / Country A'));
   }
   await page.screenshot({path:path.join(root,'tmp','dsdv_sources',file+'.png')});
   console.log(file,'PASS',result.bars.length,'bars, values and geometry validated');
   await page.close();
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
