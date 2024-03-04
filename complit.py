color_input = "banana-crepe"
# color_input = "almond-oil"
import json
import pathlib
import textwrap
from dotenv import load_dotenv
import google.generativeai as genai
import google.ai.generativelanguage as glm
from fpdf import FPDF
from io import BytesIO

# from IPython.display import Image, display, HTML
# from IPython.display import Markdown

# from google.colab import userdata

from openai import OpenAI
import textwrap
import os

from PIL import Image
from PIL import ImageDraw, ImageFont


import requests
load_dotenv()
# def set_css():
#   display(HTML('''
#   <style>
#     pre {
#         white-space: pre-wrap;
#     }
#   </style>
#   '''))
# get_ipython().events.register('pre_run_cell', set_css)

# def to_markdown(text):
#     text = text.replace('•', '  *')
#     return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))



# GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
model_vision = genai.GenerativeModel('gemini-pro-vision')


# client = OpenAI(api_key = userdata.get('OPENAI_API_KEY'))
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

with open('pantone-colors-by-key.json') as f:
    pantone = json.load(f)
# print(pantone)
color = pantone[color_input]
first = True
    
def generate_story(color):

    prompt = f"'Little {color['Name']} Riding Hood' is a spin off picture book story of 'Little Red Riding Hood' where the main character's color is called {color['Name']} instead of Red, and has the specific color {color['Name']}. The story is written for kids. Create a script for this picture book, following the previous description. Return a list of paragraphs, each corresponding to one page of the picture book. Be creative, the story is based on 'Little Red Riding Hood’, but the setting of the story can be anywhere, it doesn’t have to be in a forest, choose an appropriate setting based on the color name."

    response = model.generate_content(prompt)

# print(response.text)
# print("here is some feedback on your prompt")
# print(response.prompt_feedback)

# to_markdown(response.text)
    pages = []
    for content in response.text.split("\n"):
        if len(content)>0 and "*" not in content:
            pages.append(content)
    print(pages)
    return pages

def generate_character_description(pages):
    pages_str = " ".join(pages)
    prompt = f"Write a detailed description of physical appearance the character 'Little {color['Name']} Riding Hood' for a picture book. The character should be wearing a vibrant hooded cloak in the specific color {color['Name']}, emphasize that the hood should be of that color. The character should be a child. The description should be detailed and include the character's hair color, eye color, clothing style, clothes color, and everything else that is relevant to the character's appearance. Make your description concise and detailed only in the physical aspects. Do not mention anything other than the physical appearance of the character. Limit your answer to 150 words."
    response = model.generate_content(prompt)
    description = response.text
    print(f"Character Description:\n{description}")
    return description


def generate_image(page, character_description, num, style, save_name="story"):
    print("---------------------------")
    print(f"Generating image for page: {num}")
    while True:
        # generate_prompt = f"Imagine you are a student that needs to create an image for a picture book. Write a text that you can use later as an input to generate an image using an AI image generator. The prompt you write should follow these guideilines: The image should be in the style of a children's picture book illustration, like Bruno Munari. The scene should feature a character named '{color['Name']} Riding Hood,' wearing a vibrant hooded cloak in the specific color {color['Name']}, emphasize that the hood should be of that color. The scene that the image refers to is: '{page}.’"
        # # print(generate_prompt)
        # image_prompt = model.generate_content(generate_prompt).text
        # image_prompt += f" Do NOT add text in the image. The illustration should have bold outlines, a textured appearance, and a whimsical charm, emulating the look of hand-drawn art with colored pencils and watercolors. Remember to use the specific color '{color['Name']}'. Leave a blank space in the image for the text. The style should be similar to Bruno Munari. Here is a detailed description of the character: '{character_description}'."

        # image_prompt = style + f" The scene that the image refers to is: '{page}'. Here is a detailed description of the character: '{character_description}'. Do NOT add text in the image. Remember to use the specific color '{color['Name']}'. Leave a blank space in one of the corners of the image."
        scene_description = get_scene_decritpion(page)
        image_prompt = f"Create an image in the following style: '{style}'. This is the scene description: '{scene_description}'. Here is a detailed description of the character: '{character_description}'. Do NOT add text in the image. Remember to use the specific color '{color['Name']}'. Leave a blank space in one of the corners of the image."
        # print("PROMPT GENERATED")
        # print(response.text)
        # to_markdown(image_prompt)
        print("Image Prompt: ")
        print(image_prompt)
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        # print(f"Image URL: {image_url}")
        im = Image.open(requests.get(image_url, stream=True).raw)
        im.show()
        print("---------------------------")
        print("USER INPUT REQUIRED")
        print("Do you like the image? (y/n)")
        user_input = input("response: ")
        print("---------------------------")
        if user_input != "n":
            break
        print("Got it. Will try again")        
    image_url = save_name+f"image-{num}.png"
    im.save(image_url)
    print(f"Finished generating image for page: {num}")
    print("---------------------------")
    return image_url

    # display(Image(url=image_url, width=500))

def get_style(image_path):
    response = model_vision.generate_content(
    glm.Content(
        parts = [
            glm.Part(text="Describe the style of the image in detail. Talk about the color scheme, the texture, the line work, and the overall feel of the image. Be as detailed as possible. Describe any details that you would need to know to recreate the style of the image without looking at it. Limit your answer to 150 words."),
            glm.Part(
                inline_data=glm.Blob(
                    mime_type='image/'+image_path.split(".")[-1],
                    data=pathlib.Path(image_path).read_bytes()
                )
            ),
        ],
    ))
    style = response.text
    print(f"New Style: {style}")
    return style
    

def get_scene_decritpion(page):
    prompt = f"Imagine the following scene as a picture book illustration: '{page}'. Write a detailed visual description of the scene. Don't write about the story, only the setting, what does the scene look like? Talk about the colors, characters, objects, and the overall feel of the scene. Be as detailed as possible. Describe any details that you would need to know to recreate the scene without looking at it. Limit your answer to 150 words."
    response = model.generate_content(prompt)
    description = response.text
    return description
# generate_image(pages[0])
def text_to_image(pages, character_description, style, save=False, save_path="story"):
    story = []
    for i,page in enumerate(pages):
        print(f"PAGE {i} out of {len(pages)}:")
        print(page)
        url = generate_image(page, character_description, i, style, save_name=save_path)
        coords = get_text_coordinates(url, page)
        overlay_text(url, page, coords)
        story.append({"text": page, "image_url": url})
        if i == 0:
            style = get_style(url)
    if save:
        with open(save_path+"story.json", "w") as fp:
            json.dump(story, fp)
    return story

def get_text_coordinates(image_url, text):
    response = model_vision.generate_content(
    glm.Content(
        parts = [
            glm.Part(text=f"I want to add the following text to the image: {text}. Find a place in the image that is not near the center of the image, and does not cover any character or important figure. Give me the coordinates to place the text in the image in that place. Return (x, y): This X and Y denotes the starting position(in pixels)/coordinate of adding the text on an image. Choose a corner, never choose the center."),
            glm.Part(
                inline_data=glm.Blob(
                    mime_type='image/png',
                    data=pathlib.Path(image_url).read_bytes()
                )
            ),
        ],
    ))
    print(response.text)
    return eval(response.text)

def overlay_text(image_url, text, coordinates):
    img = Image.open(image_url)
    width, height = img.size
    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(img)
    
    # Add Text to an image
    text_width = 50
    font_size = 30
    myFont = ImageFont.truetype('DancingScript-Bold.ttf', font_size)
    margin = coordinates[0]
    if margin +text_width > width:
        margin = width - text_width - 10
    offset = coordinates[1]
    for line in textwrap.wrap(text, width=text_width):
        I1.text((margin, offset), line, font=myFont, fill="#000000", stroke_fill="#ffffff", stroke_width=3)
        offset += font_size
    # I1.text(coordinates, wraped, font=myFont, fill=(0, 0, 0))
    
    # Display edited image
    # img.show()
    img.save(image_url)

def save_pdf(story, save_path):
    pdf = FPDF()
    for page in story:
        image = page["image_url"]
        pdf.add_page()
        pdf.image(image, x=10, y=8, w=190)
    pdf.output(f"{save_path}little-{color_input}-riding-hood.pdf", "F")


def main():
    style = f"Create an image for a children’s picture book in the style of Bruno Munari. The drawing style  in the image should be a playful blend of graphic design and illustration, characterized by its use of bold outlines, a focused yet subdued color scheme centered around the color of'{color['Name']}', and textural patterns that impart depth. The style employs a mix of stylization and realism, with exaggerated features in the figures and more detailed depictions of accompanying elements, creating a whimsical and modern aesthetic that is appealing in children's literature."
    save_path = "story8/"
    pages = generate_story(color)
    character = generate_character_description(pages)
    # print(character)
    story = text_to_image(pages, character, style, save=True, save_path=save_path)
    save_pdf(story, save_path)

if __name__ == "__main__":
    main()
    # text = "In a bustling metropolis known as Cr\u00eapeland, there lived a young girl named Banana Cr\u00eape. Her skin was as golden and smooth as the beloved pastry, and her eyes sparkled with a warm amber hue. One sunny morning, Banana Cr\u00eape's mother asked her to deliver a basket of freshly baked cr\u00eapes to her grandmother, who lived on the other side of the city."
    # image_url = "story3/story-0.png"
    # coords = get_text_coordinates(image_url, text)
    # overlay_text(image_url, text, coords)
    # with open('story3/story.json') as f:
    #     story = json.load(f)
    # save_pdf(story)
    # character = "Banna Cr\u00eape is a young girl with golden hair and blue eyes. She is wearing a vibrant hooded cloak in the specific color Banana Cr\u00eape."
    # generate_image(text, character, 101, save_name="test")
    # print(get_style("story4/image-1.png"))
    # print(get_scene_decritpion(text))