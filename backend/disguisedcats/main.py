import shutil
from typing import Annotated, Literal
from uuid import UUID

import svcs
import nanoid
from fastapi import FastAPI, Request, Response, Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from disguisedcats import db
from disguisedcats import log
from disguisedcats.log import logger
from disguisedcats.settings import settings
from disguisedcats.sessions import session


@svcs.fastapi.lifespan
async def lifespan(app: FastAPI, registry: svcs.Registry):
    await db.connect()
    registry.register_factory(AsyncIOMotorClient, db.get, ping=db.ping)
    yield
    await db.close()


app = FastAPI(lifespan=lifespan)
log.setup()
app.middleware("http")(log.middleware)
app.mount("/static", StaticFiles(directory=settings.STATIC_PATH), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request, services: svcs.fastapi.DepContainer) -> Response:
    """Index page of the service."""
    hostname = request.headers.get("Host", request.base_url.hostname)
    if (
        hostname == settings.HOSTNAME
        or hostname == f"{settings.HOSTNAME}:{settings.PORT}"
    ):
        return templates.TemplateResponse(request=request, name="index.html")
    try:
        # TODO turn on only for debug-mode
        app_id, _, _ = hostname.split(".")
    except Exception:
        logger.debug("Invalid hostname: %s", request.base_url.hostname)
        return Response(status_code=400)

    _db = await services.aget(AsyncIOMotorClient)
    result = await _db.apps.find_one({"_id": app_id})
    if result:
        return templates.TemplateResponse(
            request=request,
            name="app.html",
            context={
                "app_name": result["name"],
                "app_preset": result["preset"],
                "peerjs_host": settings.PEERJS_HOST,
                "peerjs_port": settings.PEERJS_PORT,
                "peerjs_path": settings.PEERJS_PATH,
            },
        )

    logger.debug("Invalid hostname: %s", request.base_url.hostname)
    return Response(status_code=400)


def generate_app_id() -> str:
    return nanoid.generate("0123456789abcdefghijklmnopqrstuvwxyz", 10)


@app.post("/create")
async def create_app(
    request: Request,
    services: svcs.fastapi.DepContainer,
    name: Annotated[str, Form()],
    icon: Annotated[UploadFile, File()],
    preset: Annotated[Literal["cats"], Form()],
) -> Response:
    """Create new app from the form."""
    app_id = generate_app_id()
    new_url = f"https://{app_id}.{settings.HOSTNAME}:{settings.PORT}"

    _db = await services.aget(AsyncIOMotorClient)
    await _db.apps.insert_one({"_id": app_id, "name": name, "preset": preset})

    icon_extension = icon.filename.split(".")[-1]
    icon_path = settings.STATIC_PATH / f"{app_id}.{icon_extension}"
    with open(icon_path, "wb+") as f:
        shutil.copyfileobj(icon.file, f)

    return templates.TemplateResponse(
        request=request, name="partials/new_app_url.html", context={"new_url": new_url}
    )


class CreateSessionRequest(BaseModel):
    peer_id: UUID


class CreateSessionResponse(BaseModel):
    session_id: str


@app.post("/session")
async def create_init_session(request: Request, data: CreateSessionRequest) -> Response:
    session_id = nanoid.generate("0123456789", 6)
    if session.get(session_id):
        session_id = nanoid.generate("0123456789", 6)
    await session.set(session_id, data.peer_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/new_init_session.html",
        context={"session_id": session_id},
    )


class GetSessionResponse(BaseModel):
    peer_id: UUID


@app.get("/session/{session_id}")
async def get_session(session_id: str) -> GetSessionResponse:
    peer_id = await session.get(session_id)
    if peer_id is None:
        return Response(status_code=400)
    return GetSessionResponse(peer_id=peer_id)


@app.get("/health")
async def health(services: svcs.fastapi.DepContainer) -> JSONResponse:
    ok: list[str] = []
    failing: list[dict[str, str]] = []
    code = 200

    for svc in services.get_pings():
        try:
            await svc.aping()
            ok.append(svc.name)
        except Exception as e:
            failing.append({svc.name: repr(e)})
            code = 500

    return JSONResponse(content={"ok": ok, "failing": failing}, status_code=code)
