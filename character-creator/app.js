const DATA=JSON.parse(document.getElementById('catalog').textContent);
const canvas=document.getElementById('preview'),status=document.getElementById('status');
const defaults={head:0,face:0,outfit:0,accessory:0,effect:0};
let state={...defaults},view='assembled',playing=true,time=0,last=performance.now(),busy=false,cancelled=false;
const registry={},player=new SpriterPlayer();
const effects=[['Azul arcano','#49bce7'],['Verde floresta','#8fc66d'],['Violeta','#b283ed'],['Chama','#ed8e4e'],['Gelo','#a9e9ed'],['Dourado','#e0c16f']];
const definitions=[
 {id:'head',label:'Cabelo / capuz',options:[['Careca','Cabeça básica, sem cabelo.'],['Cabelo curto','Castanho, com mechas simples.'],['Cabelo prateado','Penteado para trás.'],['Capuz','Tecido verde-escuro.'],['Elmo Ranger','Elmo e barba do personagem de referência.']]},
 {id:'face',label:'Rosto',options:[['Sem rosto','Uma base em branco para começar.'],['Concentrado','Olhos verdes e sobrancelhas castanhas.'],['Aventureiro','Olhos azuis e expressão confiante.'],['Veterano','Olhos âmbar e sobrancelhas prateadas.'],['Rosto Ranger','Expressões originais, incluindo piscar e dano.']]},
 {id:'outfit',label:'Corpo / roupa',options:[['Roupa básica','Túnica marrom, cinto e botas simples.'],['Ranger','Roupa verde e couro do ZIP de referência.'],['Mago','Túnica azul-petróleo com detalhes dourados.']]},
 {id:'accessory',label:'Acessório',options:[['Nenhum','Mãos livres.'],['Cajado de cristal','Madeira e cristal azul.'],['Clava','Madeira escura com pontas.'],['Bastão Ranger','O acessório original do Ranger.']]},
 {id:'effect',label:'Cor do efeito',options:effects.map(([name])=>[name,'A cor aparece nas animações de ataque.'])}
];
const animationLabels={'Idle':'Em repouso','Idle Blinking':'Repouso · piscar','Walking':'Caminhando','Running':'Correndo','Slashing':'Ataque básico','Throwing':'Arremesso','Kicking':'Chute','Run Slashing':'Corrida + ataque','Run Throwing':'Corrida + arremesso','Sliding':'Deslizando','Jump Start':'Início do salto','Jump Loop':'No ar','Slashing in The Air':'Ataque no ar','Throwing in The Air':'Arremesso no ar','Falling Down':'Caindo','Hurt':'Recebendo dano','Dying':'Morte'};
const select=document.getElementById('animation');
for(const name of Object.keys(DATA.rig.frameCounts))select.add(new Option(animationLabels[name]||name,name));
select.value='Idle';

function makeCanvas(width,height){const c=document.createElement('canvas');c.width=width;c.height=height;return c}
function weaponTransform(input){
 const value={...input},angle=Number(input.angle||0)*Math.PI/180;
 value.x=Number(input.x||0)+Math.cos(angle)*64+Math.sin(angle)*64;
 value.y=Number(input.y||0)+Math.sin(angle)*64-Math.cos(angle)*64;
 value.angle=(Number(input.angle||0)+40)%360;
 value.file='9';value.a=state.accessory?1:0;
 value.pivot_x=([0,90,90,44][state.accessory])/400;value.pivot_y=.5;
 return value;
}
function selectedRig(){
 const rig=structuredClone(DATA.rig);
 for(const animation of rig.animations){
  animation.timelines['15']=animation.timelines['8'].map(key=>({...key,transform:weaponTransform(key.transform)}));
  for(const key of animation.mainline){const hand=key.objects.find(ref=>ref.timeline==='8');key.objects.find(ref=>ref.timeline==='15').key=hand.key}
 }
 return rig;
}
function selectedSCML(){
 const doc=new DOMParser().parseFromString(DATA.scml,'application/xml');doc.querySelector('entity').setAttribute('name','CustomAvatar');
 for(const animation of doc.querySelectorAll('animation')){
  const timelines=[...animation.querySelectorAll('timeline')],weapon=timelines.find(t=>t.getAttribute('name')==='Sword'),hand=timelines.find(t=>t.getAttribute('name')==='Left Hand');
  weapon.replaceChildren();
  for(const key of hand.children){
   const copy=key.cloneNode(true),object=copy.querySelector('object'),values=weaponTransform(Object.fromEntries([...object.attributes].map(a=>[a.name,a.value])));
   for(const [name,value] of Object.entries(values))object.setAttribute(name,String(value));weapon.append(copy);
  }
  for(const key of animation.querySelector('mainline').children){
   const refs=[...key.querySelectorAll('object_ref')],h=refs.find(r=>r.getAttribute('timeline')===hand.getAttribute('id')),w=refs.find(r=>r.getAttribute('timeline')===weapon.getAttribute('id'));
   w.setAttribute('key',h.getAttribute('key'));
  }
 }
 return new XMLSerializer().serializeToString(doc);
}
function tintedEffect(){
 const source=registry['original/SlashFX.png'],c=makeCanvas(source.width,source.height),ctx=c.getContext('2d');ctx.drawImage(source,0,0);
 const image=ctx.getImageData(0,0,c.width,c.height),d=image.data,hex=effects[state.effect][1].slice(1),rgb=[0,2,4].map(i=>parseInt(hex.slice(i,i+2),16));
 for(let i=0;i<d.length;i+=4){if(!d[i+3])continue;const lum=(d[i]*.2126+d[i+1]*.7152+d[i+2]*.0722)/255,white=Math.max(0,(lum-.72)/.28)*.65;for(let k=0;k<3;k++)d[i+k]=Math.round(rgb[k]*(.6+.4*lum)*(1-white)+255*white)}
 ctx.putImageData(image,0,0);return c;
}
function refreshTextures(){
 const images={};for(const [id,file] of Object.entries(DATA.rig.files))images[id]=registry['original/'+file.name];
 images['1']=registry[['heads/bald.png','heads/short.png','heads/silver.png','heads/hood.png','original/Head.png'][state.head]];
 for(const id of ['4','11','12']){
  if(!state.face)images[id]=makeCanvas(320,240);
  else if(state.face<4)images[id]=registry['faces/'+['focused','adventurer','veteran'][state.face-1]+'.png'];
 }
 if(state.outfit===0)images['0']=registry['outfits/basic/Body.png'];
 if(state.outfit===2){for(const id of ['0','2','5','7','8'])images[id]=registry['outfits/mage/'+DATA.rig.files[id].name]}
 images['9']=state.accessory?registry[['','accessories/Staff.png','accessories/Club.png','original/Sword.png'][state.accessory]]:makeCanvas(400,128);
 images['10']=tintedEffect();player.images=images;player.rig=selectedRig();
}
function validState(value){
 if(!value||typeof value!=='object')throw Error('Arquivo de escolhas inválido.');
 for(const def of definitions)if(!Number.isInteger(value[def.id])||value[def.id]<0||value[def.id]>=def.options.length)throw Error('Escolha inválida: '+def.label);
 return Object.fromEntries(definitions.map(def=>[def.id,value[def.id]]));
}
function persist(){try{localStorage.setItem('chibi-creator-v1',JSON.stringify(state))}catch{}}
function update(){
 refreshTextures();persist();
 for(const def of definitions){const item=document.querySelector('[data-option="'+def.id+'"]');item.querySelector('.choice').textContent=def.options[state[def.id]][0];item.querySelector('.description').textContent=def.options[state[def.id]][1];item.querySelector('.counter').textContent=(state[def.id]+1)+' / '+def.options.length}
 document.querySelectorAll('.swatch').forEach((button,i)=>button.setAttribute('aria-pressed',String(i===state.effect)));
 render();
}
function change(id,delta){const def=definitions.find(d=>d.id===id);state[id]=(state[id]+delta+def.options.length)%def.options.length;if(id==='effect'){select.value='Slashing';time=200;setView('assembled')}update()}
function buildControls(){
 for(const def of definitions){
  const section=document.createElement('section');section.className='option';section.dataset.option=def.id;
  const top=document.createElement('div');top.className='optionTop';const label=document.createElement('span');label.className='optionLabel';label.textContent=def.label;const counter=document.createElement('span');counter.className='counter';top.append(label,counter);
  const row=document.createElement('div');row.className='stepper';
  const previous=document.createElement('button');previous.className='arrow';previous.textContent='‹';previous.setAttribute('aria-label',def.label+' anterior');previous.onclick=()=>change(def.id,-1);
  const name=document.createElement('span');name.className='choice';name.setAttribute('aria-live','polite');
  const next=document.createElement('button');next.className='arrow';next.textContent='›';next.setAttribute('aria-label','Próximo: '+def.label);next.onclick=()=>change(def.id,1);
  row.append(previous,name,next);const desc=document.createElement('p');desc.className='description';section.append(top,row,desc);
  if(def.id==='effect'){const swatches=document.createElement('div');swatches.className='swatches';effects.forEach(([name,color],i)=>{const button=document.createElement('button');button.className='swatch';button.style.setProperty('--swatch',color);button.setAttribute('aria-label',name);button.onclick=()=>{state.effect=i;select.value='Slashing';time=200;setView('assembled');update()};swatches.append(button)});section.append(swatches)}
  document.getElementById('options').append(section);
 }
}
function renderParts(){
 const ctx=canvas.getContext('2d');ctx.clearRect(0,0,900,900);
 for(const [i,[id,file]] of Object.entries(DATA.rig.files).entries()){
  const x=i%4*225,y=Math.floor(i/4)*225;ctx.fillStyle='#173c3055';ctx.fillRect(x+10,y+10,205,205);
  const image=player.images[id],scale=Math.min(180/Number(file.width),166/Number(file.height));
  ctx.drawImage(image,x+112.5-Number(file.width)*scale/2,y+100-Number(file.height)*scale/2,Number(file.width)*scale,Number(file.height)*scale);
  ctx.fillStyle='#d2e5c7';ctx.textAlign='center';ctx.font='17px system-ui';ctx.fillText(file.name.replace('.png',''),x+112.5,y+196);
 }
}
function render(){if(!player.images||!player.rig)return;if(view==='parts')renderParts();else player.draw(canvas,select.value,time)}
function setView(next){view=next;document.querySelector('.canvasWrap').classList.toggle('parts',view==='parts');document.getElementById('assembledView').setAttribute('aria-pressed',String(view==='assembled'));document.getElementById('partsView').setAttribute('aria-pressed',String(view==='parts'));canvas.setAttribute('aria-label',view==='parts'?'Peças do personagem':'Personagem montado');render()}
function tick(now){if(playing&&!busy)time+=(now-last)*Number(document.getElementById('speed').value);last=now;render();requestAnimationFrame(tick)}
function blobOf(c){return new Promise((resolve,reject)=>c.toBlob(blob=>blob?resolve(blob):reject(Error('Não foi possível gerar PNG.')),'image/png'))}
function download(blob,name){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),3000)}
const crcTable=Uint32Array.from({length:256},(_,n)=>{for(let k=0;k<8;k++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0});
function crc32(bytes){let c=0xffffffff;for(const b of bytes)c=crcTable[(c^b)&255]^(c>>>8);return(c^0xffffffff)>>>0}
class ZipStore{
 constructor(){this.parts=[];this.central=[];this.offset=0;this.count=0;this.centralSize=0}
 async add(name,input){
  const data=input instanceof Blob?new Uint8Array(await input.arrayBuffer()):typeof input==='string'?new TextEncoder().encode(input):input;
  const filename=new TextEncoder().encode(name),crc=crc32(data),header=new Uint8Array(30+filename.length),v=new DataView(header.buffer);
  v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint16(6,0x800,true);v.setUint16(12,0x21,true);v.setUint32(14,crc,true);v.setUint32(18,data.length,true);v.setUint32(22,data.length,true);v.setUint16(26,filename.length,true);header.set(filename,30);
  const central=new Uint8Array(46+filename.length),c=new DataView(central.buffer);c.setUint32(0,0x02014b50,true);c.setUint16(4,20,true);c.setUint16(6,20,true);c.setUint16(8,0x800,true);c.setUint16(14,0x21,true);c.setUint32(16,crc,true);c.setUint32(20,data.length,true);c.setUint32(24,data.length,true);c.setUint16(28,filename.length,true);c.setUint32(42,this.offset,true);central.set(filename,46);
  this.parts.push(header,data);this.central.push(central);this.offset+=header.length+data.length;this.centralSize+=central.length;this.count++;
 }
 finish(){const end=new Uint8Array(22),v=new DataView(end.buffer);v.setUint32(0,0x06054b50,true);v.setUint16(8,this.count,true);v.setUint16(10,this.count,true);v.setUint32(12,this.centralSize,true);v.setUint32(16,this.offset,true);return new Blob([...this.parts,...this.central,end],{type:'application/zip'})}
}
function setBusy(value){busy=value;document.querySelectorAll('button,input,select').forEach(element=>{if(element.id!=='cancelExport')element.disabled=value});document.getElementById('cancelExport').hidden=!value}
async function exportSprites(){
 if(busy)return;setBusy(true);cancelled=false;
 try{
  const zip=new ZipStore(),output=makeCanvas(900,900);let done=0;
  await zip.add('CustomAvatar/config.json',JSON.stringify({version:1,state},null,2));
  await zip.add('CustomAvatar/PNG/Vector Parts/Animations.scml',selectedSCML());
  for(const [id,file] of Object.entries(DATA.rig.files)){const texture=makeCanvas(Number(file.width),Number(file.height));texture.getContext('2d').drawImage(player.images[id],0,0,texture.width,texture.height);await zip.add('CustomAvatar/PNG/Vector Parts/'+file.name,await blobOf(texture))}
  for(const [name,count] of Object.entries(DATA.rig.frameCounts)){
   const animation=player.rig.animations.find(a=>a.name===name);
   for(let frame=0;frame<count;frame++){
    if(cancelled)throw Error('Exportação cancelada.');
    player.draw(output,name,frame*Number(animation.length)/count);
    await zip.add(`CustomAvatar/PNG/PNG Sequences/${name}/0_CustomAvatar_${name}_${String(frame).padStart(3,'0')}.png`,await blobOf(output));
    status.textContent=`Exportando ${++done}/207 · ${animationLabels[name]||name}`;
   }
  }
  await zip.add('CustomAvatar/README.txt','Personagem montado no criador chibi.\n13 peças PNG, rig SCML e 207 frames em 17 animações.\nCabeça/cabelo/capuz são variantes de Head.png; o rosto é independente.\nOs rostos Concentrado, Aventureiro e Veterano são poses faciais estáticas; Rosto Ranger preserva as três expressões originais.\nRig e peças de referência: Forest_Ranger_3 fornecido pelo usuário, sujeito à licença original Craftpix: https://craftpix.net/file-licenses/\n');
  download(zip.finish(),'CustomAvatar-sprites.zip');status.textContent='Pronto: 13 peças e 207 frames exportados.';
 }catch(error){status.textContent=error.message}finally{setBusy(false)}
}
document.getElementById('assembledView').onclick=()=>setView('assembled');document.getElementById('partsView').onclick=()=>setView('parts');
document.getElementById('playPause').onclick=()=>{playing=!playing;document.getElementById('playPause').textContent=playing?'Ⅱ':'▶';document.getElementById('playPause').setAttribute('aria-label',playing?'Pausar animação':'Reproduzir animação')};
select.onchange=()=>{time=0;render()};document.getElementById('speed').oninput=e=>{document.getElementById('speedValue').textContent=Number(e.target.value).toLocaleString('pt-BR')+'×'};
document.getElementById('reset').onclick=()=>{state={...defaults};select.value='Idle';time=0;status.textContent='Base careca e sem rosto.';update()};
document.getElementById('example').onclick=()=>{state={head:1,face:1,outfit:1,accessory:1,effect:1};select.value='Idle';time=0;status.textContent='Exemplo montado. Continue trocando as peças.';update()};
document.getElementById('exportPNG').onclick=async()=>{try{const c=makeCanvas(900,900);player.draw(c,select.value,time);download(await blobOf(c),'CustomAvatar.png');status.textContent='PNG transparente exportado.'}catch(error){status.textContent=error.message}};
document.getElementById('exportConfig').onclick=()=>download(new Blob([JSON.stringify({version:1,state,choices:Object.fromEntries(definitions.map(d=>[d.id,d.options[state[d.id]][0]]))},null,2)],{type:'application/json'}),'CustomAvatar-escolhas.json');
document.getElementById('importConfig').onclick=()=>document.getElementById('configFile').click();
document.getElementById('configFile').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{const config=JSON.parse(await file.text());state=validState(config.state||config);time=0;update();status.textContent='Escolhas carregadas.'}catch(error){status.textContent='Não foi possível carregar: '+error.message}finally{e.target.value=''}};
document.getElementById('exportZIP').onclick=exportSprites;document.getElementById('cancelExport').onclick=()=>{cancelled=true};
async function init(){
 try{
  await Promise.all(Object.entries(DATA.images).map(async([key,url])=>{const image=new Image();image.src=url;await image.decode();registry[key]=image}));
  try{const saved=localStorage.getItem('chibi-creator-v1');if(saved)state=validState(JSON.parse(saved))}catch{}
  buildControls();update();document.getElementById('loading').hidden=true;window.creatorReady=true;requestAnimationFrame(tick);
 }catch(error){document.getElementById('loading').textContent='Não foi possível carregar as peças: '+error.message}
}
init();
