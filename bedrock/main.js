import { world, system, EntityDamageCause } from "@minecraft/server";

// Gun tuning, injected by build_addon.py.
const GUNS = __GUNS__;

const autoFire = new Map();   // playerId -> interval handle
const cooldown = new Map();   // playerId -> tick when the next shot is allowed
const reloading = new Map();  // playerId -> timeout handle

function heldGun(player) {
  const inv = player.getComponent("minecraft:inventory");
  if (!inv) return null;
  const slot = player.selectedSlotIndex;
  const item = inv.container.getItem(slot);
  if (!item || !GUNS[item.typeId]) return null;
  return { item, slot, container: inv.container, gun: GUNS[item.typeId] };
}

function ammoIn(held) {
  const d = held.item.getComponent("minecraft:durability");
  return d.maxDurability - d.damage;
}

function setAmmo(held, ammo) {
  const d = held.item.getComponent("minecraft:durability");
  d.damage = Math.max(0, Math.min(d.maxDurability, d.maxDurability - ammo));
  held.container.setItem(held.slot, held.item);
}

function sound(player, id, volume, pitch) {
  try { player.dimension.playSound(id, player.location, { volume, pitch }); } catch (e) {}
}

function command(player, cmd) {
  try { player.runCommand(cmd); } catch (e) { try { player.runCommandAsync(cmd); } catch (e2) {} }
}

function stopAuto(player) {
  const h = autoFire.get(player.id);
  if (h !== undefined) { system.clearRun(h); autoFire.delete(player.id); }
}

function reload(player) {
  if (reloading.has(player.id)) return;
  const held = heldGun(player);
  if (!held) return;
  const { gun } = held;
  const current = ammoIn(held);
  if (current >= gun.mag) return;
  const creative = !!player.getGameMode && String(player.getGameMode()).toLowerCase() === "creative";
  if (!creative && countItems(held.container, gun.ammo) === 0) {
    sound(player, "random.click", 0.6, 0.7);
    player.onScreenDisplay.setActionBar("§cKeine Munition / No ammo");
    return;
  }
  stopAuto(player);
  sound(player, "crossbow.loading.start", 0.9, 1.3);
  const typeId = held.item.typeId;
  const total = gun.reload;
  let left = total;
  const tick = system.runInterval(() => {
    left--;
    const bar = "§6" + "▮".repeat(Math.round(10 * (1 - left / total))) + "§8" + "▯".repeat(Math.round(10 * left / total));
    player.onScreenDisplay.setActionBar(bar + " §7Reload");
    const now = heldGun(player);
    if (!now || now.item.typeId !== typeId) { // switched weapon: cancel
      system.clearRun(tick); reloading.delete(player.id); return;
    }
    if (left === Math.floor(total / 2)) sound(player, "crossbow.loading.middle", 0.9, 1.4);
    if (left > 0) return;
    system.clearRun(tick);
    reloading.delete(player.id);
    const need = gun.mag - ammoIn(now);
    const got = creative ? need : takeItems(now.container, gun.ammo, need);
    setAmmo(now, ammoIn(now) + got);
    sound(player, "crossbow.loading.end", 0.9, 1.2);
    player.onScreenDisplay.setActionBar(`§a${ammoIn(now)} / ${gun.mag}`);
  }, 1);
  reloading.set(player.id, tick);
}

function countItems(container, typeId) {
  let n = 0;
  for (let i = 0; i < container.size; i++) {
    const s = container.getItem(i);
    if (s && s.typeId === typeId) n += s.amount;
  }
  return n;
}

function takeItems(container, typeId, wanted) {
  let taken = 0;
  for (let i = 0; i < container.size && taken < wanted; i++) {
    const s = container.getItem(i);
    if (!s || s.typeId !== typeId) continue;
    const n = Math.min(s.amount, wanted - taken);
    if (n >= s.amount) container.setItem(i, undefined);
    else { s.amount -= n; container.setItem(i, s); }
    taken += n;
  }
  return taken;
}

function shoot(player) {
  const held = heldGun(player);
  if (!held) { stopAuto(player); return; }
  const { gun } = held;
  if (reloading.has(player.id)) return;
  const now = system.currentTick;
  if ((cooldown.get(player.id) ?? 0) > now) return;

  const ammo = ammoIn(held);
  if (ammo <= 0) {
    stopAuto(player);
    sound(player, "random.click", 0.7, 1.7);
    reload(player);
    return;
  }
  cooldown.set(player.id, now + gun.rate);
  setAmmo(held, ammo - 1);

  const dim = player.dimension;
  const head = player.getHeadLocation();
  const view = player.getViewDirection();
  let spread = gun.spread * (player.isSneaking ? 0.4 : 1) * (player.isSprinting ? 2 : 1);
  spread = spread * Math.PI / 180;
  const jitter = () => (Math.random() + Math.random() - 1) * spread;
  let dir = { x: view.x + jitter(), y: view.y + jitter(), z: view.z + jitter() };
  const len = Math.hypot(dir.x, dir.y, dir.z);
  dir = { x: dir.x / len, y: dir.y / len, z: dir.z / len };
  const at = (d) => ({ x: head.x + dir.x * d, y: head.y + dir.y * d, z: head.z + dir.z * d });

  let maxDist = gun.range;
  let blockHit = null;
  try {
    blockHit = dim.getBlockFromRay(head, dir, { maxDistance: gun.range, includePassableBlocks: false, includeLiquidBlocks: false });
    if (blockHit) {
      const fl = blockHit.block.location;
      const p = { x: fl.x + blockHit.faceLocation.x, y: fl.y + blockHit.faceLocation.y, z: fl.z + blockHit.faceLocation.z };
      maxDist = Math.hypot(p.x - head.x, p.y - head.y, p.z - head.z);
    }
  } catch (e) {}

  let hits = [];
  try { hits = dim.getEntitiesFromRay(head, dir, { maxDistance: maxDist }); } catch (e) {}
  const hit = hits.find(h => h.entity.id !== player.id);

  let impactDist = maxDist;
  if (hit) {
    impactDist = hit.distance;
    const point = at(hit.distance);
    const headshot = point.y > hit.entity.location.y + 1.35;
    const dmg = gun.dmg * (headshot ? 1.75 : 1);
    try {
      hit.entity.applyDamage(dmg, { cause: EntityDamageCause.projectile, damagingEntity: player });
      dim.spawnParticle(headshot ? "minecraft:critical_hit_emitter" : "minecraft:basic_crit_particle", point);
      if (headshot) sound(player, "random.orb", 0.5, 1.6);
    } catch (e) {}
  } else if (blockHit) {
    try { dim.spawnParticle("minecraft:basic_smoke_particle", at(impactDist - 0.1)); } catch (e) {}
  }

  // Tracer + muzzle flash.
  try {
    dim.spawnParticle("minecraft:basic_flame_particle", at(1.0));
    for (let d = 2.5; d < Math.min(impactDist, 40); d += 2) dim.spawnParticle("minecraft:basic_crit_particle", at(d));
  } catch (e) {}

  sound(player, gun.sound, gun.vol, gun.pitch + (Math.random() - 0.5) * 0.1);
  command(player, `camerashake add @s ${(gun.recoil * 0.045).toFixed(3)} 0.12 rotational`);
  player.onScreenDisplay.setActionBar(`§f${ammo - 1} / ${gun.mag}`);

  if (ammo - 1 <= 0) { stopAuto(player); reload(player); }
}

world.afterEvents.itemStartUse.subscribe(ev => {
  const player = ev.source;
  const gun = GUNS[ev.itemStack.typeId];
  if (!gun) return;
  if (player.isSneaking) { reload(player); return; }
  shoot(player);
  if (gun.auto) {
    stopAuto(player);
    autoFire.set(player.id, system.runInterval(() => shoot(player), 1));
  }
});

world.afterEvents.itemStopUse.subscribe(ev => stopAuto(ev.source));
world.afterEvents.itemReleaseUse.subscribe(ev => stopAuto(ev.source));

world.afterEvents.playerLeave.subscribe(ev => {
  const h = autoFire.get(ev.playerId);
  if (h !== undefined) system.clearRun(h);
  autoFire.delete(ev.playerId);
  const r = reloading.get(ev.playerId);
  if (r !== undefined) system.clearRun(r);
  reloading.delete(ev.playerId);
});
