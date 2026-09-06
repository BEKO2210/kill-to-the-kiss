package de.belkis.killtothekiss;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.List;

public class GunItem extends Item {
    public final GunStats stats;
    public final Item ammoItem;

    public GunItem(GunStats stats, Item ammoItem) {
        super(new Item.Properties().stacksTo(1).component(ModComponents.AMMO, stats.magSize()));
        this.stats = stats;
        this.ammoItem = ammoItem;
    }

    // ---------------------------------------------------------------- state

    public static int getAmmo(ItemStack stack) {
        return stack.getOrDefault(ModComponents.AMMO, 0);
    }

    public static int getReloadTicks(ItemStack stack) {
        return stack.getOrDefault(ModComponents.RELOAD, 0);
    }

    public static boolean isReloading(ItemStack stack) {
        return getReloadTicks(stack) > 0;
    }

    // ---------------------------------------------------------------- use

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (isReloading(stack)) {
            return InteractionResultHolder.fail(stack);
        }
        if (player.isShiftKeyDown()) {
            startReload(level, player, stack);
            return InteractionResultHolder.consume(stack);
        }
        if (getAmmo(stack) <= 0) {
            if (!level.isClientSide) {
                level.playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 0.7f, 1.7f);
                startReload(level, player, stack);
            }
            return InteractionResultHolder.fail(stack);
        }
        player.startUsingItem(hand);
        shoot(level, player, stack);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remainingUseDuration) {
        if (!stats.auto()) return;
        if (user instanceof Player player) {
            shoot(level, player, stack);
        }
    }

    @Override
    public int getUseDuration(ItemStack stack, LivingEntity entity) {
        return 72000;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.NONE;
    }

    // ---------------------------------------------------------------- shooting

    private void shoot(Level level, Player player, ItemStack stack) {
        if (player.getCooldowns().isOnCooldown(this)) return;
        if (isReloading(stack)) return;

        int ammo = getAmmo(stack);
        if (ammo <= 0) {
            player.stopUsingItem();
            if (!level.isClientSide) {
                level.playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 0.7f, 1.7f);
                startReload(level, player, stack);
            }
            return;
        }

        player.getCooldowns().addCooldown(this, stats.fireRate());
        RandomSource random = player.getRandom();

        if (level.isClientSide) {
            // Camera recoil: vertical kick plus a little horizontal drift.
            float kick = stats.recoil() * (0.7f + random.nextFloat() * 0.6f);
            player.setXRot(player.getXRot() - kick);
            player.setYRot(player.getYRot() + (random.nextFloat() - 0.5f) * stats.recoil() * 0.5f);
            return;
        }

        stack.set(ModComponents.AMMO, ammo - 1);
        ServerLevel serverLevel = (ServerLevel) level;

        Vec3 eye = player.getEyePosition();
        Vec3 look = player.getLookAngle();

        // Aiming down (sneaking) tightens spread; moving loosens it.
        float spreadDeg = stats.spread();
        if (player.isShiftKeyDown()) spreadDeg *= 0.4f;
        if (player.isSprinting()) spreadDeg *= 2.0f;
        double spread = Math.toRadians(spreadDeg);
        Vec3 dir = new Vec3(
                look.x + random.triangle(0, spread),
                look.y + random.triangle(0, spread),
                look.z + random.triangle(0, spread)).normalize();

        Vec3 end = eye.add(dir.scale(stats.range()));
        BlockHitResult blockHit = level.clip(new ClipContext(eye, end,
                ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
        if (blockHit.getType() != HitResult.Type.MISS) {
            end = blockHit.getLocation();
        }

        EntityHitResult entityHit = ProjectileUtil.getEntityHitResult(level, player, eye, end,
                player.getBoundingBox().expandTowards(dir.scale(stats.range())).inflate(1.0),
                e -> !e.isSpectator() && e.isPickable() && e != player, 0.3f);

        Vec3 impact = end;
        if (entityHit != null) {
            Entity target = entityHit.getEntity();
            impact = entityHit.getLocation();
            float damage = stats.damage();
            boolean headshot = target instanceof LivingEntity living
                    && impact.y > living.getY() + living.getBbHeight() * 0.72;
            if (headshot) damage *= 1.75f;
            target.invulnerableTime = 0; // let full-auto register every hit
            target.hurt(level.damageSources().playerAttack(player), damage);
            serverLevel.sendParticles(headshot ? ParticleTypes.CRIT : ParticleTypes.DAMAGE_INDICATOR,
                    impact.x, impact.y, impact.z, headshot ? 12 : 5, 0.15, 0.15, 0.15, 0.1);
            if (headshot) {
                level.playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.ARROW_HIT_PLAYER, SoundSource.PLAYERS, 0.6f, 1.5f);
            }
        } else if (blockHit.getType() == HitResult.Type.BLOCK) {
            BlockState state = level.getBlockState(blockHit.getBlockPos());
            serverLevel.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, state),
                    impact.x, impact.y, impact.z, 8, 0.1, 0.1, 0.1, 0.05);
        }

        // Tracer.
        double distance = eye.distanceTo(impact);
        Vec3 step = impact.subtract(eye).normalize();
        int points = (int) Math.min(48, distance / 1.5);
        for (int i = 1; i <= points; i++) {
            Vec3 p = eye.add(step.scale(i * 1.5));
            serverLevel.sendParticles(ParticleTypes.CRIT, p.x, p.y, p.z, 1, 0, 0, 0, 0);
        }

        // Muzzle smoke.
        Vec3 muzzle = eye.add(look.scale(1.2)).add(0, -0.15, 0);
        serverLevel.sendParticles(ParticleTypes.SMOKE, muzzle.x, muzzle.y, muzzle.z, 3, 0.05, 0.05, 0.05, 0.02);

        level.playSound(null, player.getX(), player.getY(), player.getZ(),
                stats.sound(), SoundSource.PLAYERS, stats.volume(),
                stats.pitch() + (random.nextFloat() - 0.5f) * 0.1f);

        if (ammo - 1 <= 0) {
            player.stopUsingItem();
            startReload(level, player, stack);
        }
    }

    // ---------------------------------------------------------------- reload

    public void startReload(Level level, Player player, ItemStack stack) {
        if (level.isClientSide) return;
        if (isReloading(stack)) return;
        if (getAmmo(stack) >= stats.magSize()) return;
        if (!player.getAbilities().instabuild && countAmmo(player) == 0) {
            level.playSound(null, player.getX(), player.getY(), player.getZ(),
                    SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 0.5f, 0.8f);
            return;
        }
        player.stopUsingItem();
        stack.set(ModComponents.RELOAD, stats.reloadTicks());
        level.playSound(null, player.getX(), player.getY(), player.getZ(),
                SoundEvents.CROSSBOW_LOADING_START.value(), SoundSource.PLAYERS, 0.9f, 1.3f);
    }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity entity, int slot, boolean selected) {
        if (level.isClientSide) return;
        int ticks = getReloadTicks(stack);
        if (ticks <= 0) return;

        boolean held = entity instanceof Player player
                && (selected || player.getOffhandItem() == stack);
        if (!held) {
            stack.remove(ModComponents.RELOAD); // switching away cancels the reload
            return;
        }

        Player player = (Player) entity;
        ticks--;
        if (ticks > 0) {
            stack.set(ModComponents.RELOAD, ticks);
            if (ticks == stats.reloadTicks() / 2) {
                level.playSound(null, player.getX(), player.getY(), player.getZ(),
                        SoundEvents.CROSSBOW_LOADING_MIDDLE.value(), SoundSource.PLAYERS, 0.9f, 1.4f);
            }
            return;
        }

        int need = stats.magSize() - getAmmo(stack);
        int got = player.getAbilities().instabuild ? need : takeAmmo(player, need);
        stack.set(ModComponents.AMMO, getAmmo(stack) + got);
        stack.remove(ModComponents.RELOAD);
        level.playSound(null, player.getX(), player.getY(), player.getZ(),
                SoundEvents.CROSSBOW_LOADING_END.value(), SoundSource.PLAYERS, 0.9f, 1.2f);
    }

    private int countAmmo(Player player) {
        int count = 0;
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            ItemStack s = player.getInventory().getItem(i);
            if (s.is(ammoItem)) count += s.getCount();
        }
        return count;
    }

    private int takeAmmo(Player player, int wanted) {
        int taken = 0;
        for (int i = 0; i < player.getInventory().getContainerSize() && taken < wanted; i++) {
            ItemStack s = player.getInventory().getItem(i);
            if (!s.is(ammoItem)) continue;
            int n = Math.min(s.getCount(), wanted - taken);
            s.shrink(n);
            taken += n;
        }
        return taken;
    }

    // ---------------------------------------------------------------- display

    @Override
    public boolean isBarVisible(ItemStack stack) {
        return true;
    }

    @Override
    public int getBarWidth(ItemStack stack) {
        if (isReloading(stack)) {
            return Math.round(13f * (1f - (float) getReloadTicks(stack) / stats.reloadTicks()));
        }
        return Math.round(13f * getAmmo(stack) / stats.magSize());
    }

    @Override
    public int getBarColor(ItemStack stack) {
        if (isReloading(stack)) return 0xFFAA00;
        float f = (float) getAmmo(stack) / stats.magSize();
        return Mth.hsvToRgb(f / 3f, 1f, 1f);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.killtothekiss.ammo", getAmmo(stack), stats.magSize())
                .withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.killtothekiss.damage", stats.damage())
                .withStyle(ChatFormatting.DARK_GRAY));
        tooltip.add(Component.translatable("tooltip.killtothekiss.firerate", Math.round(1200f / stats.fireRate()))
                .withStyle(ChatFormatting.DARK_GRAY));
        tooltip.add(Component.translatable("tooltip.killtothekiss.reload").withStyle(ChatFormatting.DARK_GRAY));
    }

    @Override
    public boolean isEnchantable(ItemStack stack) {
        return false;
    }
}
