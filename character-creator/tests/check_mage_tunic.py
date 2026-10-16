from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
import zipfile,json,base64,io,xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
artifacts=TemporaryDirectory(prefix='creator-mage-tunic-')
OUT=Path(artifacts.name)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/character-creator/index.html');page.wait_for_function('window.creatorReady');page.evaluate('applyTunicMage()');page.reload();page.wait_for_function('window.creatorReady');assert page.evaluate('[state.head,state.face,state.outfit,state.accessory,state.effectShape]')==[0,2,9,21,0]
 for category,last in [('head',0),('face',2),('outfit',9),('accessory',21)]:
  page.evaluate('name=>activateCategory(name)',category);page.locator('[data-option='+category+'] .arrow').last.click();assert page.evaluate('name=>state[name]',category)==(last+1)%page.evaluate('name=>definitions.find(d=>d.id===name).options.length',category);page.locator('[data-option='+category+'] .arrow').first.click();assert page.evaluate('name=>state[name]',category)==last
 result=page.evaluate('''()=>{
 const read=image=>{const c=makeCanvas(image.width,image.height);c.getContext('2d').drawImage(image,0,0);return [...c.getContext('2d').getImageData(0,0,c.width,c.height).data]};
 const changed=(a,b)=>a.some((v,i)=>v!==b[i]);applyTunicMage();
 for(const id of ['3','6'])if(changed(read(player.images[id]),read(colored('packs/fallen/'+DATA.rig.files[id].name,{skin:state.colors.skin}))))throw Error('Hands must be Fallen');
 for(const id of ['7','8'])if(player.images[id]!==registry['packs/fallen/'+DATA.rig.files[id].name])throw Error('Legs must be Fallen');
 for(const id of ['0','2','5'])if(player.images[id]!==registry['packs/mage-tunic/'+DATA.rig.files[id].name])throw Error('Wrong uploaded component');
 state.head=2;update();
 const before=Object.fromEntries(['0','1','2','3','5','6','7','8'].map(id=>[id,read(player.images[id])]));state.colors.skin='#472e27';update();
 const skin=['1','3','6'].every(id=>changed(before[id],read(player.images[id])))&&['0','2','5','7','8'].every(id=>!changed(before[id],read(player.images[id])));
 const hand=read(player.images['6']),head=read(player.images['1']);state.colors.hair='#277de0';update();const independent=changed(head,read(player.images['1']))&&!changed(hand,read(player.images['6']));
 let animations=0;const c=makeCanvas(900,900);for(const name of Object.keys(DATA.rig.frameCounts)){player.draw(c,name,100);const d=c.getContext('2d').getImageData(0,0,900,900).data;if(!d.some((v,i)=>i%4===3&&v>128))throw Error('Empty '+name);animations++}
 for(let head=0;head<8;head++){state.head=head;update();for(const name of ['Idle','Slashing','Hurt'])player.draw(c,name,150)}
 return {skin,independent,animations};
 }''');assert result=={'skin':True,'independent':True,'animations':17},result
 page.evaluate('applyTunicMage();activateCategory("effect")');page.locator('#effectShape').select_option('0');assert page.evaluate('state.effectShape')==0;page.locator('#effectShape').select_option('1');assert page.evaluate('state.effectShape')==1
 expected=page.evaluate('''()=>Object.fromEntries(Object.entries(DATA.rig.files).map(([id,file])=>{const c=makeCanvas(Number(file.width),Number(file.height));c.getContext('2d').drawImage(player.images[id],0,0);return[file.name,c.toDataURL()]}))''')
 with page.expect_download(timeout=180000) as d:page.locator('#exportZIP').click()
 d.value.save_as(OUT/'creator-mage-tunic.zip');assert not errors,errors
 page.evaluate("()=>{const saved=JSON.parse(localStorage.getItem('chibi-creator-v1'));saved.head=8;localStorage.setItem('chibi-creator-v1',JSON.stringify(saved))}")
 page.reload();page.wait_for_function('window.creatorReady');assert page.evaluate('[state.head,state.outfit,state.accessory]')==[2,9,21]
 assert page.evaluate("definitions.find(d=>d.id==='head').options.length")==8
 b.close()
with zipfile.ZipFile(OUT/'creator-mage-tunic.zip') as z:
 assert z.testzip() is None;assert len([n for n in z.namelist() if '/PNG Sequences/' in n])==207
 config=json.loads(z.read('CustomAvatar/config.json'));assert config['state']['head']==7 and config['state']['outfit']==9 and config['state']['effectShape']==1
 for name,url in expected.items():
  actual=np.array(Image.open(io.BytesIO(z.read('CustomAvatar/PNG/Vector Parts/'+name))).convert('RGBA'));ref=np.array(Image.open(io.BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGBA'));assert np.array_equal(actual,ref),name
 print('Conjunto persistido; setas e mistura de peças; mãos e pernas da Fallen; pele e cabelo independentes; 17 ações; 13 peças idênticas à prévia e 207 frames exportados com CRC válido.')

server.shutdown()
artifacts.cleanup()
