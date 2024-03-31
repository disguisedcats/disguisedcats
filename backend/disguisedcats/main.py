import shutil
from typing import Annotated, Literal
from uuid import UUID

import svcs
import nanoid
from fastapi import FastAPI, Request, Response, Form, File, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from disguisedcats import db
from disguisedcats import log
from disguisedcats.log import logger
from disguisedcats.posts import post_router
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

app.include_router(post_router, prefix="/api")


@app.get("/")
async def index(request: Request, services: svcs.fastapi.DepContainer) -> Response:
    """Index page of the service."""
    hostname = request.base_url.hostname
    if settings.PROXIED:
        hostname = request.headers.get("Host", request.base_url.hostname)
    canonical_hostname = settings.HOSTNAME

    if hostname == canonical_hostname:
        return templates.TemplateResponse(request=request, name="index.html")

    try:
        # TODO use only in debug-mode
        app_id, _, _ = hostname.split(".")
    except Exception:
        logger.debug("Invalid hostname: %s", request.base_url.hostname)
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

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
                "peerjs_secure": True if settings.PEERJS_PORT == 443 else False,
            },
        )

    logger.debug("Invalid hostname: %s", request.base_url.hostname)
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/app.webmanifest")
async def generate_manifest(
    request: Request, services: svcs.fastapi.DepContainer
) -> Response:
    hostname = request.base_url.hostname
    if settings.PROXIED:
        hostname = request.headers.get("Host", request.base_url.hostname)

    if len(hostname.split(".")) != 3:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    if not (app_id := request.headers.get("X-App-Id")):
        # TODO use only in debug-mode
        app_id = hostname.split(".")[0]

    _db = await services.aget(AsyncIOMotorClient)
    app = await _db.apps.find_one({"_id": app_id})
    response = {
        "name": app["name"],
        "short_name": app["name"],
        "description": "Cats app. That's it",
        "icons": [
            {
                "src": f"/static/{app['icon']}",
                # TODO add sizes restrictions and generation
                "sizes": "32x32",
                # TODO add icon type inference
                "type": "image/jpeg",
            },
            {
                "src": f"/static/{app['icon']}",
                # TODO add sizes restrictions and generation
                "sizes": "192x192",
                # TODO add icon type inference
                "type": "image/jpeg",
            },
            {
                "src": f"/static/{app['icon']}",
                # TODO add sizes restrictions and generation
                "sizes": "512x512",
                # TODO add icon type inference
                "type": "image/jpeg",
            },
        ],
        "start_url": f"{request.base_url.scheme}://{hostname}/",
        "display": "standalone",
        "theme_color": "#000000",
        "background_color": "#ffffff",
    }
    return JSONResponse(response)


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
    new_url = f"https://{app_id}.{settings.HOSTNAME}"
    if not settings.PROXIED:
        new_url = f"{new_url}:{settings.PORT}"

    icon_extension = icon.filename.split(".")[-1]
    icon_path = f"icons/{app_id}.{icon_extension}"
    icon_full_path = settings.STATIC_PATH / "icons" / f"{app_id}.{icon_extension}"
    with open(icon_full_path, "wb+") as f:
        shutil.copyfileobj(icon.file, f)

    _db = await services.aget(AsyncIOMotorClient)
    await _db.apps.insert_one(
        {
            "_id": app_id,
            "name": name,
            "preset": preset,
            "icon": icon_path,
        }
    )

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
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    return GetSessionResponse(peer_id=peer_id)


@app.get("/health")
async def health(services: svcs.fastapi.DepContainer) -> JSONResponse:
    ok: list[str] = []
    failing: list[dict[str, str]] = []
    code = status.HTTP_200_OK

    for svc in services.get_pings():
        try:
            await svc.aping()
            ok.append(svc.name)
        except Exception as e:
            failing.append({svc.name: repr(e)})
            code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(content={"ok": ok, "failing": failing}, status_code=code)
