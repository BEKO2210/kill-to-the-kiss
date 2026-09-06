package de.belkis.killtothekiss;

import net.minecraft.sounds.SoundEvent;

/**
 * Static tuning for one weapon.
 *
 * @param damage      damage per bullet (half hearts)
 * @param fireRate    ticks between shots
 * @param magSize     rounds per magazine
 * @param reloadTicks duration of a reload
 * @param spread      base spread in degrees
 * @param recoil      camera kick per shot in degrees
 * @param range       max bullet travel in blocks
 * @param auto        hold to fire
 */
public record GunStats(
        float damage,
        int fireRate,
        int magSize,
        int reloadTicks,
        float spread,
        float recoil,
        double range,
        boolean auto,
        SoundEvent sound,
        float volume,
        float pitch
) {}
