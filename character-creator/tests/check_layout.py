from playwright.sync_api import sync_playwright
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
artifacts=TemporaryDirectory(prefix='creator-layout-')
out=Path(artifacts.name)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 for w,h in [(1920,1080),(1440,900),(1280,720),(1024,600),(390,844),(375,667),(360,640),(320,568),(844,390),(667,375),(568,320)]:
  page.set_viewport_size({'width':w,'height':h});page.goto(f'http://127.0.0.1:{server.server_port}/character-creator/index.html');page.wait_for_function('window.creatorReady');page.evaluate('playing=false;applyLook(1)')
  for tab in ['appearance','colors','files']:
   page.locator('#tab-'+tab).click()
   checks=page.evaluate('''()=>{
   const hidden=e=>e.closest('[hidden]')!==null;
   const bad=[...document.querySelectorAll('button,input:not([type=file]),select,.variant,.colorControl')].filter(e=>!hidden(e)&&e.getBoundingClientRect().width>0).filter(e=>{const r=e.getBoundingClientRect();if(r.left<0||r.top<0||r.right>innerWidth+1||r.bottom>innerHeight+1)return true;const panel=e.closest('.editorBody');if(panel){const p=panel.getBoundingClientRect();if(r.bottom>p.bottom+1)return true}return false}).map(e=>e.id||e.className);
   return {pageFits:document.documentElement.scrollHeight<=innerHeight&&document.documentElement.scrollWidth<=innerWidth,bad};}''')
   assert checks['pageFits'] and not checks['bad'],(w,h,tab,checks)
  page.locator('#tab-appearance').click()
  for cat in ['head','face','outfit','accessory','effect']:
   page.locator('[data-category='+cat+']').click();page.locator('.variant').last.click();assert page.evaluate('activeCategory')==cat
  page.evaluate('applyLook(1);activateCategory("head")');page.screenshot(path=str(out/f'ui-{w}x{h}.png'))
  print(w,h,'3 abas, 5 categorias e controles sem cortes OK')
 # Download and keyboard navigation still work with the tab panels.
 page.locator('#tab-appearance').focus();page.keyboard.press('ArrowRight');assert page.locator('#tab-colors').get_attribute('aria-selected')=='true'
 with page.expect_download() as download:page.locator('#exportPNG').click()
 download.value.save_as(out/'new-ui-export.png')
 assert not errors,errors;b.close()

server.shutdown()
artifacts.cleanup()
