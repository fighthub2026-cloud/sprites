ELF MAGE / ELFO MAGO

Estrutura inspirada no pacote Orc fornecido:
AI: fonte SVG montada, PDF compatível com Illustrator e SVGs individuais.
EPS: 13 peças vetorizadas em EPS.
PNG/Vector Parts: 13 texturas e Animations.scml.
PNG/PNG Sequences: 207 frames transparentes de 900 x 900, nas mesmas 17 animações.
Unity Package: pacote de sprites e reprodutor de sequências.
Sources: desenho-base e texturas geradas antes do corte e registro no rig.

preview.gif: Idle Blinking em loop, fundo cinza, quadro de 600 x 338.
casting.gif: exemplo de ataque com cajado e efeito de magia.
index.html: reprodução interativa de todas as animações via HTTP.

As referências visuais inspiram as proporções chibi e o estilo de contorno.
Cabelo, roupa, cajado, efeito e texturas do elfo são novos; o rig e as durações
partem do SCML do Orc fornecido pelo usuário.

Para visualizar, execute na raiz do repositório:
python -m http.server 8765 --bind 127.0.0.1
Abra /characters/elf-mage/ no servidor local.

Para reexportar os PNGs, com o servidor ativo:
python tools/export_elf_mage.py
Requer Playwright e Chromium. CHROMIUM_PATH substitui /usr/bin/chromium.

As 17 sequências preservam os nomes do Orc para facilitar integração. Slashing e
Throwing representam movimentos do cajado; não foi implementada lógica de projéteis,
dano ou combate. O SCML original é a base dos movimentos, não uma animação nova
desenhada à mão para cada ação.
