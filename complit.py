# color_input = "banana-crepe"
# color_input = "almond-oil"
color_input = "moonstruck"
import json
import pathlib
import textwrap
from dotenv import load_dotenv
import google.generativeai as genai
import google.ai.generativelanguage as glm
from fpdf import FPDF
from io import BytesIO
import img2pdf
from pypdf import PdfMerger


# from IPython.display import Image, display, HTML
# from IPython.display import Markdown

# from google.colab import userdata

from openai import OpenAI
import textwrap
import os

from PIL import Image
import base64
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

reference_id = None

initial_style = f"Create an image for a children’s picture book in the style of Bruno Munari. The drawing style of the image should be simple and hand drawn with pencil. It is, characterized by its use of bold outlines, a simple and muted color scheme centered around the color of'{color['Name']}', and textural patterns that impart depth. Avoid using many colors. Create simple aesthetic that is appealing in children's literature."

initial_chdescription_prompt = f"Write a detailed description of physical appearance the character 'Little {color['Name']} Riding Hood' for a picture book. The character should be wearing a hooded cloak in the specific color {color['Name']}, emphasize that the hood should be of that color. The character should be a child. The description should be detailed and include the character's hair color, eye color, clothing style, clothes color, and everything else that is relevant to the character's appearance. Do not use many colors apart from the color {color['Name']}. Make your description concise and detailed only in the physical aspects. Do not mention anything other than the physical appearance of the character. Make the style look simple and easy to replicate. Limit your answer to 150 words."

update_character_description_prompt = f"In the image provided there is character named 'Little {color['Name']} Riding Hood' wearing a hood. The character should a child wearing a hooded cloak in the specific color {color['Name']}.  Describe the style of that character in detail. The description should be detailed and include the character's racial features, skin color, height, hair color, eye color, clothing style, clothes color, and everything else that is relevant to the character's appearance. Be very specific about physical details, do not use abstract concepts. Talk about the color scheme, the texture, the line work, and the overall feel of the character. Write your answer in 100 words."

def generate_story(color):

    prompt = f"'Little {color['Name']} Riding Hood' is a spin off picture book story of 'Little Red Riding Hood' where the main character's color is called {color['Name']} instead of Red, and has the specific color {color['Name']}. The story is written for kids. Create a script for this picture book, following the previous description. Return a list of paragraphs, each corresponding to one page of the picture book. Write 5 pages. Be creative, the story is based on 'Little Red Riding Hood’, but the setting of the story can be anywhere, it doesn’t have to be in a forest, choose an appropriate and creative setting based on the color name. Limit your answer to 5 pages."

    response = model.generate_content(prompt)
    pages = []
    for content in response.text.split("\n"):
        if len(content)>0 and "*" not in content:
            pages.append(content)
    print(pages)
    return pages

def generate_character_description(pages, style, save_name):
    print("---------------------------")
    print("Generating character description")
    pages_str = " ".join(pages)
    # prompt = f"Write a detailed description of physical appearance the character 'Little {color['Name']} Riding Hood' for a picture book. The character should be wearing a vibrant hooded cloak in the specific color {color['Name']}, emphasize that the hood should be of that color. The character should be a child. The description should be detailed and include the character's hair color, eye color, clothing style, clothes color, and everything else that is relevant to the character's appearance. Make your description concise and detailed only in the physical aspects. Do not mention anything other than the physical appearance of the character. Limit your answer to 150 words."
    prompt =  initial_chdescription_prompt + f" Any information you might need to know about the character is in the story: '{pages_str}'."
    response = model.generate_content(prompt)
    description = response.text
    print(f"Character Description:\n{description}")

    image_prompt = f"Create an image of 'Little {color['Name']} Riding Hood' for a children's picture book in the following style: '{style}'. Here is a detailed description of the character: '{description}'. Do NOT add text in the image."
    image_prompt += " I NEED to test how the tool workswith this EXACT prompt. DO NOT add any detail, just use it AS-IS"

    while True:
        print("Generating image for character description")
        print("Image Prompt: ")
        print(image_prompt)
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1792x1024",
            style="natural",
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
    image_url = save_name+f"image-0.png"
    im.save(image_url)
    print(f"Finished generating image for character description")
    print("---------------------------")
    description = update_character_description(image_url)

    return description

def update_character_description(image_path):
    response = model_vision.generate_content(
    glm.Content(
        parts = [
            glm.Part(text=update_character_description_prompt),
            glm.Part(
                inline_data=glm.Blob(
                    mime_type='image/'+image_path.split(".")[-1],
                    data=pathlib.Path(image_path).read_bytes()
                )
            ),
        ],
    ))
    description = response.text
    print(f"New Character Description: {description}")
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
        scene_description = get_scene_decritpion(page, style)
        image_prompt = f"Create an image in the following style: '{style}'. This is the scene description: '{scene_description}'. Here is a detailed description of the character: '{character_description}'. Do NOT add text in the image. Remember to use the specific color '{color['Name']}'. Leave a blank space in one of the corners of the image."
        image_prompt += " I NEED to test how the tool workswith this EXACT prompt. DO NOT add any detail, just use it AS-IS"
        # print("PROMPT GENERATED")
        # print(response.text)
        # to_markdown(image_prompt)
        print("Image Prompt: ")
        print(image_prompt)
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1792x1024",
            style="natural",
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

def get_style(image_path, style):
    response = model_vision.generate_content(
    glm.Content(
        parts = [
            glm.Part(text=f"Describe the drawing style of the image in detail. Talk about the color scheme, the texture, the line work. Be as detailed as possible. Describe any details that you would need to know to recreate another unrelated scene in the same style of the image without the original image. Here is a reference for style that would be valid: {style}. Limit your answer to 150 words."),
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

def get_scene_decritpion(page,style):
    prompt = f"Imagine the following scene as a picture book illustration: '{page}'. Write a detailed visual description of the scene. Don't write about the story, only the setting, what does the scene look like? Talk about the colors, characters, objects, and the overall feel of the scene. Be as detailed as possible. Describe any details that you would need to know to recreate the scene without looking at it. Limit your answer to 150 words. The scene should follow this style: {style}."
    response = model.generate_content(prompt)
    description = response.text
    return description

def text_to_image(pages, character_description, style, save=False, save_path="story"):
    story = [{"text": "This is the story of Little Banana Crepe Riding Hood", "image_url": save_path+"image-0.png"}]
    style = get_style(story[0]["image_url"], style)
    for i,page in enumerate(pages):
        num = i+1
        print(f"PAGE {num} out of {len(pages)}:")
        # print(page)
        url = generate_image(page, character_description, num, style, save_name=save_path)
        # coords = get_text_coordinates(url, page)
        position = choose_corner("Stories/story8/image-2.png")
        overlay_text(url, page, position)
        story.append({"text": page, "image_url": url})
        if i == 0:
            style = get_style(url, style)
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

def overlay_text(image_url, text, position):
    print(f"Overlaying text on the {position} corner of the image")
    # position contains a string that is either top-left, top-right, bottom-left, bottom-right.
    position = position.lower()
    img = Image.open(image_url)
    width, height = img.size

    midpoint_x, midpoint_y = width // 2, height // 2
    coordinates = None
    offset = 50
    # Determine the top-left coordinate of the specified quadrant
    if position == "top-left":
        coordinates = (offset, offset)
    elif position == "top-right":
        coordinates = (midpoint_x + offset, offset)
    elif position == "bottom-left":
        coordinates = (offset, midpoint_y+offset)
    elif position == "bottom-right":
        coordinates = (midpoint_x+offset, midpoint_y+offset)
    else:
        raise ValueError("Position must be 'top-left', 'top-right', 'bottom-left', or 'bottom-right'.")
    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(img)
    
    # Add Text to an image
    text_width = 50
    font_size = 30
    myFont = ImageFont.truetype('Font/Dancing_Script/static/DancingScript-Bold.ttf', font_size)
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
    # pdf = FPDF()
    # for page in story:
    #     image = page["image_url"]
    #     pdf.add_page()
    #     pdf.image(image, x=10, y=8, w=190)
    # pdf.output(f"{save_path}little-{color_input}-riding-hood.pdf", "F")
    pdfs = []
    for page in story:
        image = page["image_url"]
        image_pdf = image.split(".")[0]+".pdf"
        image_to_pdf(image,image_pdf)
        pdfs.append(image_pdf)
    merge_pdfs(pdfs, save_path)

def merge_pdfs(pdfs, save_path):

    merger = PdfMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write(save_path+"little-"+color_input+"-riding-hood.pdf")
    merger.close()

def image_to_pdf(img_path, pdf_path):
    image = Image.open(img_path)
 
    # converting into chunks using img2pdf
    pdf_bytes = img2pdf.convert(image.filename)
    
    # opening or creating pdf file
    file = open(pdf_path, "wb")
    
    # writing pdf files with chunks
    file.write(pdf_bytes)
    
    # closing image file
    image.close()
    
    # closing pdf file
    file.close()

def choose_corner(image_url):
    images = split_image(image_url)
    prompt = "Here are four images, each image is a corner of a whole image. The corners are labeled top-left, top-right, bottom-left, bottom-right. Choose one of the corners that is suitable to write a text on top of it. When choosing a corner of an image to overlay text, DO NOT choose a corner that has a a face or an animal. The ideal location is one where the background is simple and uncluttered, offering high contrast with the text color for clear readability. It should avoid obscuring key visual elements or the central subject of the image, maintain the overall balance and composition, and utilize available negative space. The chosen corner should also have consistent lighting to prevent text distortion due to shadows or highlights, and it should not cover any crucial elements that contribute to the image's message or context. These considerations ensure that the text is both legible and harmoniously integrated into the image. If possible, do  choose any image that might feature a face or an animal. Choose one of the corners and write the name of the corner in the response. Return only one word, corresponding to the chosen corner."
    messages = [{
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt
          }
        ]
      }]
    for base64_image in encode_image(images):
        messages[0]["content"].append(
        {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/png;base64,{base64_image}"
            }
          })
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": messages,
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # print(response.json())
    print(response.json()["choices"][0]["message"]["content"])
    return response.json()["choices"][0]["message"]["content"]

def split_image(image_url):
    # Crop the image into four pieces
    image = Image.open(image_url)
    width, height = image.size
    split_width = width // 2
    split_height = height // 2
    top_left = image.crop((0, 0, split_width, split_height))
    top_right = image.crop((split_width, 0, split_width * 2, split_height))
    bottom_left = image.crop((0, split_height, split_width, split_height * 2))
    bottom_right = image.crop((split_width, split_height, split_width * 2, split_height * 2))
    return top_left, top_right, bottom_left, bottom_right

def encode_image(images):
    encoded_images = []
    for image in images:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        # Base64 encode
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        # Store the base64 string with appropriate label
        encoded_images.append(img_str)
    return encoded_images

def main():
    # style = f"Create an image for a children’s picture book in the style of Bruno Munari. The drawing style  in the image should be a playful blend of graphic design and illustration, characterized by its use of bold outlines, a focused yet subdued color scheme centered around the color of'{color['Name']}', and textural patterns that impart depth. The style employs a mix of stylization and realism, with exaggerated features in the figures and more detailed depictions of accompanying elements, creating a whimsical and modern aesthetic that is appealing in children's literature."
    style = f"Create an image for a children’s picture book in the style of Bruno Munari. The drawing style of the image should be simple and hand drawn with pencil. It is, characterized by its use of bold outlines, a simple and muted color scheme centered around the color of'{color['Name']}', and textural patterns that impart depth. Avoid using many colors. Create simple aesthetic that is appealing in children's literature."
    save_path = "Stories/story8/"
    pages = generate_story(color)
    character = generate_character_description(pages, style, save_path)
    # print(character)
    story = text_to_image(pages, character, style, save=True, save_path=save_path)
    save_pdf(story, save_path)

if __name__ == "__main__":
    main()
    # choose_corner("Stories/story7/image-2.png")
    # for image in split_image("Stories/story8/image-2.png"):
    #     image.show()
    # image_to_pdf("Images/forest.png", "Images/forest.pdf")
    # merge_pdfs(["Images/forest.pdf", "Images/cafe.pdf"],"Images/")
    # position = choose_corner("Stories/story8/image-2.png")
    # overlay_text("Stories/story8/image-2.png", "Once upon a time, in a sugary-sweet land, there lived a little girl named Banana Crepe. Her skin was as golden and velvety as a freshly baked crepe, with a lovely hue that was as bright as the sun.", "top-left")