'use strict';
const $ = id => document.getElementById(id);
const fields = ['title','story','look','camera','duration','seed'];
const refs = ['start','end','background','voice','music'];
let graphTemplate, urls = [];
function direction() { return Object.fromEntries(fields.map(id => [id, $(id).value])); }
function names() { return Object.fromEntries(refs.map(id => [id, $(id).files[0]?.name || null])); }
function generate() {
 const d = direction();
 return `Title: ${d.title}\n\nScene: ${d.story}\n\nVisual direction: ${d.look}.\nCamera and movement: ${d.camera}.\n\nReference guidance: use the provided images as flexible inspiration for characters, composition and world; adapt them to the action rather than treating them as exact frame locks.\n\nDelivery: approximately ${d.duration} seconds, 24 fps, widescreen. Preserve character continuity and clear visual storytelling.`;
}
function update() { $('previewTitle').textContent = $('title').value || 'Untitled scene'; $('shotLength').textContent = `${$('duration').value || '—'} SEC`; }
function download(name, content, type) { const blob = new Blob([content], {type}); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href=url; a.download=name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 3000); }
function packet() {return {schema:'budnspud-production-packet-v1',direction:direction(),shots:[{title:$('title').value,prompt:$('prompt').value}],references:names(),reference_policy:'Guidance only; not hard locks',runtime:{generation:'self-hosted ComfyUI submission available',cloud:'not implemented',graph:'MiniMax H3 graph with three image and two audio references'},note:'Reference names only; source media is not included.'};}
function valid() { const d=Number($('duration').value), s=Number($('seed').value); if (!Number.isInteger(d)||d<1||d>30||!Number.isSafeInteger(s)||s<0) throw Error('Duration must be a whole number from 1 to 30 and seed a non-negative safe integer.'); if (!$('prompt').value.trim()) throw Error('Write a prompt first.'); }
function run(fn) { try { valid(); fn(); $('notice').textContent='Export prepared. Your prompt remains editable.'; } catch(e) { $('notice').textContent=e.message; } }
function renderRefs(){ urls.forEach(URL.revokeObjectURL);urls=[];const target=$('previews');target.replaceChildren(); for(const id of refs){const f=$(id).files[0];if(!f)continue; const url=URL.createObjectURL(f);urls.push(url); const node=document.createElement(id==='voice'||id==='music'?'audio':'img'); if(node.tagName==='AUDIO')node.controls=true; else node.alt=`${id} reference preview`;node.src=url;target.append(node);} }
fields.forEach(id => $(id).addEventListener('input',update)); refs.forEach(id => $(id).addEventListener('change',renderRefs));
$('rebuild').addEventListener('click',()=>{if($('prompt').value!==generate() && !confirm('Replace the current prompt with a newly generated one?'))return; $('prompt').value=generate();$('notice').textContent='Prompt rebuilt from direction.';});
$('packet').addEventListener('click',()=>run(()=>download('production-packet.json',JSON.stringify(packet(),null,2),'application/json')));
$('prompts').addEventListener('click',()=>run(()=>download('prompts.json',JSON.stringify([$('prompt').value],null,2),'application/json')));
$('script').addEventListener('click',()=>run(()=>download('script.md',`# ${$('title').value}\n\n## Scene 01 — ${$('duration').value} seconds\n\n${$('story').value}\n\n## Prompt\n\n${$('prompt').value}\n\nReferences are guidance, not hard locks.\n`,'text/markdown')));
function buildGraph() {
 if(!graphTemplate)throw Error('Workflow template could not be loaded.');
 const n=names(); if(refs.some(id=>!n[id]))throw Error('Choose all three images and both audio references.');
 const g=structuredClone(graphTemplate);
 for(const [id,node,key] of [['start','137','image'],['end','149','image'],['background','150','image'],['voice','151','audio'],['music','152','audio']]) g[node].inputs[key]=n[id];
 g['138'].inputs.value=$('prompt').value; g['132'].inputs.value=Number($('duration').value);g['129'].inputs.noise_seed=Number($('seed').value); return g;
}
$('graph').addEventListener('click',()=>run(()=>download('comfy-api-graph.json',JSON.stringify(buildGraph(),null,2),'application/json')));
$('submit').addEventListener('click',async()=>{
 try {
  valid(); buildGraph();
  if (!$('endpoint').value.trim()) throw Error('Enter your local ComfyUI URL.');
  if (!confirm('Upload all five references to your local ComfyUI and queue a GPU job?')) return;
  const form=new FormData(); form.append('endpoint',$('endpoint').value.trim()); form.append('prompt',$('prompt').value); form.append('duration',$('duration').value); form.append('seed',$('seed').value);
  refs.forEach(id=>form.append(id,$(id).files[0])); $('submit').disabled=true; $('notice').textContent='Uploading and submitting to local ComfyUI…';
  const response=await fetch('/api/submit',{method:'POST',body:form}); const result=await response.json(); if(!response.ok)throw Error(result.error||'Submission failed.');
  $('notice').textContent=`Queued on local ComfyUI. Prompt ID: ${result.prompt_id}. This is not a completed video.`;
 } catch(e) { $('notice').textContent=e.message; } finally { $('submit').disabled=false; }
});
$('prompt').value=generate();update();fetch('workflow.json').then(r=>{if(!r.ok)throw Error('Workflow unavailable');return r.json()}).then(g=>{graphTemplate=g}).catch(()=>{$('notice').textContent='Workflow template unavailable; prompt exports still work.'});
