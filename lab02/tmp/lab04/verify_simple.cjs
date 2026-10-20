const {chromium}=require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('url');const assert=require('assert/strict');const fs=require('fs');const path=require('path');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));const root=path.resolve('../lab04/lab04-d3');
const ready=()=>page.waitForFunction(()=>typeof busy!=='undefined'&&!busy&&active.length>0);
const click=async id=>{await page.click('#'+id);await ready()};
const ids=()=>page.evaluate(()=>active.map(d=>d.id));
await page.goto(pathToFileURL(path.join(root,'index.html')).href);await ready();assert.equal(await page.locator('.row').count(),20);const initial=await ids();
await click('add');assert.equal(await page.locator('.row').count(),21);await click('remove');assert.deepEqual(await ids(),initial);
await page.evaluate(()=>window.nodes=new Map([...document.querySelectorAll('.row')].map(n=>[n.dataset.id,n])));
await page.selectOption('#sort-select','grdp');await ready();assert(await page.evaluate(()=>[...document.querySelectorAll('.row')].every(n=>nodes.get(n.dataset.id)===n)));assert.deepEqual(await ids(),initial);
await click('remove');await click('undo');assert.deepEqual(await ids(),initial);assert(await page.isDisabled('#undo'));
await click('remove');await click('add');assert.deepEqual(await ids(),initial);assert(await page.isDisabled('#undo'));
await page.evaluate(()=>{document.querySelector('#add').click();document.querySelector('#add').click()});await ready();assert.equal(await page.locator('.row').count(),21);await click('remove');
// Fast boundary pass uses the same file with only duration reduced.
await page.route('**/chart.js',r=>r.fulfill({contentType:'application/javascript',body:fs.readFileSync(path.join(root,'chart.js'),'utf8').replace('const duration = 700;','const duration = 1;')}));
await page.reload();await ready();for(let i=0;i<70;i++){await page.evaluate(()=>document.querySelector('#add').click());await ready()};assert.equal(await page.locator('.row').count(),63);assert(await page.isDisabled('#add'));
for(let i=0;i<70;i++){await page.evaluate(()=>document.querySelector('#remove').click());await ready()};assert.equal(await page.locator('.row').count(),1);assert(await page.isDisabled('#remove'));
assert(await page.evaluate(()=>{const r=document.querySelector('.row');return x.domain()[0]===0&&Math.abs(+r.querySelector('.bar').getAttribute('width')-x(active[0].value))<.001&&Math.abs(+r.querySelector('.value-label').getAttribute('x')-x(active[0].value)-7)<.001}));assert.deepEqual(errors,[]);
console.log('PASS: local file, 20->21->20, sort preserves DOM identity, Undo, Remove/Add, rapid clicks, 1-63 boundaries, scale and label positions.');await browser.close()})().catch(e=>{console.error(e);process.exit(1)});
