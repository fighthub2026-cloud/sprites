# Criador de personagens chibi

Abra `index.html` para usar o criador. O HTML inclui as imagens, o rig, os estilos
e o código; funciona sem importar ZIPs, instalar dependências ou buscar recursos
externos. Também pode ser servido como página estática.

O personagem começa careca, sem rosto, com roupa básica e sem acessório. As setinhas
alteram independentemente cabeça/cabelo/capuz, rosto, corpo/roupa, acessório e cor do efeito.

- 6 opções de cabeça: careca, curto preto, prateado, capuz, azul e loiro.
- 5 opções de rosto, incluindo a base sem rosto e as expressões do Ranger.
- 3 roupas, com braços e pernas correspondentes.
- 4 opções de acessório, incluindo mãos livres.
- 6 cores para o efeito de ataque.
- Prévia montada e visão das 13 peças.
- 17 animações, pausa e ajuste de velocidade.
- PNG transparente de 900 × 900, configuração JSON e exportação completa em ZIP.

O ZIP exportado contém 13 PNGs de peças, `Animations.scml`, 207 frames nas mesmas
17 pastas de animação do Forest Ranger, configuração e instruções. Os pivôs, os
ossos e os movimentos partem do SCML enviado pelo usuário. A arma preserva exatamente a hierarquia, os pivôs, a visibilidade e os keyframes
do original, inclusive o arco completo nos ataques em pé, correndo e no ar.
Cajado e clava ocupam o mesmo alcance da textura original.

As opções de cabelo e capuz substituem a peça `Head.png`, como no padrão do pacote
original; o rosto é uma peça independente. Todos os rostos com feições mantêm as três expressões originais, incluindo piscar
e dano, com o mesmo registro entre elas.

As escolhas ficam salvas localmente quando o navegador permite. Use Salvar escolhas
e Carregar escolhas salvas para transferir a configuração entre navegadores.

## Fontes e reconstrução

- `assets/original/`: as peças e o SCML do `Forest_Ranger_3.zip` fornecido.
- `assets/heads/`, `assets/faces/`, `assets/outfits/basic/`: novas texturas geradas
  e registradas para a montagem.
- `assets/outfits/basic/` e `assets/outfits/mage/`: variantes de cor das sete peças originais; silhuetas, luvas, encaixes e alfa preservados.
- `prepare_native.py`: prepara paletas, expressões e alcance dos acessórios. O contorno comum é `#1b1a18`.
- `assets/accessories/`: cajado simples do mesmo conjunto, clava e bastão Ranger.
- `sources/`: atlas gerados de cabeças, peças do mago e rostos, antes do corte e registro.
- `rig.json` e `catalog.json`: dados e imagens para o HTML independente.
- `template.html`, `style.css`, `app.js`: fontes da interface.

Execute `python character-creator/build.py` na raiz do repositório para reconstruir
`index.html`. A renderização usa `characters/goblin/player.js`, o reprodutor SCML
existente no projeto, embutido pelo script de construção.

Materiais originais Craftpix e rig fornecidos pelo usuário permanecem sujeitos à
licença do pacote original: https://craftpix.net/file-licenses/.

Para reconstruir as texturas refinadas a partir dos atlas, execute `python character-creator/pack_refinement.py` antes de `build.py`. Esse passo de preparação requer Pillow, NumPy, SciPy e ImageMagick; a página pronta não precisa dessas ferramentas.
