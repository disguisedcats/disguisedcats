from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get('/')
def index(request: Request) -> Response:
    return templates.TemplateResponse(request=request, name="item.html")

@app.post('/create')
def create_app(request: Request) -> Response:
    new_url = 'https://XAyk9BNvYM.example.loc:9999'
    return templates.TemplateResponse(
        request=request, name="partials/new_app_url.html" , context={'new_url': new_url}
    )
