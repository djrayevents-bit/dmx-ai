# Market and product plan — DMX AI

**Status:** Planning research (Aug 2026)  
**Beachhead:** Not decided

---

## Product vision

**DMX AI** is AI lighting software for DJs and bands — a fusion of:

| Influence | What we take |
|-----------|--------------|
| **SoundSwitch** | Track-scripted DJ lighting, phrase/beatgrid sync, AutoScript |
| **Wolfmix / ADJ WMX1** | Tactile live FX — Colour, Move, Beam without a laptop |
| **MaestroDMX / Konductor** | Autonomous, structure-aware direction (builds, drops, speech) |

**One-liner:** SoundSwitch's sync × Maestro's autonomy × Wolfmix's hands × a real AI lighting director.

**Working product names (not final):** LumenForge, CueMind, StageBrain.

---

## Market map

| Cluster | Products | Superpower | Weakness |
|---------|----------|------------|----------|
| **Track-scripted DJ DLW** | SoundSwitch, Engine Lighting, Rekordbox Lighting | Phrase/beatgrid sync, AutoScript, Serato/VDJ/Engine integration | Weak for bands; ~1–2 universes; bad phrase analysis at library scale; multicell/pixel/laser awkward; generic autoscript |
| **Tactile live FX** | Wolfmix / ADJ WMX1 | No laptop, Colour/Move/Beam FX | One FX engine across groups; no per-track storytelling |
| **Autonomous AI hardware** | MaestroDMX | Structure-aware (builds/drops/speech), zero programming | 1 universe; less override; browser config |
| **AI software desks** | MyStrow, DMXDesktop + Konductor | Role-aware auto shows, volume dynamics, Art-Net | Smaller ecosystems |
| **Musician / DAW** | ENTTEC EMU, Show Buddy Active | VST/MIDI/footswitch, pixel, DAW timeline | Not a DJ booth brain |
| **Pro / open desks** | Lightkey, QLC+, ShowXpress, myDMX 5 | Deep patching, universes | Little musical intelligence |
| **Bridge / visuals** | CueSync, Lightjams, Resolume | OSC/console/pixel | Not an AI LD in a box |

---

## SoundSwitch user pain (research signals)

These pain points define opportunity at the DJ DLW beachhead:

1. **Wrong phrase analysis** — autoscript misfires when beatgrid/sections are off
2. **Autoscript hitting wrong positions** — lectern, cake-cut, ceremony zones get unwanted looks
3. **Presets not saving attributes** — fixture state doesn't round-trip reliably
4. **Multicell as one blob** — pixel/multicell fixtures treated as monolithic channels
5. **Static Looks all-or-nothing** — users want **layered** gobo/prism/frost, not single preset swaps
6. **Engine Lighting cannot run standalone** — requires an actively playing track
7. **~2 universes ceiling** — insufficient for growing mobile rigs

---

## Thesis

Build **one Stage Intelligence layer** that:

1. **Listens** to music (live + library)
2. **Understands structure** (intro, verse, build, drop, breakdown, speech, silence)
3. **Knows the rig** (fixtures, cells, positions, capabilities)
4. **Respects event context** (cocktail, speeches, first dance, dancefloor)
5. **Accepts human overrides** (layered, teachable, non-destructive)
6. **Directs lights** like a junior lighting director — not a chaser, not a randomizer

**Design principle:** *Restraint is a feature.* Wrong phrase detection must **degrade gracefully** (hold, dim, safe look) rather than flash the wrong cue.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUTS                                   │
│  DJ apps · Pro DJ Link · Ableton Link · MIDI clock · line/mic   │
│  stems · drum triggers · setlist · OSC · footswitches           │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
                    ┌────────────────┐
                    │   MUSIC BRAIN   │
                    │ structure · BPM │
                    │ confidence · stems│
                    └────────┬───────┘
                             ▼
                    ┌────────────────┐
                    │    DIRECTOR     │
                    │ roles · idioms  │
                    │ look grammar    │
                    │ event modes     │
                    │ safety rules    │
                    └────────┬───────┘
                             ▼
                    ┌────────────────┐
                    │   RIG MODEL     │
                    │ GDTF · cells    │
                    │ stage plot      │
                    │ forbidden zones │
                    └────────┬───────┘
                             ▼
                    ┌────────────────┐
                    │ PERFORMANCE     │
                    │ SURFACE         │
                    │ desktop/tablet  │
                    │ hardware · layers│
                    │ overrides       │
                    └────────┬───────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUTS                                  │
│  DMX · Art-Net · sACN · Hue/Nanoleaf · OSC to consoles        │
│  pixels · lasers · haze                                         │
└─────────────────────────────────────────────────────────────────┘
```

### Layer responsibilities

| Layer | Role |
|-------|------|
| **Inputs** | Ingest sync and context from every source the booth already uses |
| **Music Brain** | Real-time + library analysis; structure, confidence, stem awareness |
| **Director** | Role assignment, lighting idioms, look grammar, event modes, safety |
| **Rig Model** | Fixture capabilities (GDTF), multicell topology, stage plot, forbidden positions |
| **Performance Surface** | Prep and live UI; layered overrides; teach-from-override |
| **Outputs** | Protocol-agnostic emission to fixtures and downstream consoles |

---

## UX split: Prep vs Perform

| Mode | User | Goals |
|------|------|-------|
| **Prep** | DJ/band LD at home or venue walkthrough | Rig patch, stage plot, forbidden zones, style packs, library pre-analysis, rehearsal |
| **Perform** | Operator under show pressure | Minimal cognitive load, instant overrides, confidence indicators, event-mode switches, graceful degradation |

Prep builds the **Rig Model** and **Director** rules. Perform is the **Performance Surface** — fast, tactile, forgiving.

---

## Push-the-limits (differentiation roadmap)

### Music Brain 2.0

- Library graph + live listener (dual path)
- Confidence scoring per section (when unsure, restrain)
- Stem-aware cues (vocals vs drums vs bass)
- Band MIDI / live instrument triggers
- Speech detection (duck, warm wash, no strobes)

### Director — not a chaser

- **Roles:** key, fill, mover, pixel, haze — not "all fixtures chase"
- **Idioms:** genre- and event-appropriate vocabulary
- **Restraint:** less is more; anti-cheese rules
- **Style packs:** wedding classic, club peak, corporate safe, band rock

### Layered overrides + teach-from-override

- Overrides stack (gobo layer + color layer + movement layer)
- "Do that again" → capture as a reusable cue or rule
- Venue remap: same show file, different rig topology

### Event OS

Modes with distinct Director behavior:

- Cocktail / ambient
- Speeches (warm, static, no movement into faces)
- First dance / slow song
- Dancefloor / peak
- Live band set (MIDI + structure)

### Protocol-agnostic

- Same Director brain → DMX, Art-Net, sACN, Hue, OSC to Chamsys/Avolites/etc.

### Moonshots (Phase 4+)

- CV followspot
- Crowd energy inference
- Generative pixel content
- Copilot chat ("make it more disco, less wedding")
- Show DNA marketplace (shareable style packs)
- Safety brain (laser interlocks, haze limits, venue rules)
- Edge appliance (Wolfmix-class hardware running full stack)
- Rehearsal twin (simulate show before load-in)

---

## Phased roadmap

| Phase | Name | Focus |
|-------|------|-------|
| **0** | Spike | Music Brain accuracy on real DJ libraries; phrase confidence; 1-rig end-to-end |
| **1** | MVP — solo mobile LD | DJ wedding/corporate; 1–2 universes; SoundSwitch-parity sync + better phrase handling |
| **2** | Band & event | Setlists, MIDI, event modes, multicell, venue remap |
| **3** | Scale / pro | Multi-universe, console bridges, style marketplace, team accounts |
| **4** | Moonshots | CV, crowd, edge hardware, generative pixels |

---

## Competitive positioning

| vs | DMX AI difference |
|----|-------------------|
| **SoundSwitch** | Structure-aware Director, not template autoscript; graceful degradation; event modes |
| **MaestroDMX** | Software-first, multi-universe, deep overrides, rig flexibility |
| **Wolfmix** | Per-track storytelling + library prep; AI Director, not one global FX engine |
| **QLC+ / Lightkey** | Musical intelligence built in; not a blank desk |
| **Konductor / MyStrow** | Broader input surface; DJ-native workflow; tactile perform layer |

---

## Success criteria (planning-level)

1. Phrase/section detection **good enough** that users trust autopilot for 80% of a wedding reception
2. Override in **< 1 second** without breaking the show
3. Rig setup in **< 30 minutes** for a typical 12-fixture mobile package
4. Wrong analysis → **safe hold**, never flash strobes at the cake table

---

## Next step

Resolve open questions in [02-decisions.md](02-decisions.md). Minimum **8 answers** required before Phase 0 spike.
