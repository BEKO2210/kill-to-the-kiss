package de.belkis.killtothekiss;

import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;

/** Client -> server: "reload the gun I am holding". */
public record ReloadPayload() implements CustomPacketPayload {
    public static final Type<ReloadPayload> TYPE = new Type<>(KillToTheKiss.id("reload"));
    public static final StreamCodec<io.netty.buffer.ByteBuf, ReloadPayload> CODEC = StreamCodec.unit(new ReloadPayload());

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
