package de.belkis.killtothekiss.client;

import com.mojang.blaze3d.platform.InputConstants;
import de.belkis.killtothekiss.GunItem;
import de.belkis.killtothekiss.KillToTheKiss;
import de.belkis.killtothekiss.ModItems;
import de.belkis.killtothekiss.ReloadPayload;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.world.entity.player.Player;
import org.lwjgl.glfw.GLFW;

public class KillToTheKissClient implements ClientModInitializer {
    public static final KeyMapping RELOAD_KEY = new KeyMapping(
            "key.killtothekiss.reload", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_R, "category.killtothekiss");

    @Override
    public void onInitializeClient() {
        KeyBindingHelper.registerKeyBinding(RELOAD_KEY);
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            while (RELOAD_KEY.consumeClick()) {
                if (client.player == null) continue;
                boolean holdingGun = client.player.getMainHandItem().getItem() instanceof GunItem
                        || client.player.getOffhandItem().getItem() instanceof GunItem;
                if (holdingGun) {
                    ClientPlayNetworking.send(new ReloadPayload());
                }
            }
        });

        for (GunItem gun : ModItems.GUNS) {
            // 0 -> not reloading, (0,1] -> reload progress. Drives the reload animation frames.
            ItemProperties.register(gun, KillToTheKiss.id("reload"), (stack, level, entity, seed) -> {
                int ticks = GunItem.getReloadTicks(stack);
                if (ticks <= 0) return 0f;
                return Math.max(0.001f, 1f - (float) ticks / gun.stats.reloadTicks());
            });
            // Cooldown fraction right after a shot. Drives the muzzle-flash frame.
            ItemProperties.register(gun, KillToTheKiss.id("fire"), (stack, level, entity, seed) ->
                    entity instanceof Player player ? player.getCooldowns().getCooldownPercent(gun, 0f) : 0f);
        }
    }
}
