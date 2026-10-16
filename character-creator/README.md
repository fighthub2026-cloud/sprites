# Criador de personagens chibi

Abra `index.html` para usar o criador. O HTML inclui as imagens, o rig, os estilos
e o código; funciona sem importar ZIPs, instalar dependências ou buscar recursos
externos. Também pode ser servido como página estática.

O personagem começa careca, sem rosto, com roupa básica e sem acessório. As setinhas
alteram independentemente cabeça/cabelo, rosto, corpo/roupa, acessório e cor do efeito.

- 7 opções de cabeça: careca, curto preto, prateado, azul, loiro, Fallen e capuz Espectral.
- 7 opções de rosto: Sem rosto, Severo, Determinado, Resoluto, Ranger, Fallen e Espectral.
- 8 roupas: básica, Ranger, mago, couro com rebites, colete com medalhão, peitoral de aço, armadura Fallen e túnica Espectral.
- Seletores independentes de pele, cabelo, sobrancelhas e olhos. Máscaras de materiais preservam contornos e convertem sombras e brilhos em sobreposições neutras.
- Pele compartilhada por cabeça e mãos descobertas dos trajes Colete e Peitoral; as luvas não são recoloridas.
- Três combinações prontas inspiradas nas referências (Couro, Azul e Loiro).
- 6 opções de acessório, incluindo mãos livres, espada Fallen e cajado Espectral.
- 6 cores e 3 traços para o efeito de ataque (Ranger, Fallen e Espectral).
- Prévia montada e visão das 13 peças.
- 17 animações, pausa e ajuste de velocidade.
- PNG transparente de 900 × 900, configuração JSON e exportação completa em ZIP.

O ZIP exportado contém 13 PNGs de peças, `Animations.scml`, 207 frames nas mesmas
17 pastas de animação do Forest Ranger, configuração e instruções. Os pivôs, os
ossos e os movimentos partem do SCML enviado pelo usuário. A arma preserva exatamente a hierarquia, os pivôs, a visibilidade e os keyframes
do original, inclusive o arco completo nos ataques em pé, correndo e no ar.
Cajado e clava ocupam o mesmo alcance da textura original.

As opções de cabelo substituem a peça `Head.png`, como no padrão do pacote
original; o rosto é uma peça independente. Todos os rostos com feições mantêm as três expressões originais, incluindo piscar
e dano, com o mesmo registro entre elas.

As escolhas ficam salvas localmente quando o navegador permite. O ZIP inclui
a configuração JSON com a paleta escolhida.

## Fontes e reconstrução

- `assets/original/`: as peças e o SCML do `Forest_Ranger_3.zip` fornecido.
- `assets/heads/` e `assets/faces/`: cabeças registradas e expressões animadas.
- `assets/masks/`: máscaras por material com alfa, sombras e brilhos neutros.
- `assets/outfits/leather/`, `vest/` e `plate/`: três novos desenhos de traje, registrados nos mesmos pivôs.
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

Para preparar os novos trajes e máscaras: `python character-creator/prepare_outfits.py` e `python character-creator/prepare_materials.py`, antes de `build.py`. O ZIP exporta as cores aplicadas e o JSON inclui a paleta; escolhas já salvas no navegador continuam aceitas.

As máscaras de cabelo separam o material pelos tons de origem e sua mistura com o contorno, incluindo mechas escuras. O preenchimento usa tons planos neutros; nas bordas, a nova cor é combinada com o contorno, sem resíduos da cor anterior. Verificação: `python -m unittest discover -s character-creator/tests -v`. A preparação das máscaras requer também SciPy.


## Interface em uma tela

A oficina ocupa a altura disponível (`100dvh`) em computador e celular, inclusive
na horizontal. As abas Aparência e Cores organizam os controles sem
rolagem. Em Aparência, escolha uma categoria (cabelo, rosto, traje, arma ou efeito)
e use as setas para escolher a peça. PNG e ZIP ficam sempre disponíveis na
base do painel. As abas também aceitam setas do teclado, Home e End.

A interface usa cenário e botões em CSS, sem fontes ou imagens remotas. Todos os
recursos anteriores continuam no HTML independente. Para verificar o encaixe em
11 tamanhos de tela, navegação e exportação PNG, execute
`python character-creator/tests/check_layout.py` (Playwright e Chromium em
`/usr/bin/chromium`). O teste inicia e encerra seu próprio servidor local.

A aba Arquivos foi removida. As escolhas continuam salvas automaticamente no navegador e incluídas no ZIP. O efeito pode ser escolhido pelas setas ou amostras de cor, sem uma segunda grade de botões.

Os rostos Severo, Determinado e Resoluto foram redesenhados a partir das referências
com três expressões cada. Em Rosto, use Aberto, Piscar e Dano para pausar e conferir
a expressão; retome a reprodução para vê-las nas ações originais. O ZIP sempre
exporta todas as expressões nos momentos definidos pelo rig.
`prepare_expressions.py` registra o atlas `sources/expression-options.png` e gera
máscaras independentes de sobrancelhas e íris, preservando a parte branca dos olhos.
`prepare_materials.py` também executa essa preparação ao final. O capuz foi retirado
da lista de cabelos; escolhas antigas são migradas preservando azul e loiro.

As grades de miniaturas foram removidas de todas as categorias. A seleção das peças permanece nas setas de cada categoria.

A pele da cabeça e das mãos descobertas usa o mesmo tratamento plano do cabelo:
base, sombra e brilho neutros, com cobertura parcial apenas junto ao contorno.
As máscaras de cabelo e pele são separadas e não se sobrepõem. O processamento
não reaproveita a cor original nas bordas nem reproduz seu ruído no preenchimento.
Os testes `test_skin_masks.py` verificam cobertura, separação dos materiais e
preservação dos contornos.


## Proporções pela versão prateada

Cada opção conserva o desenho completo original de cabelo, cabeça e orelha,
incluindo seus contornos. Nos cortes curtos, a orelha aparece normalmente; nos
cortes que a cobrem, a sobreposição e o acabamento seguem as mechas. A versão prateada é a
referência de proporção e permanece sem transformação. `head-registration.json`
alinha a largura e a posição da parte inferior do rosto das outras opções à
referência, sem recortar ou redesenhar os cabelos. Feições, expressões e pivôs
mantêm o mesmo registro. O PNG `Head.png` exportado já inclui essa montagem.

A base careca ampliada e as camadas de cabelo extraídas da versão anterior foram
removidas. Teste: `python -m unittest discover -s character-creator/tests -v`.

O rosto Astuto usa olhos estreitos e sorriso de canto inspirados na referência.
Inclui aberto, piscar e dano, com máscaras independentes de sobrancelhas e íris.
`prepare_sly_face.py` registra o atlas `sources/sly-expressions.png`; a preparação
geral de materiais também chama esse passo.

Astuto e Perspicaz foram removidos do catálogo. Escolhas salvas desses rostos
são migradas para Severo, preservando cabelo, roupa, acessórios e cores.


## Conjunto importado do Vector Parts.zip

O botão **Fallen** monta o conjunto completo do pacote enviado: cabelo, três
expressões, corpo, dois braços, duas mãos, duas pernas, espada e efeito. Cada
opção também pode ser escolhida pelas setas e combinada com os itens anteriores.
Em Efeito, o seletor Traço do ataque escolhe o desenho do arco, independentemente
da cor. As áreas descobertas do peito e mãos acompanham a pele; luvas e armadura
mantêm seus materiais.

- `assets/imported/forest-variant/`: os 13 PNGs e o SCML originais, sem alterações.
- `assets/packs/fallen/`: peças registradas no rig, com os contornos normalizados.
- `assets/faces/fallen/`: expressões registradas no plano facial do criador.
- `assets/masks/packs/fallen/` e `assets/masks/faces/fallen/`: máscaras de materiais.
- `prepare_fallen.py`: preparação reproduzível, também chamada por `prepare_materials.py`.

Os keyframes das 17 ações são idênticos aos do rig existente. A ordem de expressões
foi preservada: Face 01 normal, Face 02 piscar e Face 03 dano. O pacote exportado
continua contendo 13 peças e 207 frames. As peças originais e o SCML permanecem
sujeitos à licença de seu pacote de origem.

Testes: `python -m unittest discover -s character-creator/tests -v` e
`python character-creator/tests/check_fallen.py` (Playwright e Chromium).

No rosto Fallen, a máscara da sobrancelha aberta cobre somente o interior
fechado pelo contorno original. Nas expressões de piscar e dano do Fallen, a sobrancelha fica totalmente preta
como os contornos, sem responder ao seletor de cor.

Os rostos existentes foram ampliados para um plano de 232 × 152 px para as feições
na expressão aberta, centrado em (163, 118) na textura de 320 × 240. Olhos,
sobrancelhas, nariz e boca foram ampliados juntos, incluindo as expressões
fechadas; o tamanho da cabeça, cabelos e corpos permanece inalterado. O Fallen
usa a escala facial nativa do ZIP. As máscaras acompanham o novo tamanho.

A cabeça Fallen usa o tamanho, a posição e a proporção exatos do ZIP original:
escala horizontal e vertical iguais a 1, sem alongamento ou alargamento. O teste
do conjunto compara a silhueta montada pixel a pixel com o alfa do Head.png
original, além de validar a exportação.

O cabelo e seu contorno ficam à frente das feições: as texturas faciais são
recortadas pela área de pele exposta da cabeça escolhida, no mesmo sistema
de coordenadas do rig. Assim a sobrancelha não invade as mechas. O recorte
é aplicado também aos PNGs exportados, mantendo a montagem SCML com 13 peças.
Verificação visual automatizada: `python character-creator/tests/check_hair_occlusion.py`.


## Conjunto Espectral — Vector Parts (2).zip

O botão **Espectro** monta o novo conjunto completo. As setas também permitem
selecionar separadamente o capuz, rosto, túnica com asas, cajado e traço do ataque.
Os braços, mãos e pernas acompanham o corpo. As 13 peças e o rig originais estão
preservados em `assets/imported/vector-parts-2/`; as versões preparadas ficam em
`assets/packs/spectral/`, `assets/faces/spectral/` e suas pastas de máscaras.

`prepare_spectral.py` prepara o conjunto e é chamado por `prepare_materials.py`.
A cabeça e as feições usam escala e posição nativas, sem achatamento. Pele altera
rosto e áreas descobertas das mãos; roupa, asas e luvas mantêm seus materiais.
O seletor Cabelo / capuz recolore o capuz com sombras e brilhos. Na expressão
aberta, a cor das sobrancelhas altera só o preenchimento, preservando o contorno.
Piscar e dano mantêm sobrancelhas inteiramente pretas, seguindo o padrão Fallen.
O capuz oculta feições que invadiriam suas mechas, inclusive nos arquivos exportados.

Testes do conjunto: `python character-creator/tests/check_spectral.py` e
`python -m unittest discover -s character-creator/tests -v`. A verificação de
sobreposição cobre 108 combinações de cabelos e expressões. A interface continua
em uma tela; o novo pacote também exporta 13 peças e 207 frames em 17 ações.

Na sobrancelha aberta do Espectral, a faixa superior é a cor base escolhida
e a inferior é uma sombra neutra multiplicada por 0,75, equivalente a uma camada
de cinza transparente. As duas acompanham a mesma cor, sem clarear a faixa
superior para branco. Os contornos e as expressões fechadas permanecem pretos.
