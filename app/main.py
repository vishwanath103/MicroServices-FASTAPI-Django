import uuid
import pathlib
import os
import io
from functools import lru_cache
from fastapi import(
        FastAPI,
        Depends,
        Request,
        File,
        UploadFile,
        HTTPException
        )
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from PIL import Image

class Settings(BaseSettings):
    debug: bool = False
    echo_active: bool = False

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()

DEBUG = settings.debug
BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

print(DEBUG)
@app.get("/",response_class=HTMLResponse)
def home_view(request: Request, settings:Settings = Depends(get_settings)):
    print(request)
    return templates.TemplateResponse("home.html",{"request": request,"abc":123})

@app.post("/")
def home_detail_view():
    return {"hello":"world"}

@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(file:UploadFile = File(...), settings:Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(detail="Invalid endpoint", status_code=400)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid image", status_code=400)
    fname = pathlib.Path(file.filename)
    fext = fname.suffix
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    img.save(dest)
    return dest
