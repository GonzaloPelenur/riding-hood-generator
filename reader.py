import json
from pdf2image import convert_from_path
import os
from openai import OpenAI
from dotenv import load_dotenv
from playsound import playsound
import cv2
import numpy as np
import threading

load_dotenv() 
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = OPENAI_API_KEY)

with open('Stories/story10/story.json') as f:
    story = json.load(f)

pages = convert_from_path('Stories/story10/little-moonstruck-riding-hood2.pdf', 500)
print(len(pages))

for i, page in enumerate(story):
    text = page['text']
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    response.stream_to_file(f"output{i}.mp3")
    # playsound(f"output{i}.mp3")

def play_sound(file):
    playsound(file)
for i, page in enumerate(pages):
    # page.show()
    image = np.array(page)
    image = image[:, :, ::-1].copy()
    cv2.imshow(f'Page {i+1}', image)
    t1 = threading.Thread(target=play_sound, args=(f"output{i}.mp3",))
    t1.start()
    # playsound(f"output{i+1}.mp3")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    t1.join()
    # sleep(2)
    os.remove(f"output{i}.mp3")
