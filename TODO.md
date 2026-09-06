# Kill to the Kiss – TODO

- [x] 1. Toolchain prüfen (Java 21, Python PIL)
- [x] 2. Fabric-Template klonen (Minecraft 1.21, Loader 0.19.5, Fabric API 0.102)
- [x] 3. Projekt umbenennen auf `killtothekiss`, Mixins entfernen
- [x] 4. Data-Components: Magazin-Munition + Reload-Timer (persistiert, netzwerksynchron)
- [x] 5. Items: AK-47, M16, UZI, Sniper, USP · 3 Munitionstypen · 3 Bauteile · Creative-Tab
- [x] 6. Schusslogik: Raycast, Vollautomatik (halten), Rückstoß, Headshot ×1.75, Tracer, Einschlagpartikel
- [x] 7. Nachladen: Taste R (C2S-Packet) oder Schleichen+Rechtsklick, Auto-Reload bei leerem Magazin
- [x] 8. Animationen: Model-Predicates `fire` (Mündungsfeuer + Recoil-Pose) und `reload` (3 Frames, Magazin raus/rein)
- [x] 9. Assets generiert (`tools/gen_assets.py`): 31 Texturen, 31 Models, 11 Rezepte, en_us + de_de, Icon
- [x] 10. Build → `build/libs/kill-to-the-kiss-1.0.0.jar`

## Später (optional)
- [ ] Eigene Sounds (OGG) statt Vanilla-Explosion/Feuerwerk
- [ ] 3D-Modelle statt extrudierter Sprites
- [ ] Scope-Zoom für Sniper beim Schleichen
