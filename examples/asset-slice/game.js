'use strict';
(async () => {
  const canvas = document.querySelector('#game'), ctx = canvas.getContext('2d');
  const stateView = document.querySelector('#state'), message = document.querySelector('#message');
  const loadJSON = async url => { const response = await fetch(url); if (!response.ok) throw new Error(`${url}: ${response.status}`); return response.json(); };
  const image = url => new Promise((resolve, reject) => { const img = new Image(); img.onload = () => resolve(img); img.onerror = () => reject(new Error(`Image failed: ${url}`)); img.src = url; });
  const [map, translations, hero, enemy, tiles] = await Promise.all([loadJSON('room.json'), loadJSON('locales.json'), image('hero.svg'), image('enemy.svg'), image('tiles.svg')]);
  let language = 'zh-CN', player = {x:96,y:160}, hp = 2, quest = false, won = false, started = false;
  let audioContext, sound, audioStatus = 'locked', soundEvents = 0, hits = 0, effects = [], keys = new Set(), last = performance.now(), lastAttack = -Infinity, walkingUntil = 0;
  const enemyPosition = {x:288,y:160}, storageKey = 'game-studio-plus-asset-slice-v1';
  const text = key => translations.locales[language][key] || translations.locales[translations.default_locale][key] || key;
  function translate() { document.documentElement.lang = language; document.querySelectorAll('[data-text]').forEach(element => { element.textContent = text(element.dataset.text); }); }
  async function unlock() {
    started = true;
    try {
      audioContext ||= new AudioContext();
      await audioContext.resume();
      if (!sound) { const response = await fetch('hit.wav'); if (!response.ok) throw new Error('Run build_audio.py first'); sound = await audioContext.decodeAudioData(await response.arrayBuffer()); }
      audioStatus = audioContext.state === 'running' ? 'running' : audioContext.state;
    } catch (error) { audioStatus = 'unavailable'; document.querySelector('#error').textContent = `Audio: ${error.message}`; }
    update();
  }
  function playSound() { if (sound && audioContext?.state === 'running') { const source = audioContext.createBufferSource(); source.buffer = sound; source.connect(audioContext.destination); source.onended = () => source.disconnect(); source.start(); soundEvents++; } }
  function update() { stateView.textContent = `\nx=${Math.round(player.x)} y=${Math.round(player.y)}\nenemy_hp=${hp}\nquest=${quest}\ncompleted=${won}\nhit_events=${hits}\nsound_events=${soundEvents}\naudio=${audioStatus}\nlocale=${language}`; }
  function move(dx,dy) { if (!started || won) return; player.x = Math.max(48,Math.min(592,player.x+dx)); player.y = Math.max(48,Math.min(272,player.y+dy)); walkingUntil = performance.now()+120; if (quest && hp===0 && player.x>540 && Math.abs(player.y-160)<48) { won=true; message.textContent=text('win'); } update(); }
  function attack() { const now=performance.now(); if (!started || won || now-lastAttack<250) return; lastAttack=now; if(hp>0 && Math.hypot(player.x-enemyPosition.x,player.y-enemyPosition.y)<64) { hp--; hits++; playSound(); effects.push({x:enemyPosition.x,y:enemyPosition.y,t:now}); } update(); }
  document.querySelector('#start').onclick = unlock;
  document.querySelector('#accept').onclick = () => { if (started) { quest=true; message.textContent=text('quest'); update(); } };
  document.querySelector('#attack').onclick = attack;
  for (const [id,dx,dy] of [['left',-32,0],['right',32,0],['up',0,-32],['down',0,32]]) document.querySelector(`#${id}`).onclick=()=>move(dx,dy);
  document.querySelector('#locale').onclick=()=>{language=language==='zh-CN'?'en':'zh-CN';translate();message.textContent=won?text('win'):quest?text('quest'):'';update();};
  document.querySelector('#save').onclick=()=>{try { localStorage.setItem(storageKey,JSON.stringify({version:1,player,hp,quest,won,language}));message.textContent='Saved / 已保存'; } catch {message.textContent='Save unavailable / 存档不可用';}};
  document.querySelector('#load').onclick=()=>{try {const saved=JSON.parse(localStorage.getItem(storageKey)); if(!saved || saved.version!==1 || ![0,1,2].includes(saved.hp) || !Number.isFinite(saved.player?.x) || !Number.isFinite(saved.player?.y) || typeof saved.quest!=='boolean' || typeof saved.won!=='boolean' || !translations.locales[saved.language]) throw new Error('Invalid save'); player={x:Math.max(48,Math.min(592,saved.player.x)),y:Math.max(48,Math.min(272,saved.player.y))};hp=saved.hp;quest=saved.quest;won=saved.won;language=saved.language;effects=[];keys.clear();translate();message.textContent='Loaded / 已读取';update();}catch{message.textContent='No valid save / 无有效存档';}};
  document.querySelector('#reset').onclick=()=>{player={x:96,y:160};hp=2;quest=false;won=false;hits=0;soundEvents=0;effects=[];keys.clear();lastAttack=-Infinity;message.textContent='';update();};
  addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' '].includes(event.key))event.preventDefault();keys.add(event.key.toLowerCase());if(event.key===' '&&!event.repeat)attack();});
  addEventListener('keyup',event=>keys.delete(event.key.toLowerCase()));
  addEventListener('blur',()=>keys.clear());
  document.addEventListener('visibilitychange',()=>{keys.clear();last=performance.now();});
  function frame(now) {
    const dt=Math.min((now-last)/1000,.04);last=now;
    if(keys.has('arrowleft')||keys.has('a'))move(-140*dt,0);
    if(keys.has('arrowright')||keys.has('d'))move(140*dt,0);
    if(keys.has('arrowup')||keys.has('w'))move(0,-140*dt);
    if(keys.has('arrowdown')||keys.has('s'))move(0,140*dt);
    ctx.clearRect(0,0,640,320);
    for(const layer of map.layers.filter(layer=>layer.type==='tilelayer')) layer.data.forEach((gid,i)=>{if(gid)ctx.drawImage(tiles,(gid-1)*32,0,32,32,(i%20)*32,Math.floor(i/20)*32,32,32);});
    ctx.fillStyle=won?'#edbe68':'#6edfc0';ctx.fillRect(554,122,20,76);ctx.fillStyle='#152b35';ctx.fillRect(558,127,12,65);
    ctx.fillStyle='#091f2a88';ctx.beginPath();ctx.ellipse(player.x,player.y+15,17,6,0,0,Math.PI*2);ctx.fill();
    const frameIndex=now<walkingUntil?Math.floor(now/100)%4:0;ctx.drawImage(hero,frameIndex*32,0,32,32,player.x-20,player.y-24,40,40);
    if(hp>0){ctx.drawImage(enemy,enemyPosition.x-20,enemyPosition.y-24,40,40);ctx.fillStyle='#f09584';ctx.fillRect(enemyPosition.x-16,enemyPosition.y-33,hp*16,3);}
    effects=effects.filter(effect=>now-effect.t<400);
    for(const effect of effects){const age=(now-effect.t)/400;ctx.strokeStyle=`rgba(255,213,139,${1-age})`;ctx.lineWidth=3;ctx.beginPath();ctx.arc(effect.x,effect.y,12+age*35,0,Math.PI*2);ctx.stroke();}
    requestAnimationFrame(frame);
  }
  translate();update();requestAnimationFrame(frame);
})().catch(error=>{document.querySelector('#error').textContent=error.message;console.error(error);});
