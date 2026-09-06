package de.belkis.killtothekiss;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KillToTheKiss implements ModInitializer {
    public static final String MOD_ID = "killtothekiss";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        ModComponents.register();
        ModItems.register();

        PayloadTypeRegistry.playC2S().register(ReloadPayload.TYPE, ReloadPayload.CODEC);
        ServerPlayNetworking.registerGlobalReceiver(ReloadPayload.TYPE, (payload, context) -> {
            var player = context.player();
            ItemStack stack = player.getMainHandItem();
            if (!(stack.getItem() instanceof GunItem)) {
                stack = player.getOffhandItem();
            }
            if (stack.getItem() instanceof GunItem gun) {
                gun.startReload(player.level(), player, stack);
            }
        });

        LOGGER.info("Kill to the Kiss loaded. Lock and load.");
    }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
    }
}
