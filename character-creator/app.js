const DATA=JSON.parse(document.getElementById('catalog').textContent);
const canvas=document.getElementById('preview'),status=document.getElementById('status');
const defaultColors={skin:'#dbbe9a',hair:'#40505a',brows:'#734b2e',eyes:'#307d60'};
const defaults={head:0,face:0,outfit:0,accessory:0,shield:0,effect:0,effectShape:0,colors:{...defaultColors}};
let state={...defaults},view='assembled',playing=true,time=0,last=performance.now(),busy=false,cancelled=false;
const registry={},player=new SpriterPlayer();
const effects=[['Azul arcano','#49bce7'],['Verde floresta','#8fc66d'],['Violeta','#b283ed'],['Chama','#ed8e4e'],['Gelo','#a9e9ed'],['Dourado','#e0c16f']];
const definitions=[
 {id:'head',label:'Cabelo',options:[['Careca','Cabeça básica, sem cabelo.'],['Cabelo curto','Corte preto, com formas simples.'],['Cabelo prateado','Penteado para trás.'],['Cabelo azul','Curto, com mechas geométricas.'],['Cabelo loiro','Corte arredondado com franja.'],['Fallen · cabelo','Cabelo longo prateado do pacote enviado.'],['Espectral · capuz','Capuz do novo pacote, preservando o desenho original.'],['Valquíria · elmo','Elmo alado e cabelo do pacote enviado.'],['Mago · cabelo','Cabelo claro e cabeça sem rosto do mago enviado.']]},
 {id:'face',label:'Rosto',options:[['Sem rosto','Uma base em branco para começar.'],['Severo','Sobrancelhas marcadas e olhar estreito.'],['Determinado','Sobrancelhas angulares e olhar confiante.'],['Resoluto','Traços firmes e expressão séria.'],['Rosto Ranger','Expressões originais, incluindo piscar e dano.'],['Fallen · rosto','As três expressões originais do pacote enviado.'],['Espectral · rosto','Olhar marcado e três expressões originais.'],['Valquíria · rosto','Olhos, sobrancelhas e três expressões do novo conjunto.']]},
 {id:'outfit',label:'Corpo / roupa',options:[['Roupa básica','Túnica marrom, cinto e botas simples.'],['Ranger','Roupa verde e couro do ZIP de referência.'],['Mago','Traje azul no molde original, com mangas, luvas e botas.'],['Armadura de couro','Couro escuro com rebites e mãos protegidas por luvas.'],['Colete com medalhão','Colete marrom, gola e medalhão. Mãos descobertas.'],['Peitoral de aço','Peitoral cinza e túnica curta. Mãos descobertas.'],['Fallen · armadura','Armadura, ombreiras, mãos e botas do pacote enviado.'],['Espectral · túnica','Túnica com asas, braços, mãos e pernas do novo pacote.'],['Valquíria · armadura','Armadura alada, braços, luvas e botas do novo conjunto.'],['Mago · túnica roxa','Túnica e braços do ZIP; mãos e pernas da Fallen.']]},
 {id:'accessory',label:'Acessório',options:[['Nenhum','Mãos livres.'],['Cajado de cristal','Madeira e cristal azul.'],['Clava','Madeira escura com pontas.'],['Bastão Ranger','O acessório original do Ranger.'],['Espada Fallen','Espada original do pacote enviado.'],['Cajado espectral','Cajado mágico com efeito azul do novo pacote.'],...DATA.equipment.staves.map(item=>[item.name,'Cajado do pacote Craftpix, com tamanho e encaixe originais.']),['Espada Valquíria','Espada original do novo conjunto.'],['Tridente alternativo','Arma alternativa incluída no ZIP.']]},
 {id:'shield',label:'Escudo',options:[['Nenhum','Sem escudo.'],...DATA.equipment.shields.map(item=>[item.name,'Escudo com encaixe e movimento próprios; combina com qualquer arma.']),['Escudo Valquíria','Escudo original com o encaixe do conjunto enviado.']]},
 {id:'effect',label:'Cor do efeito',options:effects.map(([name])=>[name,'A cor aparece nas animações de ataque.'])}
];
const animationLabels={'Idle':'Em repouso','Idle Blinking':'Repouso · piscar','Walking':'Caminhando','Running':'Correndo','Slashing':'Ataque básico','Throwing':'Arremesso','Kicking':'Chute','Run Slashing':'Corrida + ataque','Run Throwing':'Corrida + arremesso','Sliding':'Deslizando','Jump Start':'Início do salto','Jump Loop':'No ar','Slashing in The Air':'Ataque no ar','Throwing in The Air':'Arremesso no ar','Falling Down':'Caindo','Hurt':'Recebendo dano','Dying':'Morte'};
const select=document.getElementById('animation');
for(const name of Object.keys(DATA.rig.frameCounts))select.add(new Option(animationLabels[name]||name,name));
select.value='Idle';

function makeCanvas(width,height){const c=document.createElement('canvas');c.width=width;c.height=height;return c}
// Equipped weapons keep their native movement, but remain visible in every action.
function selectedRig(){
 const rig=structuredClone(state.shield?DATA.shieldRig:DATA.rig);
 for(const animation of rig.animations)for(const timeline of Object.values(animation.timelines))for(const key of timeline){
  if(key.transform.file==='9')key.transform.a=1;
 }
 return rig;
}
function selectedSCML(){
 const doc=new DOMParser().parseFromString(state.shield?DATA.shieldSCML:DATA.scml,'application/xml');
 doc.querySelector('entity').setAttribute('name','CustomAvatar');
 doc.querySelectorAll('timeline key object[file="9"]').forEach(weapon=>weapon.setAttribute('a','1'));
 return new XMLSerializer().serializeToString(doc);
}
const weaponReachCache=new WeakMap();
function attackEffectScale(weapon){
 if(!state.accessory)return 1;
 if(weaponReachCache.has(weapon))return weaponReachCache.get(weapon);
 const c=makeCanvas(weapon.width,weapon.height),ctx=c.getContext('2d');ctx.drawImage(weapon,0,0);
 const pixels=ctx.getImageData(0,0,c.width,c.height).data;let tip=0;
 for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++)if(pixels[(y*c.width+x)*4+3]>=64)tip=Math.max(tip,x+1);
 // The native weapon grip is near x=48. Shorter weapons need a smaller arc
 // radius, keeping its origin fixed rather than shifting the whole slash.
 const scale=Math.max(.55,Math.min(1,(tip-48-18)/(372-48)));
 weaponReachCache.set(weapon,scale);return scale;
}
function tintedEffect(weapon){
 const source=registry[['original/SlashFX.png','packs/fallen/SlashFX.png','packs/spectral/SlashFX.png','packs/guardian/SlashFX.png'][state.effectShape??0]],c=makeCanvas(source.width,source.height),ctx=c.getContext('2d');ctx.drawImage(source,0,0);
 const image=ctx.getImageData(0,0,c.width,c.height),d=image.data,hex=effects[state.effect][1].slice(1),rgb=[0,2,4].map(i=>parseInt(hex.slice(i,i+2),16));
 for(let i=0;i<d.length;i+=4){if(!d[i+3])continue;const lum=(d[i]*.2126+d[i+1]*.7152+d[i+2]*.0722)/255,white=Math.max(0,(lum-.72)/.28)*.65;for(let k=0;k<3;k++)d[i+k]=Math.round(rgb[k]*(.6+.4*lum)*(1-white)+255*white)}
 ctx.putImageData(image,0,0);
 const scale=attackEffectScale(weapon);if(scale===1)return c;
 const fitted=makeCanvas(c.width,c.height),fx=fitted.getContext('2d');
 // All four native slash textures share the lower-left center of their arc.
 const originX=40,originY=484;fx.translate(originX,originY);fx.scale(scale,scale);fx.translate(-originX,-originY);fx.drawImage(c,0,0);
 return fitted;
}
const colorCache=new Map();
function colored(key,materials){
 const cacheKey=key+JSON.stringify(materials);if(colorCache.has(cacheKey))return colorCache.get(cacheKey);
 const source=registry[key],c=makeCanvas(source.width,source.height),ctx=c.getContext('2d');ctx.drawImage(source,0,0);
 const image=ctx.getImageData(0,0,c.width,c.height),d=image.data;
 for(const [material,hex] of Object.entries(materials)){
  const mask=registry['masks/'+key.replace(/\.png$/, '-'+material+'.png')];if(!mask)continue;
  const mc=makeCanvas(c.width,c.height),mx=mc.getContext('2d');mx.drawImage(mask,0,0);const m=mx.getImageData(0,0,c.width,c.height).data;
  const rgb=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
  for(let i=0;i<d.length;i+=4){if(!m[i+3])continue;const shade=m[i]/128;
   // Neutral gray shadows multiply the base; translucent white highlights screen it.
   for(let k=0;k<3;k++){const target=shade<=1?rgb[k]*shade:rgb[k]+(255-rgb[k])*(m[i]-128)/127;
    const flatMaterial=material==='hair'||material==='skin';
    const coverage=flatMaterial?m[i+3]/255:1;
    const under=flatMaterial?[27,26,24][k]:d[i+k];
    d[i+k]=Math.round(under*(1-coverage)+target*coverage);
   }
  }
 }
 ctx.putImageData(image,0,0);colorCache.set(cacheKey,c);if(colorCache.size>160)colorCache.delete(colorCache.keys().next().value);return c;
}
function applyLook(index){
 const looks=[{head:1,face:1,outfit:3,colors:{skin:'#d4b890',hair:'#414b4d',brows:'#333332',eyes:'#878559'}},{head:3,face:2,outfit:4,colors:{skin:'#d9bd9c',hair:'#7bb7de',brows:'#6689a0',eyes:'#809dba'}},{head:4,face:3,outfit:5,colors:{skin:'#e5c9a6',hair:'#edc34c',brows:'#a48639',eyes:'#869bb1'}}];
 state={...state,...structuredClone(looks[index])};update();
}
function applyFallen(){
 state={head:5,face:5,outfit:6,accessory:4,shield:0,effect:0,effectShape:1,colors:{skin:'#d3bcb4',hair:'#cec4be',brows:'#a59d98',eyes:'#92bed9'}};
 select.value='Idle';time=0;update();status.textContent='Conjunto Fallen completo, com todas as peças do ZIP.';
}
function applySpectral(){
 state={head:6,face:6,outfit:7,accessory:5,shield:0,effect:0,effectShape:2,colors:{skin:'#d3bcb4',hair:'#514646',brows:'#eae2df',eyes:'#92bed9'}};
 select.value='Idle';time=0;update();status.textContent='Conjunto Espectral completo, com todas as peças do novo ZIP.';
}
function applyGuardian(){
 state={head:7,face:7,outfit:8,accessory:46,shield:41,effect:0,effectShape:3,colors:{skin:'#c4996e',hair:'#73736b',brows:'#6c533d',eyes:'#3d514b'}};
 select.value='Idle';time=0;update();status.textContent='Valquíria completa, com espada e escudo independente.';
}
function applyTunicMage(){
 state={head:8,face:state.face||2,outfit:9,accessory:21,shield:0,effect:2,effectShape:0,colors:{skin:'#fccaa3',hair:'#ecdaca',brows:'#6c533d',eyes:'#654587'}};
 select.value='Idle';time=0;update();status.textContent='Mago roxo: cabeça, túnica e braços novos; mãos e pernas da Fallen.';
}
function buildColorControls(){
 const section=document.getElementById('colors');
 for(const [key,label]of Object.entries({skin:'Pele',hair:'Cabelo / capuz',brows:'Sobrancelhas',eyes:'Olhos'})){
  const row=document.createElement('label');row.className='colorControl';const text=document.createElement('span');text.textContent=label;
  const input=document.createElement('input');input.type='color';input.dataset.material=key;input.setAttribute('aria-label','Cor: '+label);input.value=state.colors[key];
  const output=document.createElement('output');output.textContent=input.value;
  input.oninput=()=>{state.colors={...state.colors,[key]:input.value};update()};row.append(text,output,input);section.append(row);
 }
}
// Each hairstyle retains its own original outline and integrated ear.
// Register the complete drawing to the former silver head's facial proportions.
function assembledHead(){
 const name=['bald','short','silver','blue','blond','fallen','spectral','guardian','mage-tunic'][state.head];
 const image=colored(state.head>=5?'packs/'+name+'/Head.png':'heads/'+name+'.png',{skin:state.colors.skin,hair:state.colors.hair});
 const placement=DATA.headRegistration.styles[name];
 const c=makeCanvas(480,480),ctx=c.getContext('2d');ctx.imageSmoothingQuality='high';
 ctx.setTransform(placement.scaleX,0,0,placement.scaleY,placement.offsetX,placement.offsetY);
 ctx.drawImage(image,0,0);return c;
}
// Face textures sit on the same bone as Head. Clip their paint to exposed
// skin in that shared coordinate system, so the original hair/outline wins.
const faceCoverageCache=new Map();
function textureMatrix(value,file){
 const n=(key,fallback)=>Number(value[key]??file[key]??fallback);
 return new DOMMatrix().translate(Number(value.x||0),-Number(value.y||0)).rotate(-Number(value.angle||0)).scale(Number(value.scale_x??1),Number(value.scale_y??1)).translate(-n('pivot_x',0)*Number(file.width),-(1-n('pivot_y',1))*Number(file.height));
}
function faceCoverage(){
 if(faceCoverageCache.has(state.head))return faceCoverageCache.get(state.head);
 const name=['bald','short','silver','blue','blond','fallen','spectral','guardian','mage-tunic'][state.head],placement=DATA.headRegistration.styles[name];
 const key=state.head===8?'masks/packs/mage-tunic/Head-face.png':state.head>=5?'masks/packs/'+name+'/Head-skin.png':'masks/heads/'+name+'-skin.png';
 const headMask=makeCanvas(480,480),headCtx=headMask.getContext('2d');headCtx.setTransform(placement.scaleX,0,0,placement.scaleY,placement.offsetX,placement.offsetY);headCtx.drawImage(registry[key],0,0);
 const base=DATA.rig.animations.find(a=>a.name==='Base');
 const transforms=Object.values(base.timelines).flat().map(k=>k.transform);
 const h=transforms.find(t=>t.file==='1'),f=transforms.find(t=>t.file==='4');
 const relative=textureMatrix(f,DATA.rig.files['4']).inverse().multiply(textureMatrix(h,DATA.rig.files['1']));
 const mask=makeCanvas(320,240),ctx=mask.getContext('2d');ctx.setTransform(relative);ctx.drawImage(headMask,0,0);
 faceCoverageCache.set(state.head,mask);return mask;
}
function faceBehindHair(image){
 const c=makeCanvas(320,240),ctx=c.getContext('2d');ctx.drawImage(image,0,0);ctx.globalCompositeOperation='destination-in';ctx.drawImage(faceCoverage(),0,0);return c;
}
function refreshTextures(){
 const images={};for(const [id,file] of Object.entries(DATA.rig.files))images[id]=registry['original/'+file.name];
 images['1']=assembledHead();
 for(const id of ['4','11','12']){
  if(!state.face)images[id]=makeCanvas(320,240);
  else images[id]=faceBehindHair(colored('faces/'+['focused','adventurer','veteran','ranger','fallen','spectral','guardian'][state.face-1]+'/'+DATA.rig.files[id].name,{brows:state.colors.brows,eyes:state.colors.eyes}));
 }
 if(state.outfit===0){for(const id of ['0','2','3','5','6','7','8'])images[id]=registry['outfits/basic/'+DATA.rig.files[id].name]}
 if(state.outfit===2){for(const id of ['0','2','3','5','6','7','8'])images[id]=registry['outfits/mage/'+DATA.rig.files[id].name]}
 if(state.outfit>=3&&state.outfit<=5){const kind=['leather','vest','plate'][state.outfit-3];images['0']=registry['outfits/'+kind+'/Body.png'];for(const id of ['2','5'])images[id]=registry['outfits/'+kind+'/'+DATA.rig.files[id].name];if(state.outfit!==3)for(const id of ['3','6'])images[id]=colored('hands/bare/'+DATA.rig.files[id].name,{skin:state.colors.skin})}
 if(state.outfit>=6&&state.outfit<=8){const pack=['fallen','spectral','guardian'][state.outfit-6];for(const id of ['0','2','3','5','6','7','8'])images[id]=colored('packs/'+pack+'/'+DATA.rig.files[id].name,{skin:state.colors.skin})}
 if(state.outfit===9){
  for(const id of ['0','2','5'])images[id]=registry['packs/mage-tunic/'+DATA.rig.files[id].name];
  for(const id of ['3','6'])images[id]=colored('packs/fallen/'+DATA.rig.files[id].name,{skin:state.colors.skin});
  for(const id of ['7','8'])images[id]=registry['packs/fallen/'+DATA.rig.files[id].name];
 }
 images['9']=state.accessory?registry[['','accessories/Staff.png','accessories/Club.png','original/Sword.png','packs/fallen/Sword.png','packs/spectral/Sword.png',...DATA.equipment.staves.map(item=>item.key),'packs/guardian/Sword.png','accessories/GuardianTrident.png'][state.accessory]]:makeCanvas(400,128);
 if(state.shield)images['13']=registry[state.shield===41?'packs/guardian/Shield.png':DATA.equipment.shields[state.shield-1].key];
 images['10']=tintedEffect(images['9']);player.images=images;player.rig=selectedRig();
}
function validState(value){
 if(!value||typeof value!=='object')throw Error('Arquivo de escolhas inválido.');
 value={shield:0,...value};
 for(const def of definitions)if(!Number.isInteger(value[def.id])||value[def.id]<0||value[def.id]>=def.options.length)throw Error('Escolha inválida: '+def.label);
 const colors={...defaultColors,...value.colors};for(const key of Object.keys(defaultColors))if(!/^#[0-9a-f]{6}$/i.test(colors[key]))throw Error('Cor inválida: '+key);
 const effectShape=value.effectShape??0;if(!Number.isInteger(effectShape)||effectShape<0||effectShape>3)throw Error('Forma de efeito inválida.');
 return {...Object.fromEntries(definitions.map(def=>[def.id,value[def.id]])),colors,effectShape};
}
function persist(){try{localStorage.setItem('chibi-creator-v1',JSON.stringify({...state,headOptionsVersion:2,faceOptionsVersion:2}))}catch{}}
function update(){
 refreshTextures();persist();
 const shape=document.getElementById('effectShape');if(shape)shape.value=String(state.effectShape??0);
 document.querySelectorAll('[data-material]').forEach(input=>{input.value=state.colors[input.dataset.material];input.previousElementSibling.textContent=input.value});
 for(const def of definitions){const item=document.querySelector('[data-option="'+def.id+'"]');item.querySelector('.choice').textContent=def.options[state[def.id]][0];item.querySelector('.description').textContent=def.options[state[def.id]][1];item.querySelector('.counter').textContent=(state[def.id]+1)+' / '+def.options.length;const clear=item.querySelector('.equipmentClear');if(clear)clear.disabled=state[def.id]===0}
 renderExpressionChoices();
 document.querySelectorAll('.swatch').forEach((button,i)=>button.setAttribute('aria-pressed',String(i===state.effect)));
 render();
}
function change(id,delta){const def=definitions.find(d=>d.id===id);state[id]=(state[id]+delta+def.options.length)%def.options.length;if(id==='effect'||id==='accessory'){select.value='Slashing';time=200;setView('assembled')}update()}
let activeCategory='head';
function activateEditor(name){
 document.querySelectorAll('[data-editor-tab]').forEach(button=>{const active=button.dataset.editorTab===name;button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;document.getElementById('panel-'+button.dataset.editorTab).hidden=!active});
}
function activateCategory(name){
 activeCategory=name;
 for(const def of definitions){const active=def.id===name,button=document.querySelector('[data-category="'+def.id+'"]');button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;document.querySelector('[data-option="'+def.id+'"]').hidden=!active}
 
}
function previewExpression(index){
 select.value=['Idle','Idle Blinking','Hurt'][index];time=[0,500,0][index];
 if(playing)document.getElementById('playPause').click();renderExpressionChoices();render();
}
function expressionThumbnail(file){
 if(state.face<5)return file;
 return {'Face 02.png':'Face 03.png','Face 03.png':'Face 02.png'}[file]||file;
}
function renderExpressionChoices(){
 const row=document.getElementById('expressionChoices');if(!row)return;row.replaceChildren();row.hidden=!state.face;if(!state.face)return;
 for(const [index,[name,file]] of [['Aberto','Face 01.png'],['Piscar','Face 03.png'],['Dano','Face 02.png']].entries()){
  const button=document.createElement('button');button.className='expressionChoice';button.setAttribute('aria-label','Ver expressão: '+name);button.setAttribute('aria-pressed',String(!playing&&select.value===['Idle','Idle Blinking','Hurt'][index]));
  const image=new Image();image.alt='';image.src=DATA.images['faces/'+['focused','adventurer','veteran','ranger','fallen','spectral','guardian'][state.face-1]+'/'+expressionThumbnail(file)];const label=document.createElement('span');label.textContent=name;button.append(image,label);button.onclick=()=>previewExpression(index);row.append(button);
 }
}
function setupEditorTabs(){
 const icons={head:'♟',face:'◉',outfit:'♜',accessory:'⚔',shield:'⛨',effect:'✧'},labels={head:'Cabelo',face:'Rosto',outfit:'Traje',accessory:'Arma',shield:'Escudo',effect:'Efeito'};
 for(const def of definitions){
  const button=document.createElement('button');button.dataset.category=def.id;button.id='category-'+def.id;button.setAttribute('role','tab');button.setAttribute('aria-controls','option-'+def.id);button.setAttribute('aria-label',def.label);
  const icon=document.createElement('span');icon.className='categoryIcon';icon.setAttribute('aria-hidden','true');icon.textContent=icons[def.id];const text=document.createElement('span');text.textContent=labels[def.id];button.append(icon,text);button.onclick=()=>activateCategory(def.id);document.getElementById('categoryTabs').append(button);
  const section=document.querySelector('[data-option="'+def.id+'"]');section.id='option-'+def.id;section.setAttribute('role','tabpanel');section.setAttribute('aria-labelledby',button.id);
 }
 document.querySelectorAll('[data-editor-tab]').forEach(button=>button.onclick=()=>activateEditor(button.dataset.editorTab));
 for(const list of document.querySelectorAll('[role="tablist"]'))list.addEventListener('keydown',event=>{
  const tabs=[...list.querySelectorAll('[role="tab"]')],index=tabs.indexOf(document.activeElement);if(index<0)return;let next;
  if(event.key==='ArrowRight')next=(index+1)%tabs.length;else if(event.key==='ArrowLeft')next=(index-1+tabs.length)%tabs.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=tabs.length-1;else return;
  event.preventDefault();tabs[next].click();tabs[next].focus();
 });
 activateCategory('head');
}

function buildControls(){
 for(const def of definitions){
  const section=document.createElement('section');section.className='option';section.dataset.option=def.id;
  const top=document.createElement('div');top.className='optionTop';const label=document.createElement('span');label.className='optionLabel';label.textContent=def.label;const counter=document.createElement('span');counter.className='counter';top.append(label,counter);
  const row=document.createElement('div');row.className='stepper';
  const previous=document.createElement('button');previous.className='arrow';previous.textContent='‹';previous.setAttribute('aria-label',def.label+' anterior');previous.onclick=()=>change(def.id,-1);
  const name=document.createElement('span');name.className='choice';name.setAttribute('aria-live','polite');
  const next=document.createElement('button');next.className='arrow';next.textContent='›';next.setAttribute('aria-label','Próximo: '+def.label);next.onclick=()=>change(def.id,1);
  row.append(previous,name,next);const desc=document.createElement('p');desc.className='description';section.append(top,row,desc);
  if(def.id==='shield'||def.id==='accessory'){
   const clear=document.createElement('button');clear.className='look equipmentClear';clear.textContent='Nenhum';clear.setAttribute('aria-label',def.id==='shield'?'Ficar sem escudo':'Ficar sem arma');
   clear.onclick=()=>{state[def.id]=0;update()};section.append(clear);
  }
  if(def.id==='effect'){const swatches=document.createElement('div');swatches.className='swatches';effects.forEach(([name,color],i)=>{const button=document.createElement('button');button.className='swatch';button.style.setProperty('--swatch',color);button.setAttribute('aria-label',name);button.onclick=()=>{state.effect=i;select.value='Slashing';time=200;setView('assembled');update()};swatches.append(button)});section.append(swatches)}
  if(def.id==='face'){const row=document.createElement('div');row.id='expressionChoices';row.className='expressionChoices';row.setAttribute('aria-label','Expressões do rosto');section.append(row)}
  if(def.id==='effect'){const label=document.createElement('label');label.className='effectShape';label.textContent='Traço do ataque';const shape=document.createElement('select');shape.id='effectShape';shape.setAttribute('aria-label','Traço do ataque');shape.add(new Option('Arco Ranger','0'));shape.add(new Option('Arco Fallen','1'));shape.add(new Option('Arco Espectral','2'));shape.add(new Option('Arco Valquíria','3'));shape.onchange=()=>{state.effectShape=Number(shape.value);select.value='Slashing';time=200;setView('assembled');update()};label.append(shape);section.append(label)}
  document.getElementById('options').append(section);
 }
}
function renderParts(){
 const ctx=canvas.getContext('2d');ctx.clearRect(0,0,900,900);
 for(const [i,[id,file]] of Object.entries(player.rig.files).entries()){
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
  await zip.add('CustomAvatar/config.json',JSON.stringify({version:2,state},null,2));
  await zip.add('CustomAvatar/PNG/Vector Parts/Animations.scml',selectedSCML());
  for(const [id,file] of Object.entries(player.rig.files)){const texture=makeCanvas(Number(file.width),Number(file.height));texture.getContext('2d').drawImage(player.images[id],0,0,texture.width,texture.height);await zip.add('CustomAvatar/PNG/Vector Parts/'+file.name,await blobOf(texture))}
  for(const [name,count] of Object.entries(DATA.rig.frameCounts)){
   const animation=player.rig.animations.find(a=>a.name===name);
   for(let frame=0;frame<count;frame++){
    if(cancelled)throw Error('Exportação cancelada.');
    player.draw(output,name,frame*Number(animation.length)/count);
    await zip.add(`CustomAvatar/PNG/PNG Sequences/${name}/0_CustomAvatar_${name}_${String(frame).padStart(3,'0')}.png`,await blobOf(output));
    status.textContent=`Exportando ${++done}/207 · ${animationLabels[name]||name}`;
   }
  }
  for(const [key,url] of Object.entries(DATA.images)){if(key.startsWith('imported/guardian/'))await zip.add('CustomAvatar/Source Packs/Valquiria/'+key.split('/').at(-1),new Uint8Array(await (await fetch(url)).arrayBuffer()))}
  await zip.add('CustomAvatar/Source Packs/Valquiria/Animations.scml',DATA.guardianSCML);
  await zip.add('CustomAvatar/Source Packs/Valquiria/Animations.autosave.scml',DATA.guardianViewsSCML);
  await zip.add('CustomAvatar/README.txt','Personagem montado no criador chibi.\n13 peças PNG (14 com escudo), rig SCML e 207 frames em 17 animações.\nO escudo é independente e usa o osso, pivô e movimento do conjunto Valquíria enviado pelo usuário.\nCabeça e cabelo são variantes de Head.png; o rosto é independente.\nTodos os rostos preservam as três expressões originais. Armas equipadas permanecem visíveis em todos os frames e usam os movimentos e pivôs originais.\nRig e peças de referência: Forest_Ranger_3 fornecido pelo usuário, sujeito à licença original Craftpix: https://craftpix.net/file-licenses/\nCajados e escudos adicionais: pacotes Craftpix 996712 e 781198 fornecidos pelo usuário; licença original Craftpix.\n');
  download(zip.finish(),'CustomAvatar-sprites.zip');status.textContent='Pronto: '+Object.keys(player.rig.files).length+' peças e 207 frames exportados.';
 }catch(error){status.textContent=error.message}finally{setBusy(false)}
}
document.getElementById('assembledView').onclick=()=>setView('assembled');document.getElementById('partsView').onclick=()=>setView('parts');
document.getElementById('playPause').onclick=()=>{playing=!playing;document.getElementById('playPause').textContent=playing?'Ⅱ':'▶';document.getElementById('playPause').setAttribute('aria-label',playing?'Pausar animação':'Reproduzir animação');renderExpressionChoices()};
select.onchange=()=>{time=0;renderExpressionChoices();render()};document.getElementById('speed').oninput=e=>{document.getElementById('speedValue').textContent=Number(e.target.value).toLocaleString('pt-BR')+'×'};
document.getElementById('reset').onclick=()=>{state={...defaults};select.value='Idle';time=0;status.textContent='Base careca e sem rosto.';update()};
document.getElementById('example').onclick=()=>{state={head:2,face:1,outfit:2,accessory:1,shield:0,effect:0,effectShape:0,colors:{...defaultColors}};select.value='Slashing';time=200;status.textContent='Mago montado no molde original, com o movimento completo do cajado.';update()};
document.getElementById('exportPNG').onclick=async()=>{try{const c=makeCanvas(900,900);player.draw(c,select.value,time);download(await blobOf(c),'CustomAvatar.png');status.textContent='PNG transparente exportado.'}catch(error){status.textContent=error.message}};
document.getElementById('exportZIP').onclick=exportSprites;document.getElementById('cancelExport').onclick=()=>{cancelled=true};
async function init(){
 try{
  await Promise.all(Object.entries(DATA.images).map(async([key,url])=>{const image=new Image();image.src=url;await image.decode();registry[key]=image}));
  try{const saved=localStorage.getItem('chibi-creator-v1');if(saved){const previous=JSON.parse(saved);if(previous.headOptionsVersion!==2)previous.head=[0,1,2,0,3,4][previous.head]??0;if(previous.faceOptionsVersion!==2&&(previous.face===5||previous.face===6))previous.face=1;state=validState(previous)}}catch{}
  buildControls();buildColorControls();setupEditorTabs();update();document.getElementById('loading').hidden=true;window.creatorReady=true;requestAnimationFrame(tick);
 }catch(error){document.getElementById('loading').textContent='Não foi possível carregar as peças: '+error.message}
}
init();
