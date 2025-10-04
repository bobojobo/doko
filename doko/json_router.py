"""
REST JSON API for the Doko application.

This module provides a proper RESTful API with resource-based endpoints.
All endpoints return JSON responses and follow REST conventions.

Authentication is handled via session_token cookies.
"""

from fastapi import APIRouter
from fastapi import (
    Cookie,
    Depends,
    Request,
    HTTPException,
)
from fastapi.responses import JSONResponse
from starlette import status

from doko import (request_dto, response_dto, db, logic, exception, json_request_dto)


# JSON API router
json_router = APIRouter(prefix="/json")


@json_router.get("/")
async def api_root() -> JSONResponse:
    """API root endpoint with basic info."""
    return JSONResponse({
        "name": "Doko REST API",
        "version": "1.0",
        "description": "RESTful API for Doppelkopf card game"
    })


# Authentication endpoints
@json_router.post("/auth/login")
async def login(
    data: json_request_dto.JsonLogin,
    session: db.AsyncSession = Depends(db.session),
) -> JSONResponse:
    """Authenticate user and return session token."""
    form_data = request_dto.Login(username=data.username, password=data.password)
    context = await logic.login.login(data=form_data, session=session)
    if isinstance(context, response_dto.Login):
        return JSONResponse({"error": "Invalid credentials"}, status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        cookie_data = context
        return JSONResponse({
            "success": True,
            "user": data.username,
            "set_cookie": dict(cookie_data)
        })


@json_router.post("/auth/logout")
async def logout(
    session: db.AsyncSession = Depends(db.session),
    session_token: str | None = Cookie(default=None),
) -> JSONResponse:
    """Logout user and clear session."""
    if session_token:
        await logic.logout.logout(session_token=session_token, session=session)
    return JSONResponse({
        "success": True,
        "delete_cookie": "session_token"
    })


# User endpoints
@json_router.post("/users")
async def create_user(
    data: json_request_dto.JsonRegister,
    session: db.AsyncSession = Depends(db.session),
) -> JSONResponse:
    """Register a new user."""
    form_data = request_dto.Register(
        username=data.username,
        password=data.password,
        password_validation=data.password_validation
    )
    context = await logic.registration.register(data=form_data, session=session)
    
    # Check if username is taken
    if hasattr(context, 'username_is_taken') and context.username_is_taken:
        return JSONResponse({"error": "Username already taken"}, status_code=status.HTTP_409_CONFLICT)
    
    # Check if passwords match
    if hasattr(context, 'password_matches') and not context.password_matches:
        return JSONResponse({"error": "Passwords do not match"}, status_code=status.HTTP_400_BAD_REQUEST)
    
    return JSONResponse({"success": True, "username": data.username}, status_code=status.HTTP_201_CREATED)


# Group endpoints
@json_router.get("/groups")
async def list_groups(
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Get list of user's groups."""
    form_data = request_dto.Group(groupname="")
    context = await logic.group_selection.state(data=form_data, session=session, session_token=session_token)
    return JSONResponse({
        "groups": [{"name": name} for name in context.groupnames],
        "user": context.username
    })


@json_router.post("/groups")
async def create_group(
    data: json_request_dto.JsonGroupCreate,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Create a new group."""
    form_data = request_dto.GroupCreate(
        groupname=data.groupname,
        username_0=data.username_0,
        username_1=data.username_1,
        username_2=data.username_2
    )
    try:
        await logic.group_creation.create(data=form_data, session=session, session_token=session_token)
        return JSONResponse({"success": True, "group_name": data.groupname}, status_code=status.HTTP_201_CREATED)
    except AssertionError as e:
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
    except LookupError:
        return JSONResponse({"error": "User not found"}, status_code=status.HTTP_404_NOT_FOUND)


@json_router.get("/groups/{group_name}")
async def get_group(
    group_name: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Get group details including players."""
    form_data = request_dto.Group(groupname=group_name)
    context = await logic.group_selection.state(data=form_data, session=session, session_token=session_token)
    return JSONResponse({
        "name": group_name,
        "players": context.playernames,
        "user": context.username
    })


# Game endpoints
@json_router.get("/games")
async def list_games(
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Get list of user's games (active and completed)."""
    # This would need new logic to list games - not currently implemented
    # For now, return placeholder
    return JSONResponse({"games": [], "message": "Game listing not yet implemented"})


@json_router.post("/games")
async def create_game(
    data: json_request_dto.JsonWaiting,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Create/start a new game for a group."""
    # Check if all players are ready
    from doko import orm
    user = await orm.User.from_session_token(session=session, session_token=session_token)
    group = await orm.Group.from_name(session, name=data.groupname)
    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
    
    # First check if a game already exists (e.g., created via mark_ready endpoint)
    if await group.has_active_sitting(session=session):
        active_sitting = await group.get_active_sitting(session=session)
        if await active_sitting.has_active_game(session=session):
            # Game already exists, just return it
            game = await active_sitting.get_active_game(session=session)
            # Ensure player has correct status
            if player.status != "waiting_for_turn":
                await player.set_status(session=session, status="waiting_for_turn")
            return JSONResponse({
                "success": True,
                "game_id": str(game.id),
                "group_name": data.groupname
            }, status_code=status.HTTP_200_OK)
    
    # No active game, proceed with normal waiting flow
    form_data = request_dto.Waiting(groupname=data.groupname)
    await logic.group_waiting.waiting_for_group(data=form_data, session=session, session_token=session_token)
    
    all_ready = await group.all_players_are_waiting()
    
    if all_ready:
        # Check if game already exists
        if await group.has_active_sitting(session=session):
            active_sitting = await group.get_active_sitting(session=session)
            if await active_sitting.has_active_game(session=session):
                # Game already created by another player
                game = await active_sitting.get_active_game(session=session)
                player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
                await player.set_status(session=session, status="waiting_for_turn")
                return JSONResponse({
                    "success": True,
                    "game_id": str(game.id),
                    "group_name": data.groupname
                }, status_code=status.HTTP_201_CREATED)
        
        # No game exists yet, create one (leader only, but we'll let anyone create to avoid coordination issues)
        leader = await group.leader()
        if user.id == leader.id:
            # Create the game
            if not await group.has_active_sitting(session=session):
                active_sitting = await group.create_sitting(session=session)
                game = await active_sitting.create_game(session=session)
                await group.deal_cards(session=session)
                await game.create_active_trick(session=session)
                player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
                await player.set_status(session=session, status="waiting_for_turn")
                return JSONResponse({
                    "success": True,
                    "game_id": str(game.id),
                    "group_name": data.groupname
                }, status_code=status.HTTP_201_CREATED)
        else:
            # Not the leader, check again if game was created in the meantime
            if await group.has_active_sitting(session=session):
                active_sitting = await group.get_active_sitting(session=session)
                if await active_sitting.has_active_game(session=session):
                    game = await active_sitting.get_active_game(session=session)
                    player = await orm.Player.from_user_and_group(group=group, user=user, session=session)
                    await player.set_status(session=session, status="waiting_for_turn")
                    return JSONResponse({
                        "success": True,
                        "game_id": str(game.id),
                        "group_name": data.groupname
                    }, status_code=status.HTTP_201_CREATED)
    
    # Not all ready yet or game not created yet
    context = await logic.group_waiting.state(data=form_data, session=session, session_token=session_token)
    return JSONResponse({
        "success": False,
        "message": "Waiting for other players or game creation",
        "players": [{"name": p.name, "status": p.status} for p in context.players]
    })


@json_router.get("/games/{game_id}")
async def get_game(
    game_id: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Get current game state."""
    context = await logic.game.state(session=session, session_token=session_token, game_id=game_id)
    return JSONResponse({
        "game_id": context.game_id,
        "user": context.username,
        "players": [context.player1, context.player2, context.player3],
        "hand": [{"suit": card.suit, "rank": card.rank, "id": card.id, "playable": card.is_playable} 
                for card in context.hand.cards],
        "stack": [{"suit": card.suit, "rank": card.rank, "id": card.id} 
                 for card in context.stack.cards]
    })


@json_router.post("/games/{game_id}/cards")
async def play_card(
    game_id: str,
    data: json_request_dto.JsonGameHandcard,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Play a card in the game."""
    form_data = request_dto.GameHandcard(suit=data.suit, rank=data.rank)
    try:
        await logic.game.play_card(session=session, session_token=session_token, data=form_data, game_id=game_id)
        return JSONResponse({"success": True})
    except AssertionError as e:
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
    except LookupError as e:
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Log but don't fail on SSE-related errors
        import logging
        logging.error(f"Error in play_card: {e}", exc_info=True)
        # Still return success if the card was played (db commit happened before SSE errors)
        return JSONResponse({"success": True, "warning": "Card played but notifications may have failed"})


@json_router.get("/games/{game_id}/hand")
async def get_hand(
    game_id: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Get player's current hand."""
    context = await logic.game.hand(session=session, session_token=session_token, game_id=game_id)
    return JSONResponse({
        "cards": [{"suit": card.suit, "rank": card.rank, "id": card.id, "playable": card.is_playable} 
                 for card in context.hand.cards]
    })


@json_router.get("/games/{game_id}/stack")
async def get_stack(
    game_id: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Get current trick/stack."""
    context = await logic.game.stack(session=session, session_token=session_token, game_id=game_id)
    return JSONResponse({
        "cards": [{"suit": card.suit, "rank": card.rank, "id": card.id} 
                 for card in context.stack.cards],
        "is_full": context.stack.is_full,
        "card_count": context.stack.n_cards
    })


@json_router.post("/games/{game_id}/hand/order")
async def update_hand_order(
    game_id: str,
    data: json_request_dto.JsonGameHandOrder,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Update the order of cards in player's hand."""
    form_data = request_dto.GameHandOrder(card_ids=data.card_ids)
    await logic.game.update_hand_order(session=session, session_token=session_token, data=form_data, game_id=game_id)
    return JSONResponse({"success": True})


# Game Review endpoints
@json_router.get("/game-reviews/{game_id}")
async def get_game_review(
    game_id: str,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Get game review/results."""
    context = await logic.game_review.state(session=session, session_token=session_token, game_id=game_id)
    return JSONResponse({
        "game_id": context.gameid,
        "game_number": context.gamenumber,
        "sitting_number": context.sittingnumber,
        "user": context.username,
        "group_name": context.groupname,
        "player_cards": [{"name": pc.name, "cards": [{"suit": c.suit, "rank": c.rank} for c in pc.cards]} 
                       for pc in context.players_cards],
        "player_status": [{"name": ps.name, "status": ps.status} for ps in context.players_status],
        "all_ready": context.all_ready,
        "new_game_id": context.new_gameid if context.new_gameid else None
    })


@json_router.post("/game-reviews/ready")
async def mark_ready_for_next_game(
    data: json_request_dto.JsonGameReviewReady,
    session: db.AsyncSession = Depends(db.session),
    session_token: str = Cookie(),
) -> JSONResponse:
    """Mark player as ready for next game."""
    form_data = request_dto.GameReviewReady(status=data.status, groupname=data.groupname)
    await logic.game_review.ready(data=form_data, session=session, session_token=session_token)
    return JSONResponse({"success": True})


@json_router.get("/{path:path}")
async def catch_all(request: Request) -> JSONResponse:
    """Catch-all for undefined API routes."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API endpoint not found")