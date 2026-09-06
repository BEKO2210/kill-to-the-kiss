package de.belkis.killtothekiss;

import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

public final class ModItems {
    public static final List<Item> ALL = new ArrayList<>();
    public static final List<GunItem> GUNS = new ArrayList<>();

    // Ammo
    public static final Item PISTOL_AMMO = ammo("pistol_ammo");
    public static final Item RIFLE_AMMO = ammo("rifle_ammo");
    public static final Item SNIPER_AMMO = ammo("sniper_ammo");

    // Parts
    public static final Item GUN_BARREL = part("gun_barrel");
    public static final Item GUN_RECEIVER = part("gun_receiver");
    public static final Item GUN_STOCK = part("gun_stock");

    // Guns: damage, fireRate, mag, reload, spread, recoil, range, auto, sound, vol, pitch
    public static final GunItem AK47 = gun("ak47", new GunStats(
            7f, 3, 30, 50, 2.2f, 1.6f, 80, true,
            SoundEvents.GENERIC_EXPLODE.value(), 0.45f, 1.7f), RIFLE_AMMO);
    public static final GunItem M16 = gun("m16", new GunStats(
            6f, 2, 30, 45, 1.6f, 1.1f, 90, true,
            SoundEvents.GENERIC_EXPLODE.value(), 0.4f, 1.9f), RIFLE_AMMO);
    public static final GunItem UZI = gun("uzi", new GunStats(
            3.5f, 1, 32, 35, 3.8f, 0.8f, 40, true,
            SoundEvents.FIREWORK_ROCKET_BLAST, 0.9f, 1.6f), PISTOL_AMMO);
    public static final GunItem SNIPER = gun("sniper", new GunStats(
            24f, 30, 5, 70, 0.15f, 6.0f, 200, false,
            SoundEvents.GENERIC_EXPLODE.value(), 0.7f, 1.1f), SNIPER_AMMO);
    public static final GunItem USP = gun("usp", new GunStats(
            6f, 5, 12, 30, 1.0f, 1.8f, 50, false,
            SoundEvents.FIREWORK_ROCKET_BLAST, 0.8f, 1.3f), PISTOL_AMMO);

    public static final CreativeModeTab TAB = FabricItemGroup.builder()
            .icon(() -> new ItemStack(AK47))
            .title(Component.translatable("itemGroup.killtothekiss"))
            .displayItems((params, output) -> ALL.forEach(output::accept))
            .build();

    private static Item ammo(String name) {
        return add(name, new Item(new Item.Properties().stacksTo(64)));
    }

    private static Item part(String name) {
        return add(name, new Item(new Item.Properties().stacksTo(16)));
    }

    private static GunItem gun(String name, GunStats stats, Item ammo) {
        GunItem gun = new GunItem(stats, ammo);
        GUNS.add(gun);
        add(name, gun);
        return gun;
    }

    private static <T extends Item> T add(String name, T item) {
        Registry.register(BuiltInRegistries.ITEM, KillToTheKiss.id(name), item);
        ALL.add(item);
        return item;
    }

    public static void register() {
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, KillToTheKiss.id("main"), TAB);
    }

    private ModItems() {}
}
