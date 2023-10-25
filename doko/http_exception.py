from typing import Callable

from pathlib import Path
from functools import partial

from starlette import status
from starlette.templating import _TemplateResponse
from fastapi import Request, HTTPException

from doko import response_dto
from doko.templates import render


def exception_template(request: Request, exc: HTTPException, _code: int, _description: str) -> _TemplateResponse:
    """Error Template callable, code and description get prefilled"""
    reason = getattr(exc, "detail", "Unknown") if getattr(exc, "detail", "Unknown") != [] else "Unknown"
    context = response_dto.Error(
        reason=reason,
        status_code=_code,
        status_code_description=_description,
    )
    return render(path=Path("error/error.html"), context=context, request=request, status_code=_code)


exception_handlers: dict[int, Callable] = {}


for full_name in status.__all__:
    protocol, code, description = full_name.split("_", maxsplit=2)
    int_code = int(code)
    if 400 <= int_code < 600:
        exception_handlers[int_code] = partial(exception_template, _code=int_code, _description=description)
