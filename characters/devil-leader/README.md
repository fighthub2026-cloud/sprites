# Devil Leader

330 frames originais, em 24 sequências, extraídos do `PNG Sequences.zip` enviado pelo usuário.

O jogo em `games/forest-ranger/index.html` usa este personagem como protagonista.
O atlas WebP sem perdas e os metadados também estão embutidos no HTML, que funciona
sem carregar arquivos ou ZIPs durante o jogo.

- `PNG/PNG Sequences/`: frames originais, sem alterações.
- `atlas.webp`: frames redimensionados e registrados em células de 256 × 224, com 16 colunas.
- `atlas.json`: índices, quantidades e ponto de apoio das animações no atlas.

Frente, costas, esquerda e direita são selecionadas pela direção do personagem.
As animações mantêm os pés no chão e a escala visual consistente ao trocar de vista.
As direções originais são desenhadas sem espelhamento adicional.

O pacote contém Idle, Idle Blinking, Walking, Running, Attacking, Hurt e Dying.
Como não há sequências específicas de salto ou arremesso, o salto usa a pose Idle
com a altura calculada pelo jogo, e o arremesso usa Attacking. O ataque e o projétil
mantêm os tempos e as colisões do jogo. Os inimigos continuam com os sprites anteriores.

Material de origem: Devil Leader / Craftpix, fornecido pelo usuário. Os direitos e
as condições de uso do pacote original continuam aplicáveis.
