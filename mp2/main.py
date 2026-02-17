import os
from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI()

chat_history = """
[20:30, 12/6/2024] Naruto: jo sunke coding ho sake?
[20:30, 12/6/2024] Rohan Das: https://www.youtube.com/watch?v=DzmG-4-OASQ
[20:30, 12/6/2024] Rohan Das: ye
[20:31, 12/6/2024] Naruto: This is hindi
[20:31, 12/6/2024] Naruto: send me some english songs
[20:31, 12/6/2024] Naruto: but wait
[20:31, 12/6/2024] Naruto: this song is amazing
[20:31, 12/6/2024] Naruto: so I will stick to it
[20:31, 12/6/2024] Naruto: send me some english song also
[20:31, 12/6/2024] Rohan Das: hold on
[20:31, 12/6/2024] Naruto: I know what you are about to send
[20:32, 12/6/2024] Naruto: haha
[20:32, 12/6/2024] Rohan Das: https://www.youtube.com/watch?v=ar-3chBG4NU
ye hindi English mix hai but best hai
[20:33, 12/6/2024] Naruto: okok
[20:33, 12/6/2024] Rohan Das: Haan
""".strip()

try:
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are continuing a WhatsApp chat between Indian friends who speak Hinglish. "
                    "Reply like the next participant in an informal tone. "
                    "Output only one next message without names or timestamps."
                ),
            },
            {"role": "user", "content": chat_history},
        ],
    )
    print("\nNext reply in the chat:\n")
    print(completion.choices[0].message.content)
except Exception as exc:
    print(f"OpenAI request failed: {exc}")
    print("Set OPENAI_API_KEY in your environment and try again.")
