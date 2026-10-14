# Goblin

Personagem montado por peças, com o corpo compacto e o rig do Orc enviado como referência. A cabeça foi adaptada para Goblin; corpo, braços, mãos, pernas, expressões, arma e efeito são reutilizados do material enviado. Não é um conjunto inteiramente redesenhado.

## Arquivos

- `PNG/Vector Parts/`: 13 peças PNG com dimensões e nomes compatíveis com o rig, mais `Animations.scml` para Spriter.
- `PNG/PNG Sequences/`: 207 frames transparentes de 900 × 900, organizados nas mesmas 17 animações do Orc.
- `idle.png`: personagem completo montado em repouso.
- `preview.gif`: prévia de corrida.
- `index.html`: reprodução das 17 animações por peças, com seleção de animação, pausa e velocidade.
- `rig.json` e `player.js`: dados do SCML e reprodutor Canvas com interpolação de transformações e hierarquia de ossos.

## Visualizar e exportar

Na raiz do repositório:

```sh
python -m http.server 8765 --bind 127.0.0.1
```

Abra `/characters/goblin/` no servidor local. A página precisa de HTTP para carregar os dados; abrir diretamente como `file://` pode bloquear o carregamento.

Para regenerar as sequências, mantenha o servidor ativo e execute em outro terminal:

```sh
python tools/export_goblin.py
```

A exportação usa Playwright e Chromium. O executável padrão é `/usr/bin/chromium`; `CHROMIUM_PATH` permite indicar outro caminho.

As poses, pivôs, hierarquia, ordem de camadas, duração e quantidades de frames vêm de `Animations.scml` e das sequências do Orc fornecidas. O renderizador foi conferido contra o frame Idle original usando as peças originais antes de exportar o Goblin. Os PNGs exportados têm fundo transparente; o quadriculado aparece apenas na página de visualização.

Material de referência: pasta Orc do pacote Craftpix `craftpix-064112-free-orc-ogre-and-goblin-chibi-2d-game-sprites`, enviada pelo usuário. Os direitos das peças reutilizadas continuam sujeitos à licença desse material.
