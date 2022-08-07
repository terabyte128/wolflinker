from typing import List
from uuid import uuid4

from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic.tools import parse_obj_as
from tinydb import Query, TinyDB

from wolflinker import models
from wolflinker.config import Settings

db = TinyDB("./db.json")
query = Query()
app = FastAPI()

security = HTTPBasic()
settings = Settings()


@app.on_event("shutdown")
def on_shutdown():
    db.close()


@app.post("/links", status_code=201, response_model=models.LinkResponse)
def create_link(
    link_request: models.LinkRequest,
    creds: HTTPBasicCredentials = Depends(security),
):
    if (
        creds.username != settings.auth_username
        or creds.password != settings.auth_password
    ):
        raise HTTPException(status_code=401)

    if link_request.short is not None:
        dup = db.search(query.short == link_request.short)

        if len(dup) > 0:
            raise HTTPException(
                status_code=409, detail="short name already exists"
            )

        link = models.Link(**link_request.dict(), is_auto_generated=False)

    else:
        link = models.Link(
            **link_request.dict()
            | {"short": uuid4().hex[:8], "is_auto_generated": True}
        )

    db.insert(link.dict())
    return models.LinkResponse(short=link.short)


@app.get("/{short:str}")
def get_link(short: str, do_redirect: bool = True):
    link = parse_obj_as(List[models.Link], db.search(query.short == short))

    if len(link) == 0:
        raise HTTPException(status_code=404, detail="Link not found")
    elif len(link) > 1:
        raise HTTPException(status_code=500)

    if do_redirect:
        return RedirectResponse(url=link[0].url)
    else:
        return link
