ElfMage.unitypackage contém as 13 peças e os 207 frames PNG, importados como sprites,
mais o arquivo SCML e um reprodutor de sequências chamado ElfMageAnimator.

Importe o pacote em um projeto Unity. Crie um GameObject com SpriteRenderer e
adicione ElfMageAnimator. Selecione animationName: Idle, Idle Blinking, Walking,
Running, Slashing, Throwing ou outro nome correspondente às pastas de sequências.
O reprodutor usa 30 frames por segundo por padrão; não requer um Animator Controller.

O SCML serve para edição no Spriter. O script Unity reproduz os PNGs já montados;
não implementa diretamente o rig SCML no Unity. O pacote e seus caminhos foram
conferidos estruturalmente; a importação no Editor Unity não foi executada neste ambiente.
