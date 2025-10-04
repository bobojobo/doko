""""""

from sqlalchemy.ext.asyncio import AsyncSession

from doko import request_dto, response_dto, orm, logging
from doko.libs import password_utils


async def state() -> response_dto.Registration:
    return response_dto.Registration()


async def username(
    data: request_dto.RegistrationUsername,
    session: AsyncSession,
) -> response_dto.RegistrationPartialUsername:
    """Usernames are Unique. Check if the chosen username is still available."""

    username_is_available = await orm.User.name_is_available(name=data.username, session=session)
    obj = response_dto.RegistrationPartialUsername(
        first_load=False,
        username=data.username,
        username_is_taken=not username_is_available,
    )
    return obj


async def password(data: request_dto.RegistrationPassword) -> response_dto.RegistrationPartialPassword:
    return response_dto.RegistrationPartialPassword(password=data.password)


async def password_validation(
    data: request_dto.RegistrationPasswordValidation,
) -> response_dto.RegistrationPartialPasswordValidation:
    return response_dto.RegistrationPartialPasswordValidation(
        password=data.password,
        password_validation=data.password_validation,
    )


async def register(data: request_dto.Register, session: AsyncSession) -> response_dto.RegistrationPartialUsername | response_dto.RegistrationPartialPasswordValidation | response_dto.RegistrationPartialSuccess:
    """The submit form-input of the registration page."""

    # todo: add username validation -> regex min length, ...
    # todo: Also prefilling username into the login would be nice
    #       redirect_url = URL("/").include_query_params(username=username)

    # Check if username is available
    username_is_available = await orm.User.name_is_available(name=data.username, session=session)
    if not username_is_available:
        return response_dto.RegistrationPartialUsername(
            first_load=False,
            username=data.username,
            username_is_taken=True,
        )

    # Validate password match
    # todo: these should be on the pydantic model. But test if it indeed works!
    # assert password_utils.is_valid_password(data.password), (
    #    "Password is not valid: \n" + password_utils.password_regex_description
    # )
    if data.password != data.password_validation:
        return response_dto.RegistrationPartialPasswordValidation(
            password=data.password,
            password_validation=data.password_validation,
        )

    hashed_password = password_utils.hash_password(data.password)
    new_user = orm.User(name=data.username, password=hashed_password)
    session.add(new_user)
    await session.commit()
    logging.debug(f"New user created: {new_user.name}")
    obj = response_dto.RegistrationPartialSuccess()
    return obj
