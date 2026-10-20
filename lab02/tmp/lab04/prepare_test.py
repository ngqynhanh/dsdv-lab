from pathlib import Path
s=Path('tmp/lab04/verify_simple.cjs').read_text(encoding='utf-8-sig')
s=s.replace("(async()=>{",'''const http=require('http');
const server=http.createServer((req,res)=>{try{const file=path.join(path.resolve('../lab04/lab04-d3'),req.url==='/'?'index.html':decodeURIComponent(req.url));res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':file.endsWith('.csv')?'text/csv':'text/html');res.end(fs.readFileSync(file));}catch{res.statusCode=404;res.end();}});
(async()=>{await new Promise(r=>server.listen(8765,'127.0.0.1',r));''')
s=s.replace("await page.goto(pathToFileURL(path.join(root,'index.html')).href)","await page.goto('http://127.0.0.1:8765/')")
s=s.replace("'.row'","'rect.bar'").replace("r.querySelector('.bar').getAttribute('width')","r.getAttribute('width')").replace("r.querySelector('.value-label').getAttribute('x')","document.querySelector('.value-label').getAttribute('x')")
s=s.replace("local file,", "HTTP CSV, join pattern,")
s=s.replace('await browser.close()', 'await browser.close();server.close()')
s=s.replace('console.error(e);process.exit(1)', 'console.error(e);server.close();process.exit(1)')
Path('tmp/lab04/verify_prelab.cjs').write_text(s,encoding='utf-8')
