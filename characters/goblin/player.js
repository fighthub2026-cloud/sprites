const number = (obj, key, fallback = 0) => Number(obj[key] ?? fallback);

export class SpriterPlayer {
  async load(base = './') {
    this.rig = await fetch(base + 'rig.json').then(r => { if (!r.ok) throw Error('Rig indisponível'); return r.json(); });
    this.images = {};
    await Promise.all(Object.entries(this.rig.files).map(async ([id, file]) => {
      const img = new Image();
      img.src = base + 'PNG/Vector Parts/' + encodeURIComponent(file.name);
      await img.decode();
      this.images[id] = img;
    }));
    return this;
  }

  sample(animation, ref, time) {
    const keys = animation.timelines[ref.timeline];
    const current = keys.find(k => k.id === ref.key);
    const index = keys.indexOf(current);
    let next = keys[(index + 1) % keys.length];
    const start = number(current, 'time');
    let end = number(next, 'time');
    if (index === keys.length - 1) end += Number(animation.length);
    let t = time;
    if (t < start) t += Number(animation.length);
    const f = keys.length < 2 || end === start ? 0 : Math.max(0, Math.min(1, (t - start) / (end - start)));
    const a = current.transform, b = next.transform;
    const result = {...a};
    for (const [key, fallback] of [['x',0], ['y',0], ['scale_x',1], ['scale_y',1], ['a',1]]) {
      result[key] = number(a, key, fallback) + (number(b, key, fallback) - number(a, key, fallback)) * f;
    }
    let angle = number(b, 'angle') - number(a, 'angle');
    const spin = number(current, 'spin', 1);
    if (!spin) angle = 0;
    else if (spin > 0 && angle < 0) angle += 360;
    else if (spin < 0 && angle > 0) angle -= 360;
    result.angle = number(a, 'angle') + angle * f;
    return result;
  }

  world(local, parent) {
    if (!parent) return local;
    const angle = number(parent, 'angle') * Math.PI / 180;
    const x = number(local, 'x') * number(parent, 'scale_x', 1);
    const y = number(local, 'y') * number(parent, 'scale_y', 1);
    return {...local,
      x: number(parent, 'x') + x * Math.cos(angle) - y * Math.sin(angle),
      y: number(parent, 'y') + x * Math.sin(angle) + y * Math.cos(angle),
      angle: number(parent, 'angle') + number(local, 'angle') * Math.sign(number(parent, 'scale_x', 1) * number(parent, 'scale_y', 1)),
      scale_x: number(local, 'scale_x', 1) * number(parent, 'scale_x', 1),
      scale_y: number(local, 'scale_y', 1) * number(parent, 'scale_y', 1),
      a: number(local, 'a', 1) * number(parent, 'a', 1)};
  }

  draw(canvas, name, milliseconds) {
    const animation = this.rig.animations.find(a => a.name === name);
    if (!animation) throw Error('Animação desconhecida: ' + name);
    const time = ((milliseconds % Number(animation.length)) + Number(animation.length)) % Number(animation.length);
    const main = animation.mainline.filter(k => number(k, 'time') <= time).at(-1);
    const bones = {};
    for (const ref of main.bones) bones[ref.id] = this.world(this.sample(animation, ref, time), bones[ref.parent]);
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.scale(canvas.width / 900, canvas.height / 900);
    ctx.translate(450, 750);
    for (const ref of [...main.objects].sort((a,b) => number(a,'z_index') - number(b,'z_index'))) {
      const value = this.world(this.sample(animation, ref, time), bones[ref.parent]);
      const file = this.rig.files[value.file];
      ctx.save();
      ctx.globalAlpha = number(value, 'a', 1);
      ctx.translate(number(value, 'x'), -number(value, 'y'));
      ctx.rotate(-number(value, 'angle') * Math.PI / 180);
      ctx.scale(number(value, 'scale_x', 1), number(value, 'scale_y', 1));
      const width = Number(file.width), height = Number(file.height);
      ctx.drawImage(this.images[value.file], -number(value,'pivot_x',number(file,'pivot_x')) * width,
        -(1 - number(value,'pivot_y',number(file,'pivot_y',1))) * height, width, height);
      ctx.restore();
    }
    ctx.restore();
  }
}
