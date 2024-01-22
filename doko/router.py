"""
The routing of the application. These are very minimal and serve only for tying everything together. The bulk of the 
logic is in the logic module. 

A request_dto goes in, gets transformed into a response_dto and finally into a template that goes back out. 
┌─────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│             │                                                                                                        │
│             │            ┌───────────────┐   ┌─────┐   ┌────────────────┐             ┌──────────┐                   │
│ data models │            │  request_dto  │   │ orm │   │  response_dto  │             │ template │                   │
│             │            └───────────────┘   └─────┘   └────────────────┘             └──────────┘                   │
│             │            ▲               │     ▲ │     ▲                │             ▲          │                   │
├─────────────┤            │               │     │ │     │                │             │          │                   │
│             │            │               ▼     │ ▼     │                ▼             │          ▼                   │
│             │  ┌──────────┐              ┌─────────────┐                ┌─────────────┐          ┌─────────┐         │
│ processes   │  │ browser  │              │    logic    │                │ templating  │          │ browser │         │
│             │  └──────────┘              └─────────────┘                └─────────────┘          └─────────┘         │
│             │                                                                                                        │
└─────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────┘


SSM works slightly different. Browser sets up SSM connections, conection stays open and listenes to new events. 
In the backeend event listeners are hooked into Database events. DB-events get broadcasted to the respective listeners 
that the ssm connection is awaiting. Sometimes a filled in template gets send back to the client, sometimes only the event
other dom elements in the browser then listen to these events and react with direct dom changes or with a new get reuest 
to update the dom with the html coming for there. 


"""
from fastapi import APIRouter
from typing import AsyncGenerator

from fastapi import (
    Cookie,
    Depends,
    Request,
    Response,
    HTTPException,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
import asyncio

from pathlib import Path

from doko import (request_dto, response_dto, db, sse, logic, exception, logging,)
from doko.templates import render


router = APIRouter()


@router.get("/", response_model=None)
async def index_get() -> HTMLResponse | RedirectResponse:
    """Landing/ index page: Forwarding to the login."""

    return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)


@router.get("/login/", response_model=None)
async def login_get(
    request: Request,
    session: db.AsyncSession = Depends(db.session),
    session_token: str | None = Cookie(default=None),
) -> HTMLResponse | RedirectResponse:
    """login page for users."""

    try:
        context = await logic.login.state(session_token=session_token, session=session)
    except exception.AlreadyAuthenticated:
        return RedirectResponse("/group/", status_code=status.HTTP_302_FOUND)
    return render(path=Path("login/login.html"), context=context, request=request)


@router.post("/login/", response_model=None)
async def login_post(
    request: Request,
    data: request_dto.Login = Depends(),
    session: db.AsyncSession = Depends(db.session),
) -> HTMLResponse | RedirectResponse:
    """Submit a login. Success forwards to /group/"""

    context = await logic.login.login(data=data, session=session)
    if isinstance(context, response_dto.Login):
        return render(path=Path("login/login.html"), context=context, request=request)
    else:
        cookie = context
    response = RedirectResponse("/group/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(**dict(cookie))
    return response


@router.get("/logout/")
async def logout_get(
    response: Response,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> RedirectResponse:
    """
    Submit a logout: Expire the session and remove the cookie from the client side. Then redirect the client to the index.
    """

    await logic.logout.logout(session_token=session_token, session=session)
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_token")
    return response


@router.get("/registration/", response_class=HTMLResponse)
async def registration_get(request: Request) -> HTMLResponse:
    """Registration page. This is where new users can create an account."""

    context = await logic.registration.state()
    return render(path=Path("registration/registration.html"), context=context, request=request)


@router.post("/registration/username/", response_class=HTMLResponse)
async def registration_username_post(
    request: Request,
    data: request_dto.RegistrationUsername = Depends(),
    session: db.AsyncSession = Depends(db.session),
) -> HTMLResponse:
    """The username form input of the registration page"""

    context = await logic.registration.username(data=data, session=session)
    return render(path=Path("registration/partials/username.html"), context=context, request=request)


@router.post("/registration/password/", response_class=HTMLResponse)
async def registration_password_post(
    request: Request,
    data: request_dto.RegistrationPassword = Depends(),
) -> HTMLResponse:
    """The password form input of the registration page"""

    context = await logic.registration.password(data=data)
    return render(path=Path("registration/partials/password.html"), context=context, request=request)


@router.post("/registration/password_validation/", response_class=HTMLResponse)
async def registration_password_validation_post(
    request: Request,
    data: request_dto.RegistrationPasswordValidation = Depends(),
) -> HTMLResponse:
    """The password-validation form input of the registration page"""

    context = await logic.registration.password_validation(data=data)
    return render(path=Path("registration/partials/password_validation.html"), context=context, request=request)


@router.post("/registration/", response_class=HTMLResponse)
async def registration_post(
    request: Request,
    data: request_dto.Register = Depends(),
    session: db.AsyncSession = Depends(db.session),
) -> HTMLResponse:
    """The submit form input of the registration page. Creates a new user."""

    context = await logic.registration.register(data=data, session=session)
    return render(path=Path("registration/partials/success.html"), context=context, request=request)


@router.get("/group/", response_class=HTMLResponse)
async def group_get(
    request: Request,
    data: request_dto.Group = Depends(),
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> HTMLResponse:
    """
    The group screen contains an overview of the groups of a player. The player has the option to create a new group.
    The player can also join a new sitting with one of the groups.
    """

    context = await logic.group_selection.state(data=data, session=session, session_token=session_token)
    return render(path=Path("group/group.html"), context=context, request=request)


@router.get("/group/players/", response_class=HTMLResponse)
async def group_players_get(
    request: Request,
    data: request_dto.GroupPlayers = Depends(),
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> HTMLResponse:
    """The players partial of a group."""

    context = await logic.group_selection.players(data=data, session=session, session_token=session_token)
    return render(path=Path("group/partials/players.html"), context=context, request=request)


@router.get("/group/sse/", response_class=EventSourceResponse)
async def group_sse_updates_get(
    request: Request,
    session_token: str = Cookie(),
    session: db.AsyncSession = Depends(db.session),
) -> EventSourceResponse:
    """This partial is pusing server sent events (SSE) of new groups that are created to the group screen."""

    async def event_stream() -> AsyncGenerator[ServerSentEvent, None]:
        """Return the html directly instead of the event + get pattern."""
        try:
            async for event in sse.EventLoop(session_token, sse.Event.group_created):
                context = await logic.group_selection.groups(
                    session=session,
                    session_token=session_token,
                )
                template = render(path=Path("group/partials/groups.html"), context=context, request=request)
                yield ServerSentEvent(
                    event=event.value,
                    data=template.body.decode("utf-8"),
                )
                logging.debug(f"{session_token}: waiting for events")

        except asyncio.CancelledError as e:
            logging.debug("SSE disconnection")
            raise asyncio.CancelledError() from e

    return EventSourceResponse(event_stream(), ping=60)


@router.get("/group/create/", response_class=HTMLResponse)
async def group_create_get(
    request: Request,
    data: request_dto.GroupCreate = Depends(),
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> HTMLResponse:
    """The group create screen. Lets a user create a new group of players."""

    context = await logic.group_creation.state(data=data, session=session, session_token=session_token)
    return render(path=Path("group_create/group_create.html"), context=context, request=request)


@router.post("/group/create/groupname/", response_class=HTMLResponse)
async def group_create_groupname_post(
    request: Request,
    data: request_dto.GroupCreateGroupname = Depends(),
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> HTMLResponse:
    """The groupname partial is a form validation for the groupname. Group names needs to be unique."""

    context = await logic.group_creation.groupname(data=data, session=session, session_token=session_token)
    return render(path=Path("group_create/partials/groupname.html"), context=context, request=request)


@router.post("/group/create/username/", response_class=HTMLResponse)
async def group_create_username_post(
    request: Request,
    data: request_dto.GroupCreateUsername = Depends(),
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> HTMLResponse:
    """Validation of usernames on the group creation form input."""

    context = await logic.group_creation.playername(data=data, session=session, session_token=session_token)
    return render(path=Path("group_create/partials/username.html"), context=context, request=request)


@router.post("/group/create/", response_class=RedirectResponse)
async def group_create_post(
    data: request_dto.GroupCreate = Depends(),
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> RedirectResponse:
    """
    Call for the creation button on the group screen. Does a serverside validation of the form data for 
    the new group. If all is good: and creates the group and redirects back to group.
    """
    
    await logic.group_creation.create(data=data, session=session, session_token=session_token)
    return RedirectResponse("/group/", status_code=status.HTTP_302_FOUND)


# todo @router.get("/waiting/{groupname}/")
@router.get("/waiting/")
async def waiting_get(
    request: Request,
    data: request_dto.Waiting = Depends(),
    # groupname: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> HTMLResponse:
    """Waiting screen once a user clicks ready on the /group/ screen."""
   
    # data = request_dto.Waiting(groupname=groupname)
    await logic.group_waiting.waiting_for_group(data=data, session=session, session_token=session_token)
    context = await logic.group_waiting.state(data=data, session=session, session_token=session_token)
    return render(path=Path("waiting/waiting.html"), context=context, request=request)


@router.get("/waiting/{groupname}/sse/", response_class=EventSourceResponse)
async def waiting_sse_get(
    request: Request,
    groupname: str,
    session_token: str = Cookie(),
    session: db.AsyncSession = Depends(db.session),
) -> EventSourceResponse:
    """
    Pushing server sent events (SSE) of player status updates to the waiting screen.
    When a player of the group comes online or goes offline it gets automatically updated by this call.
    """

    data = request_dto.Waiting(groupname=groupname)

    async def event_stream() -> AsyncGenerator[ServerSentEvent, None]:
        """Return the html directly instead of the event + get pattern."""
        try:
            async for event in sse.EventLoop(session_token, [sse.Event.player_status_update]): # , sse.Event.game_created
                context = await logic.group_waiting.update(
                    data=data,
                    session=session,
                    session_token=session_token,
                )
                template = render(path=Path("waiting/partials/update.html"), context=context, request=request)
                yield ServerSentEvent(
                    event=event.value,
                    data=template.body.decode("utf-8"),
                )
                logging.debug(f"{session_token}: waiting for events")

        except asyncio.CancelledError as e:
            logging.debug("SSE disconnection")
            sse.add_task(logic.group_waiting.cleanup(data=data, session_token=session_token))
            raise asyncio.CancelledError() from e

    return EventSourceResponse(event_stream(), ping=60)


@router.get("/game/{id}/", response_class=HTMLResponse)
async def game_get(
    request: Request,
    id: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> HTMLResponse:
    """Full game state"""

    context = await logic.game.state(session=session, session_token=session_token, game_id=id)
    return render(path=Path("game/game.html"), context=context, request=request)


@router.get("/game/{id}/sse/", response_class=HTMLResponse)
async def game_sse_get(
    session_token: str = Cookie(),
) -> HTMLResponse:
    """Server sent events (SSE) for game changes."""

    async def event_stream() -> AsyncGenerator[ServerSentEvent, None]:
        """event + get pattern."""
        try:
            async for event in sse.EventLoop(session_token, [sse.Event.card_played, sse.Event.turn_changed, sse.Event.game_closed]):
                yield ServerSentEvent(event=event.value, data="")
        except asyncio.CancelledError as e:
            logging.debug("SSE disconnection")
            raise asyncio.CancelledError() from e

    return EventSourceResponse(event_stream(), ping=60)


@router.post("/game/{id}/card/", response_class=HTMLResponse)
async def game_card_post(
    id: str,
    data: request_dto.GameHandcard = Depends(),
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> None:
    """Player played a card."""

    await logic.game.play_card(session=session, session_token=session_token, data=data, game_id=id)


@router.get("/game/{id}/stack/", response_class=HTMLResponse)
async def game_stack_get(
    request: Request,
    id: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> None:
    context: response_dto.Stack = await logic.game.stack(session=session, session_token=session_token, game_id=id)
    return render(path=Path("game/partials/stack.html"), context=context, request=request)


@router.get("/game/{id}/hand/", response_class=HTMLResponse)
async def game_hand_get(
    request: Request,
    id: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> HTMLResponse:
    context: response_dto.Hand = await logic.game.hand(session=session, session_token=session_token, game_id=id)
    return render(path=Path("game/partials/hand.html"), context=context, request=request)


@router.get("/game_review/{id}/", response_class=HTMLResponse)
async def game_review_get(
    request: Request,
    id: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> HTMLResponse:
    """Review of the last game, forwarding button to the next game"""

    context = await logic.game_review.state(session=session, session_token=session_token, game_id=id)
    return render(path=Path("game_review/game_review.html"), context=context, request=request)


@router.get("/game_review/{id}/sse/", response_class=EventSourceResponse)
async def game_review_sse_get(
    request: Request,
    id: str,
    session_token: str = Cookie(),
    session: db.AsyncSession = Depends(db.session),
) -> EventSourceResponse:
    """
    Pushing server sent events (SSE) of player status updates to the waiting screen.
    When a player of the group comes online or goes offline it gets automatically updated by this call.
    """

    async def event_stream() -> AsyncGenerator[ServerSentEvent, None]:
        """Return the html directly instead of the event + get pattern."""
        try:
            async for event in sse.EventLoop(session_token, [sse.Event.player_status_update]): # , sse.Event.game_created
                context = await logic.game_review.update( # todo: use a smaller thing: update. Like in group_waiting 
                    session=session,
                    session_token=session_token,
                    game_id=id
                )
                template = render(path=Path("game_review/partials/update.html"), context=context, request=request)
                yield ServerSentEvent(
                    event=event.value,
                    data=template.body.decode("utf-8"),
                )
                logging.debug(f"{session_token}: waiting for events")

        except asyncio.CancelledError as e:
            logging.debug("SSE disconnection")
            #sse.add_task(logic.game_review.cleanup(data=data, session_token=session_token))
            raise asyncio.CancelledError() from e

    return EventSourceResponse(event_stream(), ping=60)


@router.post("/game_review/", response_class=HTMLResponse)
async def game_review_post(
    request: Request,
    data: request_dto.GameReviewReady = Depends(),
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> None:
    """Player is ready for the next game"""

    await logic.game_review.ready(data=data, session=session, session_token=session_token)



@router.get("/{_:path}")
async def catch_all_get(request: Request) -> None:
    """Wildcard of all nonexisting routes, raises 404."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Whatebaaaa")
