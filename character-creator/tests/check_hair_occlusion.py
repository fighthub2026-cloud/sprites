"""Render real combinations and verify brows never paint over the hair."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/character-creator/index.html');page.wait_for_function('window.creatorReady')
 result=page.evaluate('''()=>{
 const render=(images,name,t)=>{const test=new SpriterPlayer();test.rig=DATA.rig;test.images=images;const c=makeCanvas(450,450);test.draw(c,name,t);return c.getContext('2d').getImageData(0,0,450,450).data};
 const blank=makeCanvas(1,1);let combinations=0,hairPixels=0;
 state.colors.hair='#2752e0';state.colors.brows='#f43c19';state.colors.eyes='#33a057';
 for(let head=1;head<7;head++)for(let face=1;face<7;face++){
  state.head=head;state.face=face;update();
  const headImages=Object.fromEntries(Object.keys(DATA.rig.files).map(id=>[id,id==='1'?player.images[id]:blank]));
  const combined={...headImages};for(const id of ['4','11','12'])combined[id]=player.images[id];
  for(const [name,t]of [['Idle',0],['Idle Blinking',500],['Hurt',0]]){
   const before=render(headImages,name,t),after=render(combined,name,t);let pixels=0;
   for(let i=0;i<before.length;i+=4)if(before[i+3]>240&&before[i+2]>before[i]*1.8&&before[i+2]>before[i+1]*1.2){
    for(let k=0;k<4;k++)if(Math.abs(before[i+k]-after[i+k])>1)throw Error('Hair painted over: head '+head+' face '+face+' '+name);
    pixels++;
   }
   if(pixels<500)throw Error('No hair pixels checked');hairPixels+=pixels;combinations++;
  }
 }
 return {combinations,hairPixels};
 }''');assert result['combinations']==108;assert not errors,errors;print('108 combinações/expressões: cabelo preservado em',result['hairPixels'],'pixels.');browser.close()
server.shutdown()
