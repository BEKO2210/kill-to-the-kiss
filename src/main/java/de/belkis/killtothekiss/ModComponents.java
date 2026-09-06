package de.belkis.killtothekiss;

import com.mojang.serialization.Codec;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.codec.ByteBufCodecs;

public final class ModComponents {
    /** Rounds currently in the magazine. */
    public static final DataComponentType<Integer> AMMO = DataComponentType.<Integer>builder()
            .persistent(Codec.INT)
            .networkSynchronized(ByteBufCodecs.VAR_INT)
            .build();

    /** Remaining reload ticks; absent or 0 when not reloading. */
    public static final DataComponentType<Integer> RELOAD = DataComponentType.<Integer>builder()
            .persistent(Codec.INT)
            .networkSynchronized(ByteBufCodecs.VAR_INT)
            .build();

    public static void register() {
        Registry.register(BuiltInRegistries.DATA_COMPONENT_TYPE, KillToTheKiss.id("ammo"), AMMO);
        Registry.register(BuiltInRegistries.DATA_COMPONENT_TYPE, KillToTheKiss.id("reload"), RELOAD);
    }

    private ModComponents() {}
}
