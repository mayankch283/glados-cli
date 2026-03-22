#!/usr/bin/env python3
"""
FORM-29827281-12: Aperture Science LLM Interface
  "Still Alive" - A Chat CLI themed after Portal's end credits

Requires:
    pip install huggingface_hub rich

Usage:
    HF_TOKEN=your_token python still_alive_chat.py
"""

import os
import sys
import time
import random
import threading
from datetime import datetime

try:
    from huggingface_hub import InferenceClient
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.text import Text
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.layout import Layout
    from rich import box
except ImportError:
    print("Missing deps. Run: pip install huggingface_hub rich")
    sys.exit(1)

# ── Aperture amber palette ──────────────────────────────────────────────────
AMBER      = "#D4870A"
AMBER_DIM  = "#8B5A00"
AMBER_BRT  = "#FFB347"
BG         = "black"
MODEL      = "deepseek-ai/DeepSeek-R1:fastest"

console = Console(style=f"{AMBER} on {BG}", highlight=False)

# ── ASCII art right panel (GLaDOS silhouette, rendered in amber chars) ──────
GLADOS_ART = r"""
             .,-:;//;:=,
         . :H@@@MM@M#H/.,+%;,
      ,/X+ +M@@M@MM%=,-%HMMM@X/,
     -+@MM; $M@@MH+-,;XMMMM@MMMM@+-
    ;@M@@M- XM@X;. -+XXXXXHHH@M@M#@/.
  ,%MM@@MH ,@%=            .---=-=:=,.
  -@#@@@MX .,              -%HX$$%%%+;
 =-./@M@M$                  .;@MMMM@MM:
 X@/ -$MM/                    .+MM@@@M$
,@M@H: :@:                    . -X#@@@@-
,@@@MMX, .                    /H- ;@M@M=
.H@@@@M@+,                    %MM+..%#$.
 /MMMM@MMH/.                  XM@MH; -;
  /%+%$XHH@$=              , .H@@@@MX,
   .=--------.           -%H.,@@@@@MX,
   .%MM@@@HHHXX$$$%+- .:$MMX -M@@MM%.
     =XMMM@MM@MM#H;,-+HMM@M+ /MMMX=
       =%@M@M#@$-.=$@MM@@@M; %M%=
         ,:+$+-,/H#MMMMMMM@- -,
               =++%%%%+/:-.
"""

# ── Aperture "form" header ───────────────────────────────────────────────────
FORM_HEADER = [
    "Forms FORM-29827281-12:",
    "Test Assessment Report",
    "",
    "",
    "This was a triumph.",
    "I'm making a note here:",
    "HUGE SUCCESS.",
    "It's hard to overstate",
    "my satisfaction.",
    "Aperture Science",
    "We do what we must",
    "because we can.",
    "For the good of all of us.",
    "Except the ones who are dead.",
    "",
    "But there's no sense crying",
    "over every mistake.",
]

CAKE = r"""
            ,:/+/-
            /M/              .,-=;//;-
       .:/= ;MH/,    ,=/+%$XH@MM#@:
      -$##@+$###@H@MMM#######H:.    -/H#
 .,H@H@ X######@ -H#####@+-     -+H###@X
  .,@##H;      +XM##M/,     =%@###@X;-
X%-  :M##########$.    .:%M###@%:
M##H,   +H@@@$/-.  ,;$M###@%,          -
M####M=,,---,.-%%H####M$:          ,+@##
@##################@/.         :%H##@$-
M###############H,         ;HM##M$=
#################.    .=$M##M$=
################H..;XM##M$=          .:+
M###################@%=           =+@MH%
@#################M/.         =+H#X%=
=+M###############M,      ,/X#H+:,
  .;XM###########H=   ,/X#H+:;
     .=+HM#######M+/+HM@+=.
         ,:/%XM####H/.
              ,.:=-.
"""

CLOSING_LYRICS = [
    "You just keep on trying",
    "till you run out of cake.",
    "And the science gets done,",
    "and you make a neat gun",
    "for the people who are",
    "still alive.",
]

# ── Typewriter helper ────────────────────────────────────────────────────────
def typewrite(text: str, delay: float = 0.04, style: str = AMBER) -> None:
    for ch in text:
        console.print(ch, end="", style=style)
        time.sleep(delay)
    console.print()


# ── Build the two-panel "Still Alive" layout ─────────────────────────────────
def render_splash() -> None:
    console.clear()

    left_lines  = FORM_HEADER[:]
    right_lines = GLADOS_ART.split("\n")

    # Pad both sides to equal height
    height = max(len(left_lines), len(right_lines))
    left_lines  += [""] * (height - len(left_lines))
    right_lines += [""] * (height - len(right_lines))

    separator = "||"

    for i, (l, r) in enumerate(zip(left_lines, right_lines)):
        left_text  = Text(f": {l:<38}", style=AMBER)
        sep_text   = Text(separator, style=AMBER_DIM)
        right_text = Text(f" {r}", style=AMBER)

        console.print(left_text + sep_text + right_text)
        time.sleep(0.03)

    console.print()
    console.rule(style=AMBER_DIM)
    console.print()


# ── Chat session ─────────────────────────────────────────────────────────────
def aperture_prompt() -> str:
    """Render the GLaDOS-flavoured input prompt."""
    console.print(
        Text("> SUBJECT INPUT: ", style=f"bold {AMBER_BRT}"),
        end="",
    )
    try:
        return input()
    except (EOFError, KeyboardInterrupt):
        return "/exit"


def render_thinking() -> None:
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    console.print(
        Text(": APERTURE AI PROCESSING ", style=AMBER_DIM),
        end="",
        style=AMBER_DIM,
    )
    for _ in range(12):
        for f in frames:
            console.print(f, end="", style=AMBER_DIM)
            time.sleep(0.06)
            console.print("\b", end="")
    console.print()


def stream_response(client: InferenceClient, history: list[dict]) -> str:
    """Stream the LLM response with amber typewriter effect."""
    render_thinking()

    console.print(Text(": APERTURE AI >> ", style=f"bold {AMBER_BRT}"), end="")

    full = ""
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=history,
            stream=True,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            if delta:
                console.print(delta, end="", style=AMBER)
                full += delta
    except Exception as exc:
        console.print(
            f"\n[ERROR] {exc}",
            style=f"bold {AMBER_BRT}",
        )
    console.print()
    console.print()
    return full


# ── Command handling ─────────────────────────────────────────────────────────
COMMANDS = {
    "/exit":  "Terminate session",
    "/clear": "Clear conversation history",
    "/help":  "Show available commands",
    "/song":  "Hear the rest of Still Alive",
}

def handle_command(cmd: str, history: list) -> bool:
    """Returns True if session should end."""
    cmd = cmd.strip().lower()

    if cmd in ("/exit", "/quit", "/q"):
        console.print()
        console.rule(style=AMBER_DIM)
        for line in CAKE.split("\n"):
            console.print(Text(line, style=AMBER), justify="center")
            time.sleep(0.03)
        console.print()
        console.print(
            Text(": THE CAKE IS A LIE!", style=f"bold {AMBER_BRT}"),
            justify="center",
        )
        console.print()
        console.print(Text(": [SESSION TERMINATED]", style=f"bold {AMBER_BRT}"))
        console.print()
        return True

    elif cmd == "/clear":
        history.clear()
        console.print(Text(": Memory wiped. Science continues.", style=AMBER_DIM))
        console.print()

    elif cmd == "/help":
        console.print()
        for c, desc in COMMANDS.items():
            console.print(Text(f":   {c:<10} — {desc}", style=AMBER_DIM))
        console.print()

    elif cmd == "/song":
        console.print()
        for line in CLOSING_LYRICS:
            typewrite(f": {line}", delay=0.06)
            time.sleep(0.08)
        console.print()

    else:
        console.print(Text(f": Unknown command: {cmd}. Try /help", style=AMBER_DIM))
        console.print()

    return False


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    client  = InferenceClient()
    history: list[dict] = []

    # System prompt — GLaDOS flavour, but still helpful
    history.append({
        "role": "system",
        "content": (
            "You are an Aperture Science AI assistant. "
            "You are helpful, precise, and occasionally remind the user "
            "that science must go on. Keep responses concise unless asked otherwise."
        ),
    })

    render_splash()

    console.print(Text(": APERTURE SCIENCE LLM INTERFACE ONLINE", style=f"bold {AMBER_BRT}"))
    console.print(Text(f": Model: {MODEL}", style=AMBER_DIM))
    console.print(Text(": Type /help for commands, /exit to terminate.", style=AMBER_DIM))
    console.print()

    while True:
        user_input = aperture_prompt().strip()

        if not user_input:
            continue

        if user_input.startswith("/"):
            if handle_command(user_input, history):
                break
            continue

        history.append({"role": "user", "content": user_input})
        response = stream_response(client, history)

        if response:
            history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
