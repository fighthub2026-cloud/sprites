"""Ensure the slash stays inside weapon tips at the end of the basic attack."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(Path(__file__).resolve().parents[2])));Thread(target=s.serve_forever,daemon=True).start()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1280,'height':800});page.goto(f'http://127.0.0.1:{s.server_port}/character-creator/index.html');page.wait_for_function('window.creatorReady');result=page.evaluate('''()=>{
 playing=false;const extents=id=>{const c=makeCanvas(900,900),test=new SpriterPlayer();test.rig=player.rig;test.images=Object.fromEntries(Object.keys(player.images).map(key=>[key,key===id?player.images[key]:makeCanvas(1,1)]));test.draw(c,'Slashing',200);const d=c.getContext('2d').getImageData(0,0,900,900).data;let max=0;for(let y=0;y<900;y++)for(let x=0;x<900;x++)if(d[(y*900+x)*4+3]>40)max=Math.max(max,x);return max};let checked=0;const overshoots=[];
 for(let a=1;a<48;a++){state.accessory=a;for(let effectShape=0;effectShape<4;effectShape++){state.effectShape=effectShape;update();let weapon=extents('9'),effect=extents('10');if(effect>weapon)overshoots.push({a,effectShape,weapon,effect});checked++}}
 applyLook(2);state.accessory=26;state.shield=1;state.effectShape=0;update();select.value='Slashing';time=200;render();return {checked,overshoots};
 }''');assert result['checked']==188 and not result['overshoots'],result;print('188 combinações: extremidade do efeito dentro da ponta da arma.');b.close()
s.shutdown()
