# ⌨️ Automaton Attack Bot — Auto-Typer for Dota 2 "Automaton Attack" (Dark Carnival Minigame)

**A free, open-source auto-typer that plays the Dota 2 _Automaton Attack_ mini-game** (the "Unga Wunga" mash-the-keyboard game in the **Dark Carnival** event). It fires the whole alphabet into the game hundreds of times per second — far faster than any human can mash — so you rack up a record without wrecking your keyboard.

<p align="center">
  <a href="https://github.com/codedpro/dark-carnival-automaton-attack-bot/releases/latest">
    <img alt="Download the latest release" src="https://img.shields.io/github/v/release/codedpro/dark-carnival-automaton-attack-bot?label=Download%20.exe&style=for-the-badge">
  </a>
  <img alt="Platform: Windows" src="https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge">
  <img alt="Python 3.12" src="https://img.shields.io/badge/python-3.12-yellow?style=for-the-badge">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge"></a>
</p>

<p align="center"><b>⚡ ~500 keystrokes per second — roughly 60× a fast human masher.</b></p>

> **Keywords:** Dota 2 Automaton Attack bot · Dark Carnival minigame auto-typer · Unga Wunga typer · Dota 2 event script · autohotkey alternative · Python keyboard macro · Windows game automation · alphabet spammer.

> ⭐ **If this bot earns you a record, please [star the repo](https://github.com/codedpro/dark-carnival-automaton-attack-bot) — it helps others find it!**

---

## ✨ Features

- ⚡ **Machine-speed typing** — cycles the alphabet at a configurable rate (default **500 keys/sec**).
- 🛡️ **Window guard** — types **only** while Dota 2 is the focused window. An accidental toggle can never spray `abcdefg…` into Discord, your browser, or a work document. _This is on by default._
- 🎮 **Scancode injection** — sends raw hardware-style scancodes via `SendInput`, the method games actually read, instead of unicode "write" calls that many games ignore.
- 🖱️ **Global hotkeys** — **F8** starts and stops from anywhere; no countdown timer, no window juggling.
- 📊 **Live stats** — real keys sent, measured keys/sec, and typing time, updating as you play.
- 🧪 **Safe dry-run** — `test.bat` shows exactly how fast your PC will type **without sending a single key anywhere**.
- 🔧 **Zero calibration** — no screen capture, no colour picking, no setup. Download, run, press F8.

---

## 🚀 Quick Start — Two Easy Ways

### 🟢 Option 1 — The easy way (no Python, no setup)

1. **[⬇️ Download `automaton-attack-bot.exe` from the latest release](https://github.com/codedpro/dark-carnival-automaton-attack-bot/releases/latest).**
2. Double-click it. _(Windows SmartScreen may warn about an unrecognized app — click **More info → Run anyway**. The full source is right here in this repo, so you can see exactly what it does.)_
3. Alt-tab to Dota, open **Automaton Attack**, and press **F8**. Press **F8** again (or **Esc**) to stop.

### 🔵 Option 2 — Run from source (auto-installs everything)

Don't have Python? No problem — the launcher installs it for you.

1. Click the green **`< > Code`** button above → **Download ZIP**, and unzip it anywhere.
2. Double-click **`run.bat`**.
   - The first launch automatically installs Python (if missing) and all required packages into a local folder — **you don't need to install anything by hand**.
3. Alt-tab to Dota, open **Automaton Attack**, and press **F8**.

> 💡 Nothing is installed system-wide. Everything lives in a local `.venv` folder next to the bot. Delete the folder and it's gone.

---

## 🎮 Before You Start

1. Run Dota in **Borderless / Windowed-Fullscreen**. Exclusive fullscreen also works, but alt-tabbing is smoother in borderless.
2. Open the **Automaton Attack** mini-game and get to the screen where you mash keys.
3. Press **F8**. The bot only types while Dota is focused, so it's safe to leave running between rounds.

That's the whole setup — there is no calibration step.

---

## ⌨️ Hotkeys (work anywhere)

| Key | Action |
|-----|--------|
| **F8** | Toggle typing **ON / OFF** (starts OFF) |
| **F9 / Esc** | Quit |

---

## 🛡️ The Window Guard (why this is safe)

An alphabet spammer with no safety net is genuinely dangerous — one forgotten toggle and it types thousands of letters into whatever you alt-tab to.

This bot checks the **focused window title** before every burst. If it doesn't contain `"Dota 2"`, it sends nothing and the status line reads `WAITING for 'Dota 2'`. You can leave it toggled ON permanently and it will simply idle while you're in your browser, then resume the instant Dota is focused again.

If the guard never fires, run **`windows.bat`** — it lists every open window title so you can copy the right one into `config.json` as `window_title`.

---

## ⚙️ Tuning (`config.json`)

The bot writes `config.json` on first launch. Most people never touch it.

| Field | Meaning |
|-------|---------|
| `keys_per_second` | Rate cap. Default `500`. Set `0` for uncapped — but see the warning below |
| `charset` | Which letters to cycle. Default `"abcdefghijklmnopqrstuvwxyz"` |
| `order` | `"alphabet"` (a→z), `"frequency"` (common English letters first), or `"random"` (reshuffles each cycle, so it can't sync up with the game's letter pattern) |
| `send_mode` | `"scancode"` (default; what games read) or `"virtual"` (fallback using the `keyboard` library) |
| `window_guard` | `true`/`false` — only type while the target window is focused. **Leave this on** |
| `window_title` | Case-insensitive substring of the target window title. Default `"Dota 2"` |
| `key_hold` | Seconds a key stays held down. Default `0.0` (instant press+release). Raise to `0.01` if the game misses keys |
| `burst_size` / `burst_pause` | Send N keys, then pause this many seconds. Both `0` by default. Use if the game's input queue overflows |
| `start_delay` | Seconds to wait after pressing F8 before the first keystroke. Default `0` |
| `max_run_seconds` | Auto-pause after this much typing time (`0` = never). A safety valve |
| `hud` | `true`/`false` — show the live stats line |

> ⚠️ **On `keys_per_second: 0`:** uncapped typing can send tens of thousands of keys per second, which overflows Windows' per-thread message queue. The game then **silently drops** most of them, so you often score *worse* while pegging a CPU core. The 500/s default is already ~60× human speed. Raise it gradually and watch the measured rate in the HUD.

---

## 🖥️ Command-line flags

Handy if you launch from a terminal or a shortcut:

| Flag | Effect |
|------|--------|
| `--dry-run` | Count keystrokes and show the speed **without sending anything**. Starts immediately |
| `--start` | Begin typing without waiting for F8 (the window guard still applies) |
| `--seconds N` | Run for N seconds, then exit — useful for benchmarking |
| `--title "X"` | Override `window_title` for this run |
| `--no-guard` | Disable the window guard. **Only combine with `--dry-run`** |
| `--windows` | List every open window title and exit |

---

## 🩺 Troubleshooting

| Problem | Fix |
|---------|-----|
| **Status stuck on `WAITING for 'Dota 2'`** | Dota isn't the focused window. Click into the game. If it still waits, run **`windows.bat`** and copy your exact title into `window_title` |
| **Nothing is typed even though it says `TYPING`** | Switch `send_mode` to `"virtual"`. If Dota runs elevated (as Administrator), run the bot as Administrator too — Windows blocks input from lower-privilege processes |
| **The game misses most keystrokes** | Lower `keys_per_second` (try `200`), or raise `key_hold` to `0.01` |
| **Score is worse than expected** | You're likely flooding the input queue. Lower `keys_per_second` — faster is not always better |
| **F8 does nothing** | Another app may have grabbed the hotkey. Close other macro tools, or run the bot as Administrator |
| **Antivirus flags the .exe** | Expected for PyInstaller builds that send keystrokes. Use **Option 2** (run from source) if you'd rather not add an exception — the source is 300 lines and right here |
| **Want to check your speed safely?** | Run **`test.bat`** — it's a dry run that sends nothing |

---

## 🧠 How It Works

The mini-game asks you to smash out letters as fast as you physically can. The bot doesn't read the screen — it just cycles the alphabet straight into the game and lets the game take the letters it wants.

**Why brute force beats reading the screen:** a full a→z sweep at 500 keys/sec takes about **52 ms**. Any detect-then-react loop — screen capture, OCR the prompt, decide, press — costs more than that per letter, and it can be wrong. Typing every letter is guaranteed to include the right one, and it's faster. So there's no OpenCV here, no calibration, and nothing to break when Valve nudges the UI.

Keystrokes go out through `SendInput` with `KEYEVENTF_SCANCODE`, which produces the same hardware-level scancodes a real keyboard sends. This matters because many games — Dota included — ignore synthetic virtual-key and unicode input. No game memory is read, nothing is injected into the Dota process, and no network traffic is touched: the bot only presses keys, exactly like a human, just faster.

---

## 🧩 Requirements (source install)

Handled automatically by `run.bat`, but for reference: **Windows**, **Python 3.12**, and the packages in [`requirements.txt`](requirements.txt) (`keyboard`, `pywin32`).

---

## 🕹️ More Dark Carnival bots

| Bot | Mini-game |
|-----|-----------|
| [🥾 **Boot Breaker Bot**](https://github.com/codedpro/boot-breaker-bot) | The Arkanoid / brick-breaker game — OpenCV paddle control |
| [🔓 **Pick the Lock Bot**](https://github.com/codedpro/pick-the-lock-bot) | The rotating lockpick game — tracks the pick and clicks the bars |
| ⌨️ **Automaton Attack Bot** | You are here |

---

## 🙏 Credits

The original brute-force idea and the first working script come from [**Naterro/DarkCarnivalAutomatonAttackScript**](https://github.com/Naterro/DarkCarnivalAutomatonAttackScript). This repo rebuilds it with a window guard, scancode injection, rate limiting, global hotkeys, live stats, a config file, a one-click launcher, and a prebuilt `.exe`.

---

## ⚠️ Disclaimer

This is a **hobby / educational input-automation project** for a single-player mini-game. Use it at your own risk and in accordance with the Dota 2 / Steam Terms of Service. The authors are not responsible for how you use it. Not affiliated with or endorsed by Valve.

## 📄 License

Released under the [MIT License](LICENSE). Contributions welcome — open an issue or PR!
