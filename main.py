import os
import time
import webbrowser

import pygame
import pyttsx3
import requests
import speech_recognition as sr
from gtts import gTTS
from openai import OpenAI

import musicLibrary

NEWS_API_ENDPOINT = "https://newsapi.org/v2/top-headlines"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

recognizer = sr.Recognizer()
engine = pyttsx3.init()
client = OpenAI()


def speak_old(text: str) -> None:
    engine.say(text)
    engine.runAndWait()


def speak(text: str) -> None:
    """Try gTTS playback first, then fall back to offline TTS."""
    temp_file = "temp.mp3"
    try:
        tts = gTTS(text)
        tts.save(temp_file)

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
    except Exception:
        speak_old(text)
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass


def ai_process(command: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a virtual assistant named Elsa. "
                        "Give concise, practical responses."
                    ),
                },
                {"role": "user", "content": command},
            ],
        )
        return completion.choices[0].message.content or "I have no response right now."
    except Exception as exc:
        print(f"OpenAI error: {exc}")
        return "I could not reach AI services right now."


def handle_play(command: str) -> None:
    parts = command.split(maxsplit=1)
    if len(parts) < 2:
        speak("Please tell me which song to play.")
        return

    song_query = parts[1].strip().lower()
    link = musicLibrary.music.get(song_query)

    if not link:
        matches = [(name, url) for name, url in musicLibrary.music.items() if song_query in name]
        if len(matches) == 1:
            song_query, link = matches[0]

    if not link:
        available = ", ".join(sorted(musicLibrary.music.keys()))
        speak(f"I could not find that song. Available songs are: {available}")
        return

    webbrowser.open(link)
    speak(f"Playing {song_query}")


def handle_news() -> None:
    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        speak("NEWS API key is missing. Set NEWS_API_KEY environment variable.")
        return

    try:
        response = requests.get(
            NEWS_API_ENDPOINT,
            params={"country": "us", "pageSize": 5, "apiKey": news_api_key},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"News request error: {exc}")
        speak("I could not fetch the news right now.")
        return

    articles = response.json().get("articles", [])
    if not articles:
        speak("No news articles were returned.")
        return

    speak("Here are the top headlines.")
    for article in articles:
        title = article.get("title")
        if title:
            speak(title)


def process_command(command: str) -> None:
    normalized = command.lower().strip()

    if "open google" in normalized:
        webbrowser.open("https://google.com")
        speak("Opening Google")
    elif "open facebook" in normalized:
        webbrowser.open("https://facebook.com")
        speak("Opening Facebook")
    elif "open youtube" in normalized:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")
    elif "open linkedin" in normalized:
        webbrowser.open("https://linkedin.com")
        speak("Opening LinkedIn")
    elif normalized.startswith("play"):
        handle_play(normalized)
    elif "news" in normalized:
        handle_news()
    else:
        speak(ai_process(command))


def listen_once(timeout: int, phrase_time_limit: int) -> str:
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    return recognizer.recognize_google(audio)


def main() -> None:
    speak("Initializing Elsa")
    while True:
        try:
            print("Listening for wake word...")
            wake_word = listen_once(timeout=5, phrase_time_limit=2)
            if wake_word.lower() != "elsa":
                continue

            speak("Yes")
            print("Listening for command...")
            command = listen_once(timeout=6, phrase_time_limit=10)
            print(f"Heard command: {command}")
            process_command(command)
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            continue
        except KeyboardInterrupt:
            print("Stopping assistant.")
            break
        except Exception as exc:
            print(f"Error: {exc}")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
