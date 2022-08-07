from typing import Optional
from pydantic import BaseModel, HttpUrl
from pydantic.class_validators import validator

import re

valid_shorts = re.compile(r"^[\w\-_]+$")


class LinkRequest(BaseModel):
    url: HttpUrl
    short: Optional[str]

    @validator("short")
    def validate_short(cls, v: Optional[str]):
        if v is not None and not valid_shorts.fullmatch(v):
            raise ValueError(f"must match pattern {valid_shorts.pattern}")

        return v


class Link(LinkRequest):
    short: str
    is_auto_generated: bool


class LinkResponse(BaseModel):
    short: str
