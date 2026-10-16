"""Equipment stays visible across actions, appearance changes and exported rigs."""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/character-creator/index.html');page.wait_for_function('window.creatorReady')
  result=page.evaluate('''()=>{
   playing=false;applyTunicMage();let frames=0;
   const c=makeCanvas(900,900),ctx=c.getContext('2d'),draw=ctx.drawImage;let rendered=0;
   ctx.drawImage=function(image,...args){if(image===player.images['9']){if(this.globalAlpha<.999)throw Error('Weapon hidden/faded');rendered++}return draw.call(this,image,...args)};
   for(const accessory of [1,21,46])for(const shield of [0,1]){
    state.accessory=accessory;state.shield=shield;update();
    const doc=new DOMParser().parseFromString(selectedSCML(),'application/xml');
    for(const node of doc.querySelectorAll('timeline key object[file="9"]'))if(node.getAttribute('a')!=='1')throw Error('SCML hides weapon');
    const source=shield?DATA.shieldRig:DATA.rig;
    for(const a of player.rig.animations){const original=source.animations.find(x=>x.name===a.name);for(const [id,keys]of Object.entries(a.timelines))for(const k of keys){const expected=structuredClone(original.timelines[id].find(x=>x.id===k.id));if(expected.transform.file==='9')expected.transform.a=1;if(JSON.stringify(k)!==JSON.stringify(expected))throw Error('Native movement changed')}}
    for(const [name,count]of Object.entries(DATA.rig.frameCounts)){
     const a=player.rig.animations.find(a=>a.name===name);
     for(let frame=0;frame<count;frame++){const before=rendered;player.draw(c,name,frame*Number(a.length)/count);if(rendered!==before+1)throw Error('Missing weapon frame '+name+' '+frame);frames++}
    }
   }
   state.accessory=21;state.shield=1;update();
   for(const id of ['head','outfit']){const count=definitions.find(d=>d.id===id).options.length;for(let i=0;i<count;i++){change(id,1);if(state.accessory!==21||state.shield!==1)throw Error('Appearance removed equipment');const a=player.rig.animations.find(a=>a.name==='Idle');for(const keys of Object.values(a.timelines))for(const k of keys)if(k.transform.file==='9'&&k.transform.a!==1)throw Error('Appearance hid weapon')}}
   return frames;
  }''')
  assert result==1242,result
  page.evaluate('activateCategory("shield")');page.get_by_role('button',name='Ficar sem escudo',exact=True).click();assert page.evaluate('state.shield')==0;assert page.evaluate("Object.keys(player.rig.files).length")==13
  page.evaluate('activateCategory("accessory")');page.get_by_role('button',name='Ficar sem arma',exact=True).click();assert page.evaluate('state.accessory')==0
  assert page.evaluate("!player.images['9'].getContext('2d').getImageData(0,0,400,128).data.some((v,i)=>i%4===3&&v)")
  page.reload();page.wait_for_function('window.creatorReady');assert page.evaluate('[state.accessory,state.shield]')==[0,0]
  assert not errors,errors;browser.close();print('1242 frames com arma visível; cabelo/traje preservam equipamentos; Nenhum retira arma/escudo e persiste; SCML confere.')
finally:server.shutdown()
