from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/sobre")
async def sobre(request: Request):
    return templates.TemplateResponse("sobre.html", {"request": request}) 