import pyautogui
import time
import pyperclip
import keyboard
from openai import OpenAI

# --- Your info ---
MY_NAME = "Your Name"  # <-- Change this to your name as it appears in chat

# --- OpenAI API setup ---
client = OpenAI(
    api_key="API_KEY=YOUR_API_KEY_HERE"  # Replace with your real API key
)

# --- Helper: Get last message sender ---
def get_last_sender(chat_log):
    messages = chat_log.strip().splitlines()
    for line in reversed(messages):
        if "]" in line and ":" in line:
            try:
                sender = line.split("]")[1].split(":")[0].strip()
                return sender
            except:
                continue
    return None

# --- Main loop ---
def main():
    print("Script starting in 3 seconds... Press ESC to stop.")
    time.sleep(3)

    # Step 1: Click Chrome icon
    pyautogui.click(1639, 1412)
    time.sleep(1)

    while True:
        if keyboard.is_pressed("esc"):
            print("Script stopped by user.")
            break

        time.sleep(5)

        # Step 2: Select the chat text
        pyautogui.moveTo(972, 202)
        pyautogui.dragTo(2213, 1278, duration=2.0, button='left')
        time.sleep(0.5)

        # Step 3: Copy to clipboard
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(2)

        # Step 4: Click to remove selection
        pyautogui.click(1994, 281)

        # Step 5: Read chat
        chat_history = pyperclip.paste()
        print("Copied chat:\n", chat_history)

        sender = get_last_sender(chat_history)
        print("Last sender:", sender)

        if sender and sender != MY_NAME:
            print(f"Generating roast reply to {sender}...")

            # Step 6: Call OpenAI
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Naruto, a funny bilingual Indian coder who roasts people in Hinglish. "
                            "Given chat history, respond with a clever roast. Output ONLY the next message, no sender name or time."
                        )
                    },
                    {"role": "user", "content": chat_history}
                ]
            )

            response = completion.choices[0].message.content.strip()
            print("AI Reply:\n", response)

            # Step 7: Copy response
            pyperclip.copy(response)

            # Step 8: Click message box, paste and send
            pyautogui.click(1808, 1328)
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)
            pyautogui.press('enter')

        else:
            print("Message is from you or sender unknown. Skipping...\n")

# --- Run safely ---
if __name__ == "__main__":
    try:
        main()
    except pyautogui.FailSafeException:
        print("PyAutoGUI fail-safe triggered! Mouse moved to corner.")
    except Exception as e:
        print("Error:", str(e))
