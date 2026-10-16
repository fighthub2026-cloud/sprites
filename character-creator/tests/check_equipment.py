"""Check every new selection, old saves, animation attachment and ZIP export."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import base64
import io
import json
import zipfile
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
try:
    with TemporaryDirectory() as temp, sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/character-creator/index.html')
        page.wait_for_function('window.creatorReady')
        # Existing saved characters have no shield field and must keep all choices.
        page.evaluate('''()=>{applySpectral();const saved=JSON.parse(localStorage.getItem('chibi-creator-v1'));delete saved.shield;localStorage.setItem('chibi-creator-v1',JSON.stringify(saved))}''')
        page.reload()
        page.wait_for_function('window.creatorReady')
        assert page.evaluate('[state.head,state.face,state.outfit,state.accessory,state.shield]') == [6,6,7,5,0]
        page.evaluate('''()=>{
          playing=false;
          if(DATA.equipment.staves.length!==40||DATA.equipment.shields.length!==40)throw Error('Incomplete packs');
          for(let i=0;i<40;i++){
            state.accessory=6+i;state.shield=i+1;update();
            if(player.images['9']!==registry[DATA.equipment.staves[i].key])throw Error('Wrong staff');
            const bare=colored('packs/spectral/Right Hand.png',{skin:state.colors.skin});
            if(player.images['3'].toDataURL()!==bare.toDataURL())throw Error('Shield was painted onto the hand');
            if(player.images['13']!==registry[DATA.equipment.shields[i].key]||player.rig.files['13'].width!=='160')throw Error('Wrong shield attachment');
            for(const name of Object.keys(DATA.rig.frameCounts))player.draw(canvas,name,200);
          }
          state.shield=0;update();
          if(player.images['3'].toDataURL()!==colored('packs/spectral/Right Hand.png',{skin:state.colors.skin}).toDataURL())throw Error('Shield removal changed hand');
          state.accessory=45;state.shield=40;update();
        }''')
        page.reload()
        page.wait_for_function('window.creatorReady')
        assert page.evaluate('[state.accessory,state.shield]') == [45,40]
        for category in ['accessory', 'shield']:
            page.evaluate('name=>{state[name]=definitions.find(d=>d.id===name).options.length-1;update();activateCategory(name)}', category)
            page.locator(f'[data-option={category}] .arrow').last.click()
            assert page.evaluate('name=>state[name]', category) == 0
            page.locator(f'[data-option={category}] .arrow').first.click()
        page.evaluate("applyGuardian();previewExpression(0)")
        # New parts combine with all existing heads and outfits without breaking poses.
        page.evaluate('''()=>{
          const read=image=>{const c=makeCanvas(image.width,image.height);c.getContext('2d').drawImage(image,0,0);return c.getContext('2d').getImageData(0,0,c.width,c.height).data};
          const changed=(a,b)=>a.some((v,i)=>v!==b[i]);
          const before=Object.fromEntries(['0','1','3','6'].map(id=>[id,read(player.images[id])]));state.colors.skin='#e030a0';update();
          if(!changed(before['0'],read(player.images['0']))||!changed(before['1'],read(player.images['1'])))throw Error('Valkyrie skin not recolored');
          if(changed(before['3'],read(player.images['3']))||changed(before['6'],read(player.images['6'])))throw Error('Valkyrie gloves recolored as skin');
          for(let head=0;head<8;head++){state.head=head;update();for(const name of ['Idle','Idle Blinking','Hurt'])player.draw(canvas,name,200)}
          state.head=7;for(let outfit=0;outfit<9;outfit++){state.outfit=outfit;update();for(const name of Object.keys(DATA.rig.frameCounts))player.draw(canvas,name,200)}
          applyGuardian();
        }''')
        expected = page.evaluate('''()=>Object.fromEntries(Object.entries(player.rig.files).map(([id,file])=>{const c=makeCanvas(+file.width,+file.height);c.getContext('2d').drawImage(player.images[id],0,0);return[file.name,c.toDataURL()]}))''')
        with page.expect_download(timeout=180000) as download:
            page.locator('#exportZIP').click()
        target = Path(temp)/'equipment.zip'
        download.value.save_as(target)
        with zipfile.ZipFile(target) as archive:
            assert archive.testzip() is None
            assert len([n for n in archive.namelist() if '/PNG Sequences/' in n]) == 207
            config = json.loads(archive.read('CustomAvatar/config.json'))
            assert config['state']['accessory'] == 46 and config['state']['shield'] == 41
            assert config['state']['head'] == 7 and config['state']['face'] == 7 and config['state']['outfit'] == 8
            assert len(expected) == 14
            assert archive.read('CustomAvatar/Source Packs/Valquiria/Shield.png') == (ROOT/'character-creator/assets/imported/guardian/Shield.png').read_bytes()
            assert archive.read('CustomAvatar/Source Packs/Valquiria/Head.png') == (ROOT/'character-creator/assets/packs/guardian/Head.png').read_bytes()
            for name, url in expected.items():
                actual = np.array(Image.open(io.BytesIO(archive.read('CustomAvatar/PNG/Vector Parts/'+name))))
                reference = np.array(Image.open(io.BytesIO(base64.b64decode(url.split(',')[1]))))
                assert np.array_equal(actual, reference), name
        assert not errors, errors
        browser.close()
    print('40 cajados e 40 escudos; 17 ações; escolhas antigas preservadas; seleção persistida; ZIP com arma, escudo e 207 frames validado.')
finally:
    server.shutdown()
