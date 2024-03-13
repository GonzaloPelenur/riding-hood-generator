from typing import Union

from fastapi import FastAPI

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from complit import riding_hood

app = FastAPI()

app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/ridinghood/{color}", response_class=HTMLResponse)
def web_riding_hood(color: str):
    return riding_hood(color)
    # return """
    # <html>
    #     <head>
    #         <title>Hint Of Mint</title>
    #     </head>
    #     <body>
    #         <h1>Resources</h1>
    #         <a href="/static/Stories/story17/little-Stories/story17/-riding-hood.pdf" download="little-Stories/story17/-riding-hood.pdf" style="margin-bottom:20px;display:inline-block;background-color:#4CAF50;color:white;padding:14px 20px;text-align:center;text-decoration:none;display:inline-block;font-size:16px;border-radius:8px;">Download PDF</a>
    #         <br>
    #         <h1>Little Hint Of Mint Riding Hood</h1>
    
    #         <img src="/static/Stories/story17/image-0.png" alt="Image">
    #         <audio controls>
    #             <source src="/static/Stories/story17/audio-0.mp3" type="audio/mp3">
    #             Your browser does not support the audio element.
    #         </audio>
        
    #         <img src="/static/Stories/story17/image-1.png" alt="Image">
    #         <audio controls>
    #             <source src="/static/Stories/story17/audio-1.mp3" type="audio/mp3">
    #             Your browser does not support the audio element.
    #         </audio>
        
    #         <img src="/static/Stories/story17/image-2.png" alt="Image">
    #         <audio controls>
    #             <source src="/static/Stories/story17/audio-2.mp3" type="audio/mp3">
    #             Your browser does not support the audio element.
    #         </audio>
        
    #         <img src="/static/Stories/story17/image-3.png" alt="Image">
    #         <audio controls>
    #             <source src="/static/Stories/story17/audio-3.mp3" type="audio/mp3">
    #             Your browser does not support the audio element.
    #         </audio>
        
    #         <img src="/static/Stories/story17/image-4.png" alt="Image">
    #         <audio controls>
    #             <source src="/static/Stories/story17/audio-4.mp3" type="audio/mp3">
    #             Your browser does not support the audio element.
    #         </audio>
        
    #         <img src="/static/Stories/story17/image-5.png" alt="Image">
    #         <audio controls>
    #             <source src="/static/Stories/story17/audio-5.mp3" type="audio/mp3">
    #             Your browser does not support the audio element.
    #         </audio>
        
    #         </body>
    #     </html>
    # """
#