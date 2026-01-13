# Implementation Plan: Phase 3 - Todo AI Chatbot

**Date**: 2026-01-13
**Feature**: Phase 3 AI-Powered Todo Chatbot

## Architecture Overview

```
┌─────────────────┐ ┌──────────────────────────────────────────────┐ ┌─────────────────┐
│                 │ │                FastAPI Server                │ │                 │
│                 │ │ ┌────────────────────────────────────────┐   │ │                 │
│   ChatKit UI    │───▶│         Chat Endpoint                  │   │ │    Neon DB      │
│   (Frontend)    │ │ │         POST /api/v1/chat              │   │ │  (PostgreSQL)   │
│                 │ │ └───────────────┬────────────────────────┘   │ │                 │
│                 │ │                 │                             │ │ - tasks         │
│                 │ │                 ▼                             │ │ - conversations │
│                 │ │ ┌────────────────────────────────────────┐   │ │ - messages      │
│                 │◀───│       OpenAI Agents SDK                │   │ │                 │
│                 │ │ │       (Agent + Runner)                 │   │ │                 │
│                 │ │ └───────────────┬────────────────────────┘   │ │                 │
│                 │ │                 │                             │ │                 │
│                 │ │                 ▼                             │ │                 │
│                 │ │ ┌────────────────────────────────────────┐   │──▶                │
│                 │ │ │          MCP Server                    │   │ │                 │
│                 │ │ │   (MCP Tools for Task Operations)      │   │◀──                │
│                 │ │ └────────────────────────────────────────┘   │ │                 │
└─────────────────┘ └──────────────────────────────────────────────┘ └─────────────────┘
```

## Component Breakdown

### 1. Database Layer

**New Models**:
- `Conversation` model in `backend/src/models/conversation.py`
- `Message` model in `backend/src/models/message.py`

**New Schemas**:
- `ChatRequest`, `ChatResponse` in `backend/src/schemas/chat.py`
- `ConversationResponse`, `MessageResponse` in `backend/src/schemas/conversation.py`

### 2. MCP Server

**Location**: `backend/src/mcp/`

**Components**:
- `server.py` - MCP server setup using Official MCP SDK
- `tools.py` - Implementation of 5 MCP tools:
  - `add_task`
  - `list_tasks`
  - `complete_task`
  - `delete_task`
  - `update_task`

### 3. AI Agent Layer

**Location**: `backend/src/agent/`

**Components**:
- `agent.py` - OpenAI Agents SDK agent configuration
- `runner.py` - Agent runner with MCP tool integration

### 4. Chat Service

**Location**: `backend/src/services/chat_service.py`

**Responsibilities**:
- Conversation management
- Message persistence
- Agent orchestration
- Response handling

### 5. Chat API

**Location**: `backend/src/api/v1/chat.py`

**Endpoints**:
- `POST /api/v1/chat` - Main chat endpoint
- `GET /api/v1/conversations` - List conversations
- `GET /api/v1/conversations/{id}` - Get conversation with messages
- `DELETE /api/v1/conversations/{id}` - Delete conversation

### 6. Frontend Chat Component

**Location**: `frontend/src/components/chat/`

**Components**:
- `chat-interface.tsx` - Main chat UI using OpenAI ChatKit
- `message-list.tsx` - Display messages
- `message-input.tsx` - Input field for sending messages

### 7. Frontend Chat Page

**Location**: `frontend/src/app/chat/page.tsx`

**Features**:
- Protected route (requires authentication)
- Conversation management
- Real-time chat interface

---

## Implementation Order

### Phase 3.1: Database Setup
1. Create Conversation and Message models
2. Create Pydantic schemas for chat
3. Run database migrations
4. Create conversation and message services

### Phase 3.2: MCP Server
1. Install MCP SDK dependencies
2. Create MCP server structure
3. Implement 5 MCP tools
4. Test tools independently

### Phase 3.3: AI Agent
1. Install OpenAI Agents SDK
2. Create agent configuration
3. Connect agent to MCP tools
4. Test agent with sample prompts

### Phase 3.4: Chat API
1. Create chat endpoint
2. Implement conversation management
3. Integrate agent with API
4. Add authentication

### Phase 3.5: Frontend
1. Install OpenAI ChatKit
2. Create chat interface component
3. Create chat page
4. Connect to chat API

### Phase 3.6: Testing & Integration
1. Test end-to-end chat flow
2. Test all natural language commands
3. Test conversation persistence
4. Fix bugs and edge cases

---

## Dependencies

### Backend Dependencies (pyproject.toml)

```toml
[project.dependencies]
# Existing dependencies...
openai-agents = "^0.1.0"      # OpenAI Agents SDK
mcp = "^1.0.0"                # Official MCP SDK
```

### Frontend Dependencies (package.json)

```json
{
  "dependencies": {
    "@openai/chatkit": "^0.1.0"
  }
}
```

---

## File Structure

```
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py     # NEW
│   │   ├── message.py          # NEW
│   │   └── task.py             # Existing
│   ├── schemas/
│   │   ├── chat.py             # NEW
│   │   ├── conversation.py     # NEW
│   │   └── task.py             # Existing
│   ├── services/
│   │   ├── chat_service.py     # NEW
│   │   ├── conversation_service.py  # NEW
│   │   └── task_service.py     # Existing
│   ├── mcp/                    # NEW
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools.py
│   ├── agent/                  # NEW
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── runner.py
│   └── api/
│       └── v1/
│           ├── chat.py         # NEW
│           └── tasks.py        # Existing

frontend/
├── src/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx        # NEW
│   │   └── dashboard/
│   │       └── page.tsx        # Existing
│   ├── components/
│   │   ├── chat/               # NEW
│   │   │   ├── chat-interface.tsx
│   │   │   ├── message-list.tsx
│   │   │   └── message-input.tsx
│   │   └── tasks/              # Existing
│   └── lib/
│       ├── api/
│       │   └── chat.ts         # NEW
│       └── hooks/
│           └── use-chat.ts     # NEW
```

---

## Key Technical Decisions

### 1. Stateless Architecture
- All conversation state persisted to database
- No in-memory conversation storage
- Any server instance can handle any request

### 2. MCP over Direct Function Calls
- Standardized tool interface
- Future extensibility (add more tools easily)
- AI agent can chain tools as needed

### 3. OpenAI Agents SDK
- Built-in tool handling
- Conversation management
- Error handling and retries

### 4. ChatKit for Frontend
- Pre-built chat UI components
- Consistent with OpenAI ecosystem
- Reduces frontend development time

---

## Risk Mitigation

### Risk: OpenAI API Latency
**Mitigation**: Show loading indicators, implement timeout handling

### Risk: Complex Natural Language
**Mitigation**: Agent should ask for clarification when unsure

### Risk: Tool Execution Failures
**Mitigation**: Graceful error handling, informative error messages

### Risk: Database Connection Issues
**Mitigation**: Retry logic, connection pooling

---

## Success Metrics

1. Chat response time < 5 seconds (including OpenAI latency)
2. AI correctly interprets user intent > 90% of the time
3. Conversation persistence works 100% of the time
4. All 5 MCP tools work correctly
5. Zero security vulnerabilities (user isolation maintained)
