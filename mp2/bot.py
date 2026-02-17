import os
import time

import keyboard
import pyautogui
import pyperclip
from openai import OpenAI

# Optional environment config
MY_NAME = os.getenv("MY_NAME", "Your Name")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Coordinates are configurable as "x,y" in env vars.
# Defaults keep your existing values.
def parse_point(env_name: str, fallback: tuple[int, int]) -> tuple[int, int]:
    raw = os.getenv(env_name)
    if not raw:
        return fallback
    try:
        x_str, y_str = raw.split(",")
        return int(x_str.strip()), int(y_str.strip())
    except ValueError:
        print(f"Invalid {env_name}='{raw}', using fallback {fallback}")
        return fallback


CHROME_ICON = parse_point("CHROME_ICON", (1639, 1412))
CHAT_TOP_LEFT = parse_point("CHAT_TOP_LEFT", (972, 202))
CHAT_BOTTOM_RIGHT = parse_point("CHAT_BOTTOM_RIGHT", (2213, 1278))
CLEAR_SELECTION = parse_point("CLEAR_SELECTION", (1994, 281))
INPUT_BOX = parse_point("INPUT_BOX", (1808, 1328))

client = OpenAI()


def get_last_sender(chat_log: str) -> str | None:
    messages = chat_log.strip().splitlines()
    for line in reversed(messages):
        if "]" in line and ":" in line:
            try:
                sender = line.split("]", 1)[1].split(":", 1)[0].strip()
                if sender:
                    return sender
            except (IndexError, ValueError):
                continue
    return None


def generate_reply(chat_history: str) -> str:
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Naruto, a funny bilingual Indian coder who roasts people in Hinglish. "
                    "Given chat history, respond with a clever roast. "
                    "Output only the next message, no sender name or time."
                ),
            },
            {"role": "user", "content": chat_history},
        ],
    )
    return (completion.choices[0].message.content or "").strip()


def main() -> None:
    print("Script starts in 3 seconds. Press ESC to stop.")
    time.sleep(3)

    pyautogui.click(*CHROME_ICON)
    time.sleep(1)

    while True:
        if keyboard.is_pressed("esc"):
            print("Script stopped by user.")
            break

        time.sleep(5)

        pyautogui.moveTo(*CHAT_TOP_LEFT)
        pyautogui.dragTo(*CHAT_BOTTOM_RIGHT, duration=2.0, button="left")
        time.sleep(0.5)

        pyautogui.hotkey("ctrl", "c")
        time.sleep(1)

        pyautogui.click(*CLEAR_SELECTION)

        chat_history = pyperclip.paste().strip()
        if not chat_history:
            print("Clipboard is empty. Retrying...")
            continue

        sender = get_last_sender(chat_history)
        print("Last sender:", sender)

        if not sender or sender == MY_NAME:
            print("Message is from you or sender unknown. Skipping...\n")
            continue

        print(f"Generating roast reply to {sender}...")
        try:
            response = generate_reply(chat_history)
        except Exception as exc:
            print(f"OpenAI error: {exc}")
            continue

        if not response:
            print("Model returned empty response. Skipping...")
            continue

        print("AI Reply:\n", response)

        pyperclip.copy(response)
        pyautogui.click(*INPUT_BOX)
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("enter")


if __name__ == "__main__":
    try:
        main()
    except pyautogui.FailSafeException:
        print("PyAutoGUI fail-safe triggered. Mouse moved to a corner.")
    except Exception as exc:
        print("Error:", str(exc))
