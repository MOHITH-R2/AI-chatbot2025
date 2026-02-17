import os
from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI()

completion = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[
        {
            "role": "system",
            "content": (
                "You are a virtual assistant named Elsa skilled in general tasks. "
                "Keep answers short and practical."
            ),
        },
        {"role": "user", "content": "What is coding?"},
    ],
)

print(completion.choices[0].message.content)
