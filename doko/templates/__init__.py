"""Loading the jinja templates."""

from functools import cache
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from doko import response_dto


template_directory: Path = Path(__file__).parent


@cache
def jinja_templates() -> Jinja2Templates:
    """lazyloading jinja templates"""
    return Jinja2Templates(directory=template_directory)


def render(path: Path, context: response_dto.ResponseDto, request: Request, **kwargs) -> HTMLResponse:
    """Function to render the templates with the given data."""
    full_path = Path.joinpath(template_directory, path)
    assert full_path.exists(), f"Path {full_path} doesn't exist"
    assert isinstance(context, response_dto.ResponseDto)

    template = jinja_templates().TemplateResponse(
        name=path.as_posix(),
        context=context.model_dump() | dict(request=request),
        **kwargs,
    )
    return template
