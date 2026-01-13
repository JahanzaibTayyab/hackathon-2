"""Chat service layer for AI agent interactions."""

import json

from agents import RunConfig, Runner
from sqlmodel import Session

from src.agent.agent import create_chat_agent
from src.agent.model_provider import openai_provider
from src.models.conversation import Conversation
from src.schemas.chat import ChatResponse, ToolCall
from src.services.conversation_service import ConversationService


class ChatService:
    """Service for chat-related operations with AI agent."""

    def __init__(self, session: Session, user_id: str):
        """
        Initialize chat service.

        Args:
            session: Database session
            user_id: Current authenticated user ID
        """
        self.session = session
        self.user_id = user_id
        self.conversation_service = ConversationService(session=session, user_id=user_id)

    async def process_message(
        self, message: str, conversation_id: int | None = None
    ) -> ChatResponse:
        """
        Process a user message and get AI response.

        Args:
            message: User's message
            conversation_id: Optional existing conversation ID

        Returns:
            ChatResponse with conversation_id, response, and tool_calls
        """
        # Get or create conversation
        conversation: Conversation
        if conversation_id is not None:
            existing_conv = self.conversation_service.get_conversation(conversation_id)
            if existing_conv is None:
                # Create new conversation if provided ID is invalid
                conversation = self.conversation_service.create_conversation()
            else:
                conversation = existing_conv
        else:
            conversation = self.conversation_service.create_conversation()

        # Ensure conversation has an ID
        if conversation.id is None:
            raise ValueError("Conversation ID is None after creation")

        conv_id = conversation.id

        # Store user message
        user_message = self.conversation_service.add_message(
            conversation_id=conv_id, role="user", content=message
        )
        if user_message is None:
            raise ValueError("Failed to store user message")

        # Build conversation history for agent
        messages = self.conversation_service.get_messages(conv_id)
        if messages is None:
            messages = []

        # Convert to OpenAI Agents SDK format (exclude the just-added user message,
        # we'll add it separately)
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.id != user_message.id  # Exclude the current message
        ]

        # Append the current user message
        history.append({"role": "user", "content": message})

        # Create agent for this user
        agent = create_chat_agent(user_id=self.user_id)

        # Run agent with conversation history using OpenAI model provider
        result = await Runner.run(
            starting_agent=agent,
            input=history,
            run_config=RunConfig(model_provider=openai_provider),
        )

        # Extract response and tool calls
        response_text = result.final_output or ""
        tool_calls_list: list[ToolCall] = []

        # Extract tool calls from result if available
        if hasattr(result, "items") and result.items:
            for item in result.items:
                # Check if item is a tool call
                if hasattr(item, "type") and item.type == "function_call":
                    tool_call_data = ToolCall(
                        tool_name=getattr(item, "name", "unknown"),
                        arguments=getattr(item, "arguments", {}),
                        result=getattr(item, "output", None),
                    )
                    tool_calls_list.append(tool_call_data)

        # Store assistant message
        tool_calls_json = json.dumps([tc.model_dump() for tc in tool_calls_list]) if tool_calls_list else None
        assistant_message = self.conversation_service.add_message(
            conversation_id=conv_id,
            role="assistant",
            content=response_text,
            tool_calls=tool_calls_json,
        )
        if assistant_message is None:
            raise ValueError("Failed to store assistant message")

        return ChatResponse(
            conversation_id=conv_id, response=response_text, tool_calls=tool_calls_list
        )
