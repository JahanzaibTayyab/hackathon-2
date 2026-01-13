"""Chat API endpoints for AI-powered task management."""

from fastapi import APIRouter, HTTPException

from src.core.database import SessionDep
from src.core.dependencies import CurrentUserDep
from src.schemas.chat import ChatRequest, ChatResponse
from src.schemas.conversation import ConversationListResponse, ConversationResponse, ConversationSummary, MessageResponse
from src.services.chat_service import ChatService
from src.services.conversation_service import ConversationService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    session: SessionDep,
    user_id: CurrentUserDep,
):
    """
    Send a message to the AI assistant and get a response.

    Args:
        request: Chat request with message and optional conversation_id
        session: Database session
        user_id: Authenticated user ID from JWT token

    Returns:
        ChatResponse with conversation_id, response, and tool_calls
    """
    chat_service = ChatService(session=session, user_id=user_id)

    try:
        response = await chat_service.process_message(
            message=request.message, conversation_id=request.conversation_id
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    session: SessionDep,
    user_id: CurrentUserDep,
):
    """
    List all conversations for the authenticated user.

    Args:
        session: Database session
        user_id: Authenticated user ID from JWT token

    Returns:
        ConversationListResponse with list of conversations
    """
    conversation_service = ConversationService(session=session, user_id=user_id)
    conversations_with_counts = conversation_service.list_conversations()

    summaries = [
        ConversationSummary(
            id=conv.id if conv.id is not None else 0,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=count,
        )
        for conv, count in conversations_with_counts
    ]

    return ConversationListResponse(conversations=summaries)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    session: SessionDep,
    user_id: CurrentUserDep,
):
    """
    Get a specific conversation with all messages.

    Args:
        conversation_id: Conversation ID
        session: Database session
        user_id: Authenticated user ID from JWT token

    Returns:
        ConversationResponse with conversation details and messages
    """
    conversation_service = ConversationService(session=session, user_id=user_id)

    conversation = conversation_service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = conversation_service.get_messages(conversation_id)
    if messages is None:
        messages = []

    message_responses = [
        MessageResponse(
            id=msg.id if msg.id is not None else 0,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
        )
        for msg in messages
    ]

    return ConversationResponse(
        id=conversation.id if conversation.id is not None else 0,
        user_id=conversation.user_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=message_responses,
    )


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    session: SessionDep,
    user_id: CurrentUserDep,
):
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: Conversation ID
        session: Database session
        user_id: Authenticated user ID from JWT token

    Returns:
        204 No Content on success
    """
    conversation_service = ConversationService(session=session, user_id=user_id)

    success = conversation_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return None
