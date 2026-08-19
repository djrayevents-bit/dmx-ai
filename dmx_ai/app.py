"""CustomTkinter desktop UI for live DMX color control."""

from __future__ import annotations

import tkinter as tk
from typing import Dict, List, Optional

import customtkinter as ctk

from dmx_ai.controller import DMXController
from dmx_ai.devices import DMXDevice, list_dmx_devices
from dmx_ai.personalities import PERSONALITY_NAMES, PRESETS, ColorMix


# Button colors (display approximations for RGBWA+UV mixes)
BUTTON_COLORS: Dict[str, str] = {
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "White": "#FFFFFF",
    "Amber": "#FFBF00",
    "UV": "#BF00FF",
    "Magenta": "#FF00FF",
    "Cyan": "#00FFFF",
    "Yellow": "#FFD700",
    "Orange": "#FF6600",
    "Pink": "#FF69B4",
    "Warm": "#FFB366",
    "Full": "#FFFFFF",
    "Blackout": "#1A1A1A",
}


class DMXApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("DMX AI — Live Color Control")
        self.geometry("720x780")
        self.minsize(640, 700)

        self._controller = DMXController(on_status=self._on_status, on_mix_changed=self._on_mix_changed)
        self._devices: List[DMXDevice] = []
        self._slider_vars: Dict[str, tk.IntVar] = {}
        self._updating_ui = False

        self._build_ui()
        self._refresh_devices()
        self.after(500, self._try_auto_connect)

    # ── UI construction ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        # Device bar
        device_frame = ctk.CTkFrame(self)
        device_frame.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        device_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(device_frame, text="Device", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=(12, 8), pady=12
        )

        self._device_var = tk.StringVar(value="")
        self._device_menu = ctk.CTkOptionMenu(
            device_frame, variable=self._device_var, values=["Scanning…"], width=340
        )
        self._device_menu.grid(row=0, column=1, padx=4, pady=12, sticky="ew")

        ctk.CTkButton(device_frame, text="Refresh", width=80, command=self._refresh_devices).grid(
            row=0, column=2, padx=4, pady=12
        )
        self._connect_btn = ctk.CTkButton(
            device_frame, text="Connect", width=100, command=self._toggle_connect
        )
        self._connect_btn.grid(row=0, column=3, padx=(4, 12), pady=12)

        self._status_label = ctk.CTkLabel(
            device_frame, text="● Disconnected", text_color="#FF6B6B", font=ctk.CTkFont(size=13)
        )
        self._status_label.grid(row=1, column=0, columnspan=4, padx=12, pady=(0, 10), sticky="w")

        # Personality
        pers_frame = ctk.CTkFrame(self)
        pers_frame.grid(row=1, column=0, padx=16, pady=8, sticky="ew")

        ctk.CTkLabel(pers_frame, text="Personality", font=ctk.CTkFont(weight="bold")).pack(
            side="left", padx=(12, 8), pady=10
        )
        self._personality_var = tk.StringVar(value="10CH A001")
        self._personality_seg = ctk.CTkSegmentedButton(
            pers_frame,
            values=list(PERSONALITY_NAMES),
            variable=self._personality_var,
            command=self._on_personality_change,
        )
        self._personality_seg.pack(side="left", padx=8, pady=10)

        # Color preview
        preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        preview_frame.grid(row=2, column=0, padx=16, pady=4, sticky="ew")
        ctk.CTkLabel(preview_frame, text="Preview").pack(side="left", padx=(0, 8))
        self._preview = ctk.CTkFrame(preview_frame, width=80, height=40, corner_radius=8)
        self._preview.pack(side="left")
        self._preview.configure(fg_color="#000000")

        # Color buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=3, column=0, padx=16, pady=8, sticky="ew")
        btn_frame.grid_columnconfigure(tuple(range(7)), weight=1)

        color_names = list(BUTTON_COLORS.keys())
        for i, name in enumerate(color_names):
            fg = BUTTON_COLORS[name]
            text_color = "#000000" if name in ("White", "Yellow", "Warm", "Full", "Amber") else "#FFFFFF"
            btn = ctk.CTkButton(
                btn_frame,
                text=name,
                fg_color=fg,
                hover_color=fg,
                text_color=text_color,
                height=36,
                command=lambda n=name: self._apply_preset(n),
            )
            btn.grid(row=i // 7, column=i % 7, padx=4, pady=4, sticky="ew")

        # Sliders
        slider_frame = ctk.CTkFrame(self)
        slider_frame.grid(row=4, column=0, padx=16, pady=8, sticky="ew")
        slider_frame.grid_columnconfigure(1, weight=1)

        slider_defs = [
            ("Master", "master"),
            ("Red", "red"),
            ("Green", "green"),
            ("Blue", "blue"),
            ("White", "white"),
            ("Amber", "amber"),
            ("UV", "uv"),
            ("Strobe", "strobe"),
        ]
        for row, (label, key) in enumerate(slider_defs):
            var = tk.IntVar(value=255 if key == "master" else 0)
            self._slider_vars[key] = var
            ctk.CTkLabel(slider_frame, text=label, width=60, anchor="w").grid(
                row=row, column=0, padx=(12, 4), pady=6, sticky="w"
            )
            slider = ctk.CTkSlider(
                slider_frame,
                from_=0,
                to=255,
                number_of_steps=255,
                variable=var,
                command=lambda v, k=key: self._on_slider(k, int(float(v))),
            )
            slider.grid(row=row, column=1, padx=4, pady=6, sticky="ew")
            val_label = ctk.CTkLabel(slider_frame, text="0", width=36)
            val_label.grid(row=row, column=2, padx=(4, 12), pady=6)
            var.trace_add("write", lambda *_a, v=var, lbl=val_label: lbl.configure(text=str(v.get())))

        # Footer
        footer = ctk.CTkLabel(
            self,
            text="Use 5-pin FEMALE (DMX OUT) → 5-to-3-pin adapter → fixture DMX IN. "
            "Fixture: A001 / 10CH / Slave-DMX. If colors strobe instead of mixing, try 10CH Alt.",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            wraplength=680,
            justify="left",
        )
        footer.grid(row=5, column=0, padx=16, pady=(8, 16), sticky="ew")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Device / connection ──────────────────────────────────────────

    def _refresh_devices(self) -> None:
        self._devices = list_dmx_devices()
        labels = [d.label for d in self._devices] if self._devices else ["No devices found"]
        self._device_menu.configure(values=labels)
        if self._devices:
            self._device_var.set(labels[0])
        else:
            self._device_var.set(labels[0])

    def _selected_device(self) -> Optional[DMXDevice]:
        label = self._device_var.get()
        for d in self._devices:
            if d.label == label:
                return d
        return self._devices[0] if self._devices else None

    def _try_auto_connect(self) -> None:
        if not self._controller.connected and self._devices:
            self._controller.connect(self._selected_device())

    def _toggle_connect(self) -> None:
        if self._controller.connected:
            self._controller.disconnect()
        else:
            dev = self._selected_device()
            if dev is None:
                self._warn_disconnected()
                return
            self._controller.connect(dev)

    def _on_mix_changed(self, mix: ColorMix) -> None:
        self.after(0, lambda: self._sync_sliders_from_mix(mix))

    def _on_status(self, connected: bool, message: str) -> None:
        def update() -> None:
            if connected:
                self._status_label.configure(text=f"● {message}", text_color="#51CF66")
                self._connect_btn.configure(text="Disconnect")
            else:
                self._status_label.configure(text=f"● {message}", text_color="#FF6B6B")
                self._connect_btn.configure(text="Connect")

        self.after(0, update)

    def _warn_disconnected(self) -> None:
        self._status_label.configure(text="● Disconnected — connect to send DMX", text_color="#FF6B6B")

    # ── Color / sliders ──────────────────────────────────────────────

    def _on_personality_change(self, value: str) -> None:
        self._controller.set_personality(value)
        if not self._controller.connected:
            return
        self._sync_sliders_from_mix(self._controller.mix)

    def _apply_preset(self, name: str) -> None:
        if not self._controller.connected:
            self._warn_disconnected()
            return
        mix = self._controller.apply_preset(name)
        self._sync_sliders_from_mix(mix)

    def _on_slider(self, key: str, value: int) -> None:
        if self._updating_ui:
            return
        if not self._controller.connected:
            self._warn_disconnected()
            return

        mix = self._controller.mix
        fields = dict(
            master=mix.master,
            red=mix.red,
            green=mix.green,
            blue=mix.blue,
            white=mix.white,
            amber=mix.amber,
            uv=mix.uv,
            strobe=mix.strobe,
        )
        fields[key] = value
        new_mix = ColorMix(**fields)
        self._controller.set_mix(new_mix)
        self._update_preview(new_mix)

    def _sync_sliders_from_mix(self, mix: ColorMix) -> None:
        self._updating_ui = True
        try:
            for key, var in self._slider_vars.items():
                var.set(getattr(mix, key))
        finally:
            self._updating_ui = False
        self._update_preview(mix)

    def _update_preview(self, mix: ColorMix) -> None:
        # Approximate RGB preview from RGBWA+UV (simple blend)
        r = min(255, mix.red + mix.amber // 2 + mix.white // 3)
        g = min(255, mix.green + mix.amber // 3 + mix.white // 3)
        b = min(255, mix.blue + mix.uv // 2 + mix.white // 3)
        scale = mix.master / 255.0
        r, g, b = int(r * scale), int(g * scale), int(b * scale)
        self._preview.configure(fg_color=f"#{r:02X}{g:02X}{b:02X}")

    def _on_close(self) -> None:
        self._controller.disconnect()
        self.destroy()


def run() -> None:
    app = DMXApp()
    app.mainloop()
