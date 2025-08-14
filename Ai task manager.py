import pyttsx3
import speech_recognition as sr
import matplotlib.pyplot as plt
from datetime import datetime

engine = pyttsx3.init()
r = sr.Recognizer()

def speak(text): 
    print(text); 
    engine.say(text);
    engine.runAndWait()

def listen():
    with sr.Microphone() as src:
        speak("Listening...")
        try:
            audio = r.listen(src, timeout=5)
            return r.recognize_google(audio).lower()
        except: return ""

def load(): 
    try: return open("task.txt").read().splitlines()
    except: return []

def save(tasks): open("task.txt", "w").write("\n".join(tasks))

def show_menu():
    speak("Welcome To Personal AI Task Managger")
    speak("1.👁️View Today | 2.📝Add | 3.❌Delete | 4.🔚Exit | 5.🔁Update | 6.🗓️ All Task")

def main():
    tasks = load()
    method = input("Voice(v) or Keyboard(k)? ").lower()
    get_input = listen if method == 'v' else lambda: input("Enter choice (1-6): ")

    while True:
        show_menu()
        ch = get_input()

        if ch in ['1','one']:
            today = datetime.now().strftime("%Y-%m-%d")
            today_tasks = [t for t in tasks if f"| {today}" in t]
            if not today_tasks: speak("No tasks today.")
            else:
                for i, t in enumerate(today_tasks,1): speak(f"{i}. {t}")
                plt.pie([1]*len(today_tasks), labels=today_tasks); plt.title(today); plt.show()

        elif ch in ['2','two']:
            task = input("Task: ").strip()
            if task:
                entry = f"{task} | {datetime.now().strftime('%Y-%m-%d')}"
                if entry not in tasks:
                    tasks.append(entry); save(tasks); speak("Task added.")
                else: speak("Already exists.")
            else: speak("Task empty.")

        elif ch in ['3','three']:
            if not tasks: speak("No tasks."); continue
            for i,t in enumerate(tasks,1): speak(f"{i}. {t}")
            try:
                idx = int(input("Delete Task #: ")) - 1
                if 0 <= idx < len(tasks): speak(f"Deleted: {tasks.pop(idx)}"); save(tasks)
            except: speak("Invalid number.")

        elif ch in ['4','four']: speak("Bye!"); break

        elif ch in ['5','five']:
            if not tasks: speak("No tasks."); continue
            for i,t in enumerate(tasks,1): speak(f"{i}. {t}")
            try:
                idx = int(input("Update Task #: ")) - 1
                new = input("New Task: ").strip()
                if new:
                    tasks[idx] = f"{new} | {datetime.now().strftime('%Y-%m-%d')}"
                    save(tasks); speak("Updated.")
            except: speak("Invalid.")

        elif ch in ['6','six']:
            for i,t in enumerate(tasks,1): speak(f"{i}. {t}")

        else: speak("Wrong choice.")

main()
