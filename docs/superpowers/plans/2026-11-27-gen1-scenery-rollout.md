# Gen 1 Scenery and Calendar Rollout Implementation Plan

**Goal:** Apply the Thor pilot's live voxel scenery and calendar behavior to verified Gen 1 cartridges and the existing sixteen GBA profiles.

**Architecture:** Keep cartridge recognition in the Game Boy profile table. Recognize terrain from live tiles and explicit material signatures. Reuse the calendar and projection across both cores. Keep device fixtures and unpublished evidence local.

- [ ] Verify each Gen 1 ROM's identity and layout independently. Register only verified profiles and report unknown revisions.
- [ ] Extend the voxel adapter past Pallet Town. Exercise the native 2D fallback, scenes with objects, walking, and palette protection.
- [ ] Share the calendar with the existing sixteen GBA games and Gen 1. Exercise season boundaries, weather stability, indoor masking and manual presets.
- [ ] Build and record the exact APK. On Thor, preserve enabled package data, use isolated fixtures, capture 2D and 3D comparisons, and record rendering and gameplay results.
- [ ] Assert every publication gate against that exact build. Keep partial coverage visible, restore the personal app, and publish only qualifying artifacts.
