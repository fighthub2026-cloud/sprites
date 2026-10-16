from playwright.sync_api import sync_playwright
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from tempfile import TemporaryDirectory
import zipfile
ROOT=Path(__file__).resolve().parents[2]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
artifacts=TemporaryDirectory(prefix='creator-head-')
out=Path(artifacts.name)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/character-creator/index.html');page.wait_for_function('window.creatorReady')
 result=page.evaluate('''()=>{
 const pixels=image=>{const c=makeCanvas(image.width,image.height);c.getContext('2d').drawImage(image,0,0);return c.getContext('2d').getImageData(0,0,c.width,c.height).data};
 let checks=0;
 for(const skin of ['#282828','#dbbe9a','#8b5038']){
 state.colors.skin=skin;state.head=0;state.face=1;update();const base=pixels(player.images['1']),face=pixels(player.images['4']);
 for(let h=0;h<5;h++){
  state.head=h;update();const head=pixels(player.images['1']);
  // Jaw, lower cheek and chin must be pixel-identical, not merely equal bounds.
  for(let y=310;y<480;y++)for(let x=230;x<480;x++)for(let k=0;k<4;k++){const i=(y*480+x)*4+k;if(base[i]!==head[i])throw Error('Jaw changed: '+h+' '+x+','+y)}
  for(let y=280;y<350;y++)for(let x=85;x<145;x++)for(let k=0;k<4;k++){const i=(y*480+x)*4+k;if(base[i]!==head[i])throw Error('Ear changed')}
  const afterFace=pixels(player.images['4']);if(face.some((v,i)=>v!==afterFace[i]))throw Error('Features changed');checks++;
 }
 }return checks;
 }''');assert result==15
 page.evaluate('state.head=3;update()')
 with page.expect_download(timeout=180000) as d:page.locator('#exportZIP').click()
 d.value.save_as(out/'creator-shared-head.zip');assert not errors;b.close()
with zipfile.ZipFile(out/'creator-shared-head.zip') as z:
 assert z.testzip() is None
 assert len([n for n in z.namelist() if '/PNG Sequences/' in n])==207
 assert len([n for n in z.namelist() if '/Vector Parts/' in n and n.endswith('.png')])==13
print('15 combinações: orelha, mandíbula, queixo e feições idênticos; ZIP válido com 13 peças e 207 frames.')

server.shutdown()
artifacts.cleanup()
