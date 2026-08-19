# DMX AI

macOS desktop DMX lighting controller for live color control over ENTTEC interfaces.

**Default fixture:** Bothlighting 12×18W RGBWA+UV PAR @ DMX address 1, personality **10CH A001**.

## Quick start (macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Requires an ENTTEC DMX USB **Pro** (VID:PID `0403:6001`) on `/dev/cu.usbserial-*`. Open DMX is supported as fallback.

## Hardware notes

- Use the **5-pin FEMALE (DMX OUT)** → 5-to-3-pin adapter → fixture **DMX IN**
- Do **not** use the 5-pin male jack (that is input)
- ENTTEC green LED blinking = DMX transmitting
- Fixture menu: **A001**, **10CH**, **Slave/DMX**
- If colors strobe instead of mixing, switch personality to **10CH Alt** (Rockville Wedge map)

## Personalities

| Mode | Map |
|------|-----|
| **10CH A001** (default) | CH1 Master, CH2 Strobe, CH3–4 = 0, CH5–10 RGBWA+UV |
| **6CH D001** | CH1–6 RGBWA+UV |
| **10CH Alt** | CH1 Master, CH2–7 RGBWA+UV, CH8 Strobe, CH9–10 = 0 |

## Planning docs

Research and product planning from Aug 2026:

- [docs/CHAT.md](docs/CHAT.md)
- [docs/planning/01-market-and-product-plan.md](docs/planning/01-market-and-product-plan.md)
- [docs/planning/02-decisions.md](docs/planning/02-decisions.md)

## Owner

Raymond — [ivstudiogroup@gmail.com](mailto:ivstudiogroup@gmail.com)
