"""
Automaton Attack Bot — auto-typer for the Dota 2 "Dark Carnival" Automaton Attack
("Unga Wunga") mini-game.

The mini-game asks you to smash out letters as fast as you physically can. Reading
the prompt and pressing the one right letter is slower than simply cycling the whole
alphabet, because a full a→z sweep at machine speed costs a few milliseconds — far
less than any detect-then-react loop. So this bot brute-forces: it cycles the charset
straight into the game and lets the game pick the letters it wants.

What it does beyond a plain typing loop:
  1. Scancode injection (SendInput) instead of virtual-key/unicode writes, so the
     keystrokes look like real hardware to the game.
  2. Window guard — types ONLY while Dota 2 is the focused window, so an accidental
     toggle can never spray the alphabet into Discord, your browser or a terminal.
  3. Global hotkeys — F8 toggles typing at any time; no countdown, no window juggling.
  4. Rate limiting — a keys-per-second cap keeps the game's input queue from
     overflowing and silently dropping keystrokes.
  5. Live stats — keys sent, real keys/sec and elapsed time.

Hotkeys (global)
    F8  — toggle typing ON / OFF (starts OFF)
    F9 / Esc — quit

Run Dota in Borderless / Windowed-Fullscreen, open Automaton Attack, press F8.
"""

import os
import sys
import json
import time
import random
import ctypes

import keyboard
import win32gui

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")

# English letter frequency, most common first — used by order="frequency".
FREQ_ORDER = "etaoinshrdlcumwfgypbvkjxqz"

# ----------------------------- config ---------------------------------------

DEFAULTS = {
    "charset": "abcdefghijklmnopqrstuvwxyz",   # letters to cycle through
    "order": "alphabet",       # "alphabet" | "frequency" | "random"
    "keys_per_second": 500,    # rate cap (0 = uncapped; see README before raising)
    "key_hold": 0.0,           # seconds a key stays held down (0 = instant down+up)
    "burst_size": 0,           # keys per burst before a pause (0 = no bursting)
    "burst_pause": 0.0,        # seconds to pause between bursts
    "send_mode": "scancode",   # "scancode" (game-friendly) | "virtual" (keyboard lib)
    "window_guard": True,      # only type while the target window is focused
    "window_title": "Dota 2",  # case-insensitive substring of the window title
    "start_delay": 0,          # seconds to wait after F8 before the first keystroke
    "max_run_seconds": 0,      # auto-pause after this long of typing (0 = never)
    "hud": True,               # live one-line stats in the console
}


def load_config():
    cfg = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception as e:
            print(f"[warn] could not read config.json ({e}); using defaults")
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in cfg.items() if not k.startswith("_")}, f, indent=2)
    print(f"[ok] saved {CONFIG_PATH}")


# --------------------------- keyboard output --------------------------------
# Low-level scancode injection. Games commonly read raw scancodes and ignore
# synthetic virtual-key/unicode input, so this is the mode that reliably lands.

_SendInput = ctypes.windll.user32.SendInput
_PUL = ctypes.POINTER(ctypes.c_ulong)


class _KBD(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                ("dwExtraInfo", _PUL)]


class _HW(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class _MOUSE(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", _PUL)]


class _II(ctypes.Union):
    _fields_ = [("ki", _KBD), ("mi", _MOUSE), ("hi", _HW)]


class _INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", _II)]


_KEYEVENTF_KEYUP = 0x0002
_KEYEVENTF_SCANCODE = 0x0008

# Set-1 make codes for the letter keys (physical QWERTY positions).
_SCAN = {
    "q": 0x10, "w": 0x11, "e": 0x12, "r": 0x13, "t": 0x14,
    "y": 0x15, "u": 0x16, "i": 0x17, "o": 0x18, "p": 0x19,
    "a": 0x1E, "s": 0x1F, "d": 0x20, "f": 0x21, "g": 0x22,
    "h": 0x23, "j": 0x24, "k": 0x25, "l": 0x26,
    "z": 0x2C, "x": 0x2D, "c": 0x2E, "v": 0x2F, "b": 0x30,
    "n": 0x31, "m": 0x32,
}


def _send_scan(code, keyup):
    flags = _KEYEVENTF_SCANCODE | (_KEYEVENTF_KEYUP if keyup else 0)
    extra = ctypes.c_ulong(0)
    ii = _II()
    ii.ki = _KBD(0, code, flags, 0, ctypes.pointer(extra))
    inp = _INPUT(ctypes.c_ulong(1), ii)
    _SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))


class Typist:
    """Sends single characters, either as scancodes or via the keyboard library."""

    def __init__(self, cfg):
        self.mode = cfg.get("send_mode", "scancode")
        self.hold = max(0.0, float(cfg.get("key_hold", 0.0)))
        self.dry_run = bool(cfg.get("_dry_run"))

    def tap(self, ch):
        if self.dry_run:
            return
        if self.mode == "scancode":
            code = _SCAN.get(ch)
            if code is None:                 # not a letter key — fall back
                keyboard.write(ch)
                return
            _send_scan(code, keyup=False)
            if self.hold > 0:
                time.sleep(self.hold)
            _send_scan(code, keyup=True)
        else:
            keyboard.write(ch)


# --------------------------- window guard -----------------------------------

def foreground_title():
    try:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) or ""
    except Exception:
        return ""


def list_windows():
    """Print every visible titled window — helps users set `window_title`."""
    titles = []

    def _cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if t.strip():
                titles.append(t)
        return True

    win32gui.EnumWindows(_cb, None)
    print("\n=== Visible windows ===")
    for t in sorted(set(titles)):
        print(f"  {t}")
    print("\nCopy the distinctive part of your game's title into config.json "
          "as \"window_title\".")


# ----------------------------- sequence -------------------------------------

def build_sequence(cfg):
    """The charset in the configured order (a fresh list per cycle for 'random')."""
    charset = [c for c in str(cfg.get("charset", "")).lower() if not c.isspace()]
    if not charset:
        charset = list(DEFAULTS["charset"])
    order = cfg.get("order", "alphabet")
    if order == "frequency":
        rank = {c: i for i, c in enumerate(FREQ_ORDER)}
        return sorted(charset, key=lambda c: rank.get(c, len(FREQ_ORDER)))
    if order == "random":
        shuffled = list(charset)
        random.shuffle(shuffled)
        return shuffled
    return charset


# ------------------------------- bot ----------------------------------------

class Bot:
    def __init__(self, cfg):
        self.cfg = cfg
        self.active = bool(cfg.get("_autostart"))
        self.quit = False
        self.typist = Typist(cfg)
        self.wall_limit = float(cfg.get("_seconds", 0) or 0)

        self.keys_sent = 0
        self.active_seconds = 0.0     # time actually spent typing
        self.rate = 0.0               # smoothed keys/sec
        self._hud_line = ""

    # --- hotkeys ---

    def _bind(self):
        keyboard.add_hotkey("f8", self._toggle)
        keyboard.add_hotkey("f9", self._stop)
        keyboard.add_hotkey("esc", self._stop)

    def _toggle(self):
        self.active = not self.active
        self._log(f"[bot] {'TYPING' if self.active else 'paused'}")

    def _stop(self):
        self.quit = True

    # --- console ---

    def _log(self, msg):
        """Print above the live HUD line without leaving fragments behind."""
        if self._hud_line:
            sys.stdout.write("\r" + " " * len(self._hud_line) + "\r")
            self._hud_line = ""
        print(msg)

    def _hud(self, state):
        if not self.cfg.get("hud", True):
            return
        line = (f"  {state}  |  {self.keys_sent:,} keys  |  {self.rate:,.0f}/s  "
                f"|  {self.active_seconds:5.1f}s typing   ")
        sys.stdout.write("\r" + line)
        sys.stdout.flush()
        self._hud_line = line

    # --- main loop ---

    def run(self):
        cfg = self.cfg
        kps = float(cfg.get("keys_per_second", 0) or 0)
        interval = 1.0 / kps if kps > 0 else 0.0
        burst_size = int(cfg.get("burst_size", 0) or 0)
        burst_pause = float(cfg.get("burst_pause", 0.0) or 0.0)
        guard = bool(cfg.get("window_guard", True))
        want_title = str(cfg.get("window_title", "")).lower()
        max_run = float(cfg.get("max_run_seconds", 0) or 0)
        start_delay = float(cfg.get("start_delay", 0) or 0)

        self._bind()
        start_mode = "starts TYPING" if self.active else "starts PAUSED — focus Dota, press F8"
        print(f"\n=== RUNNING ===  ({start_mode})")
        print("  F8 toggle typing | F9/Esc quit")
        if guard:
            print(f"  Window guard ON — only types while a window titled "
                  f"'{cfg.get('window_title')}' is focused.")
        else:
            print("  [!] Window guard OFF — it will type into whatever is focused.")
        if self.typist.dry_run:
            print("  [dry-run] counting keystrokes only — nothing is sent.\n")
        else:
            print()

        seq = build_sequence(cfg)
        idx = 0
        was_active = False
        started_at = 0.0            # when the current typing stretch began
        checked_at = -1.0           # last foreground-window check
        focused = False
        burst_count = 0
        wall_t0 = time.perf_counter()
        window_t0 = wall_t0               # rate-measurement window
        window_keys = 0

        try:
            while not self.quit:
                now = time.perf_counter()

                if self.wall_limit > 0 and now - wall_t0 >= self.wall_limit:
                    break

                if not self.active:
                    if was_active:
                        self.active_seconds += now - started_at
                        was_active = False
                    self._hud("PAUSED  (F8 to start)")
                    time.sleep(0.05)
                    continue

                # Window guard — cached, so we don't ask Windows on every keystroke.
                if guard and now - checked_at >= 0.05:
                    checked_at = now
                    focused = want_title in foreground_title().lower()
                if guard and not focused:
                    if was_active:
                        self.active_seconds += now - started_at
                        was_active = False
                    self._hud(f"WAITING for '{cfg.get('window_title')}'")
                    time.sleep(0.05)
                    continue

                if not was_active:
                    if start_delay > 0:
                        for i in range(int(start_delay), 0, -1):
                            self._log(f"[bot] starting in {i}...")
                            time.sleep(1)
                            if self.quit or not self.active:
                                break
                        if self.quit or not self.active:
                            continue
                    was_active = True
                    started_at = time.perf_counter()
                    window_t0, window_keys = started_at, 0

                # Auto-pause safety valve.
                if max_run > 0 and self.active_seconds + (now - started_at) >= max_run:
                    self.active = False
                    self._log(f"[bot] auto-paused after {max_run:.0f}s "
                              f"(max_run_seconds) — press F8 to resume")
                    continue

                self.typist.tap(seq[idx])
                self.keys_sent += 1
                window_keys += 1
                idx += 1
                if idx >= len(seq):
                    idx = 0
                    if cfg.get("order") == "random":
                        seq = build_sequence(cfg)

                if interval > 0:
                    time.sleep(interval)
                if burst_size > 0:
                    burst_count += 1
                    if burst_count >= burst_size:
                        burst_count = 0
                        if burst_pause > 0:
                            time.sleep(burst_pause)

                # Refresh stats ~4x/second (measured rate, not the configured cap).
                elapsed = time.perf_counter() - window_t0
                if elapsed >= 0.25:
                    self.rate = window_keys / elapsed
                    self.active_seconds += elapsed
                    started_at = window_t0 = time.perf_counter()
                    window_keys = 0
                    self._hud("TYPING")
        finally:
            if was_active:
                self.active_seconds += time.perf_counter() - started_at
            self._log("")
        print(f"[bot] stopped — {self.keys_sent:,} keys sent in "
              f"{self.active_seconds:.1f}s of typing.")


def main():
    if "--windows" in sys.argv:
        list_windows()
        return

    cfg = load_config()
    if "--dry-run" in sys.argv:
        # Nothing is sent, so start immediately — the point is to see the numbers.
        cfg["_dry_run"] = True
        cfg["_autostart"] = True
    if "--start" in sys.argv:
        # Begin typing without waiting for F8. Safe on its own because the window
        # guard still holds fire until the target window is actually focused.
        cfg["_autostart"] = True
    if "--no-guard" in sys.argv:
        cfg["window_guard"] = False
    if "--title" in sys.argv:
        i = sys.argv.index("--title")
        if i + 1 < len(sys.argv):
            cfg["window_title"] = sys.argv[i + 1]
    if "--seconds" in sys.argv:
        i = sys.argv.index("--seconds")
        if i + 1 < len(sys.argv):
            cfg["_seconds"] = float(sys.argv[i + 1])
    if not os.path.exists(CONFIG_PATH):
        save_config(cfg)      # first launch: drop a config.json the user can tweak

    Bot(cfg).run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
