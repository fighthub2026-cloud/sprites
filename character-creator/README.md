# Criador de personagens chibi

Abra `index.html` para usar o criador. O HTML inclui as imagens, o rig, os estilos
e o código; funciona sem importar ZIPs, instalar dependências ou buscar recursos
externos. Também pode ser servido como página estática.

O personagem começa careca, sem rosto, com roupa básica e sem acessório. As setinhas
alteram independentemente cabeça/cabelo/capuz, rosto, corpo/roupa, acessório e cor do efeito.

- 5 opções de cabeça, incluindo a base careca e o elmo original.
- 5 opções de rosto, incluindo a base sem rosto e as expressões do Ranger.
- 3 roupas, com braços e pernas correspondentes.
- 4 opções de acessório, incluindo mãos livres.
- 6 cores para o efeito de ataque.
- Prévia montada e visão das 13 peças.
- 17 animações, pausa e ajuste de velocidade.
- PNG transparente de 900 × 900, configuração JSON e exportação completa em ZIP.

O ZIP exportado contém 13 PNGs de peças, `Animations.scml`, 207 frames nas mesmas
17 pastas de animação do Forest Ranger, configuração e instruções. Os pivôs, os
ossos e os movimentos partem do SCML enviado pelo usuário. O acessório acompanha
a mão também durante a animação e na montagem exportada.

As opções de cabelo e capuz substituem a peça `Head.png`, como no padrão do pacote
original; o rosto é uma peça independente. Os rostos novos Concentrado, Aventureiro
e Veterano são poses faciais estáticas. A opção Rosto Ranger mantém as três
expressões originais, incluindo piscar e dano.

As escolhas ficam salvas localmente quando o navegador permite. Use Salvar escolhas
e Carregar escolhas salvas para transferir a configuração entre navegadores.

## Fontes e reconstrução

- `assets/original/`: as peças e o SCML do `Forest_Ranger_3.zip` fornecido.
- `assets/heads/`, `assets/faces/`, `assets/outfits/basic/`: novas texturas geradas
  e registradas para a montagem.
- `assets/outfits/mage/`, `assets/accessories/`: opções reutilizadas dos assets do projeto.
- `rig.json` e `catalog.json`: dados e imagens para o HTML independente.
- `template.html`, `style.css`, `app.js`: fontes da interface.

Execute `python character-creator/build.py` na raiz do repositório para reconstruir
`index.html`. A renderização usa `characters/goblin/player.js`, o reprodutor SCML
existente no projeto, embutido pelo script de construção.

Materiais originais Craftpix e rig fornecidos pelo usuário permanecem sujeitos à
licença do pacote original: https://craftpix.net/file-licenses/.
