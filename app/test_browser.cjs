// Browser integration against an in-process simulated ComfyUI; no GPU work.
const {chromium}=require(process.env.PLAYWRIGHT_CORE || '/home/ubuntu/.local/opt/rea-6.8.0/node_modules/playwright-core');
const http=require('http'), {spawn}=require('child_process'), assert=require('assert'), readline=require('readline');
(async()=>{
 let uploads=[], graph;
 const mock=http.createServer((req,res)=>{let chunks=[];req.on('data',c=>chunks.push(c));req.on('end',()=>{const b=Buffer.concat(chunks);res.setHeader('Content-Type','application/json'); if(req.url==='/upload/image'){uploads.push(b);res.end(JSON.stringify({name:`uploaded-${uploads.length}.bin`,subfolder:'',type:'input'}));}else if(req.url==='/prompt'){graph=JSON.parse(b).prompt;res.end(JSON.stringify({prompt_id:'mock-browser-job'}));}else{res.statusCode=404;res.end('{}');}})});
 await new Promise(r=>mock.listen(0,'127.0.0.1',r));
 const app=spawn('python',['server.py','--port','0'],{cwd:__dirname});
 const line=await new Promise(r=>readline.createInterface({input:app.stdout}).once('line',r)); const url=line.split(' ').at(-1);
 let browser;
 try {
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM || '/home/ubuntu/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome',args:['--no-sandbox']});
  const page=await browser.newPage({acceptDownloads:true}); const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  page.on('dialog',d=>d.accept()); await page.goto(url); await page.waitForResponse(r=>r.url().endsWith('/workflow.json'));
  const refs=['start','end','background','voice','music']; for(const name of refs) await page.locator('#'+name).setInputFiles({name:name+(name==='voice'||name==='music'?'.wav':'.png'),mimeType:'application/octet-stream',buffer:Buffer.from(name)});
  await page.locator('#prompt').fill('Browser test scene'); await page.locator('#endpoint').fill(`http://127.0.0.1:${mock.address().port}`);
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#graph').click()]); const exported=JSON.parse(await require('fs').promises.readFile(await download.path(),'utf8'));
  assert.equal(exported['150'].inputs.image,'background.png');assert.equal(exported['152'].inputs.audio,'music.wav');
  const [packet]=await Promise.all([page.waitForEvent('download'),page.locator('#packet').click()]); assert.equal(JSON.parse(await require('fs').promises.readFile(await packet.path(),'utf8')).schema,'budnspud-production-packet-v1');
  await page.locator('#submit').click(); await page.getByText('mock-browser-job',{exact:false}).waitFor();
  assert.equal(uploads.length,5); for(const [i,node] of ['137','149','150','151','152'].entries()) assert.equal(graph[node].inputs[i<3?'image':'audio'],`uploaded-${i+1}.bin`);
  assert.equal(graph['138'].inputs.value,'Browser test scene'); assert.deepEqual(errors,[]);
  console.log('PASS browser: 5 uploads, graph and packet exports, prompt ID, graph mapping; simulated ComfyUI only');
 } finally {if(browser)await browser.close(); app.kill(); mock.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
