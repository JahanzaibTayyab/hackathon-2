"""Conversation service layer for chat operations."""

from sqlmodel import Session, func, select

from src.models.conversation import Conversation
from src.models.message import Message


class ConversationService:
    """Service for conversation-related operations."""

    def __init__(self, session: Session, user_id: str):
        """
        Initialize conversation service.

        Args:
            session: Database session
            user_id: Current authenticated user ID
        """
        self.session = session
        self.user_id = user_id

    def create_conversation(self) -> Conversation:
        """
        Create a new conversation.

        Returns:
            Created conversation
        """
        conversation = Conversation(user_id=self.user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: int) -> Conversation | None:
        """
        Get conversation by ID for current user.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation if found and belongs to user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == self.user_id,
        )
        return self.session.exec(statement).first()

    def list_conversations(self) -> list[tuple[Conversation, int]]:
        """
        List all conversations for current user with message counts.

        Returns:
            List of tuples containing (conversation, message_count)
        """
        statement = (
            select(Conversation, func.count(Message.id).label("message_count"))
            .outerjoin(Message, Conversation.id == Message.conversation_id)
            .where(Conversation.user_id == self.user_id)
            .group_by(Conversation.id)
            .order_by(Conversation.updated_at.desc())
        )
        results = self.session.exec(statement).all()
        return [(row[0], row[1]) for row in results]

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: str | None = None,
    ) -> Message | None:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role ("user" or "assistant")
            content: Message content
            tool_calls: Optional JSON string of tool calls

        Returns:
            Created message if conversation exists and belongs to user, None otherwise
        """
        conversation = self.get_conversation(conversation_id)
        if conversation is None:
            return None

        message = Message(
            conversation_id=conversation_id,
            user_id=self.user_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
        )
        self.session.add(message)

        # Update conversation timestamp
        conversation.mark_updated()
        self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages(self, conversation_id: int) -> list[Message] | None:
        """
        Get all messages for a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of messages if conversation exists and belongs to user, None otherwise
        """
        conversation = self.get_conversation(conversation_id)
        if conversation is None:
            return None

        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(self.session.exec(statement).all())

    def delete_conversation(self, conversation_id: int) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found or doesn't belong to user
        """
        conversation = self.get_conversation(conversation_id)
        if conversation is None:
            return False

        # Delete all messages first
        delete_messages = select(Message).where(Message.conversation_id == conversation_id)
        messages = self.session.exec(delete_messages).all()
        for message in messages:
            self.session.delete(message)

        # Delete conversation
        self.session.delete(conversation)
        self.session.commit()
        return True
