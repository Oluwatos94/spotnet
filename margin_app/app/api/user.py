"""
API for handling user endpoints
"""

from app.crud.deposit import deposit_crud
from app.crud.user import UserCRUD
from app.db.sessions import get_db
from app.schemas.user import (AddMarginPositionRequest,
                              AddMarginPositionResponse, AddUserDepositRequest,
                              AddUserDepositResponse)
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/add_user_deposit",
    status_code=status.HTTP_201_CREATED,
    response_model=AddUserDepositResponse,
)
async def add_user_deposit(user_deposit: AddUserDepositRequest):
    """
    Add an user deposit

    :param user_deposit: user id, amount, token, transaction_id
    :return: deposit id
    """
    try:
        deposit = await deposit_crud.create_deposit(
            user_id=user_deposit.user_id,
            token=user_deposit.token,
            amount=user_deposit.amount,
            transaction_id=user_deposit.transaction_id,
        )
        return AddUserDepositResponse(deposit_id=deposit.id)
    except Exception as e:
        logger.error(f"Error adding user deposit: {e}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/add_margin_position", response_model=AddMarginPositionResponse)
async def add_margin_position(
    request: AddMarginPositionRequest,
):
    """
    Adds a margin position for a user.

    This endpoint allows users to open a margin position by borrowing a specified
    amount with a given multiplier. A valid transaction ID is required.

    Parameters:
    - request (AddMarginPositionRequest): The request payload containing:
        - user_id (UUID): The ID of the user opening the margin position.
        - borrowed_amount (Decimal): The amount borrowed in the margin trade.
        - multiplier (int): The leverage multiplier.
        - token (str): The asset token for the margin position.
        - transaction_id (str): The associated transaction ID.

    Returns:
    - AddMarginPositionResponse: A response containing the created margin position ID.

    Raises:
    - HTTPException (400): If the user does not exist or any validation fails.
    """
    user_crud = UserCRUD()

    try:
        margin_position = await user_crud.add_margin_position(
            user_id=request.user_id,
            borrowed_amount=request.borrowed_amount,
            multiplier=request.multiplier,
            transaction_id=request.transaction_id,
        )
        return {"margin_position_id": margin_position.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
