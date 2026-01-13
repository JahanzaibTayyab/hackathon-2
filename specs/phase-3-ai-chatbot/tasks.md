# Implementation Tasks: Phase 3 - Todo AI Chatbot

**Date**: 2026-01-13
**Feature**: Phase 3 AI-Powered Todo Chatbot

## Task Status Legend
- [ ] Not Started
- [x] Completed
- [~] In Progress

---

## Phase 3.1: Database Setup

### T-301: Create Conversation Model
**Status**: [ ]
**Priority**: P1
**Depends On**: None

**Description**: Create SQLModel for Conversation table

**Files to Create/Modify**:
- `backend/src/models/conversation.py` (CREATE)
- `backend/src/models/__init__.py` (MODIFY)

**Acceptance Criteria**:
- Conversation model has id, user_id, created_at, updated_at fields
- Model is properly indexed on user_id and created_at
- Model can be created, read, updated, deleted

---

### T-302: Create Message Model
**Status**: [ ]
**Priority**: P1
**Depends On**: T-301

**Description**: Create SQLModel for Message table

**Files to Create/Modify**:
- `backend/src/models/message.py` (CREATE)
- `backend/src/models/__init__.py` (MODIFY)

**Acceptance Criteria**:
- Message model has id, conversation_id, user_id, role, content, tool_calls, created_at
- Model is properly indexed on conversation_id and user_id
- Foreign key to conversations table works

---

### T-303: Create Chat Schemas
**Status**: [ ]
**Priority**: P1
**Depends On**: None

**Description**: Create Pydantic schemas for chat request/response

**Files to Create/Modify**:
- `backend/src/schemas/chat.py` (CREATE)
- `backend/src/schemas/conversation.py` (CREATE)
- `backend/src/schemas/__init__.py` (MODIFY)

**Acceptance Criteria**:
- ChatRequest schema with message and optional conversation_id
- ChatResponse schema with conversation_id, response, tool_calls
- ConversationResponse and MessageResponse schemas

---

### T-304: Create Database Tables
**Status**: [ ]
**Priority**: P1
**Depends On**: T-301, T-302

**Description**: Run migrations to create conversations and messages tables

**Files to Create/Modify**:
- `backend/scripts/create_chat_tables.py` (CREATE)

**Acceptance Criteria**:
- conversations table exists in database
- messages table exists in database
- Foreign keys and indexes are created

---

### T-305: Create Conversation Service
**Status**: [ ]
**Priority**: P1
**Depends On**: T-301, T-302, T-304

**Description**: Create service layer for conversation and message operations

**Files to Create/Modify**:
- `backend/src/services/conversation_service.py` (CREATE)

**Acceptance Criteria**:
- Can create new conversation
- Can get conversation by ID with user isolation
- Can list conversations for user
- Can add messages to conversation
- Can get messages for conversation
- Can delete conversation

---

## Phase 3.2: MCP Server

### T-306: Install MCP Dependencies
**Status**: [ ]
**Priority**: P1
**Depends On**: None

**Description**: Add MCP SDK to project dependencies

**Files to Create/Modify**:
- `backend/pyproject.toml` (MODIFY)

**Acceptance Criteria**:
- MCP SDK is installed and importable
- No dependency conflicts

---

### T-307: Create MCP Server Structure
**Status**: [ ]
**Priority**: P1
**Depends On**: T-306

**Description**: Set up MCP server skeleton

**Files to Create/Modify**:
- `backend/src/mcp/__init__.py` (CREATE)
- `backend/src/mcp/server.py` (CREATE)

**Acceptance Criteria**:
- MCP server can be initialized
- Server structure follows MCP SDK patterns

---

### T-308: Implement add_task Tool
**Status**: [ ]
**Priority**: P1
**Depends On**: T-307

**Description**: Create MCP tool for adding tasks

**Files to Create/Modify**:
- `backend/src/mcp/tools.py` (CREATE)

**Acceptance Criteria**:
- Tool accepts user_id, title, description parameters
- Tool creates task via task service
- Tool returns task_id, status, title

---

### T-309: Implement list_tasks Tool
**Status**: [ ]
**Priority**: P1
**Depends On**: T-308

**Description**: Create MCP tool for listing tasks

**Files to Create/Modify**:
- `backend/src/mcp/tools.py` (MODIFY)

**Acceptance Criteria**:
- Tool accepts user_id and optional status parameter
- Tool lists tasks via task service
- Tool returns array of task objects

---

### T-310: Implement complete_task Tool
**Status**: [ ]
**Priority**: P1
**Depends On**: T-308

**Description**: Create MCP tool for completing tasks

**Files to Create/Modify**:
- `backend/src/mcp/tools.py` (MODIFY)

**Acceptance Criteria**:
- Tool accepts user_id and task_id parameters
- Tool marks task as completed via task service
- Tool returns task_id, status, title

---

### T-311: Implement delete_task Tool
**Status**: [ ]
**Priority**: P1
**Depends On**: T-308

**Description**: Create MCP tool for deleting tasks

**Files to Create/Modify**:
- `backend/src/mcp/tools.py` (MODIFY)

**Acceptance Criteria**:
- Tool accepts user_id and task_id parameters
- Tool deletes task via task service
- Tool returns task_id, status, title

---

### T-312: Implement update_task Tool
**Status**: [ ]
**Priority**: P1
**Depends On**: T-308

**Description**: Create MCP tool for updating tasks

**Files to Create/Modify**:
- `backend/src/mcp/tools.py` (MODIFY)

**Acceptance Criteria**:
- Tool accepts user_id, task_id, title, description parameters
- Tool updates task via task service
- Tool returns task_id, status, title

---

## Phase 3.3: AI Agent

### T-313: Install OpenAI Agents SDK
**Status**: [ ]
**Priority**: P1
**Depends On**: None

**Description**: Add OpenAI Agents SDK to project dependencies

**Files to Create/Modify**:
- `backend/pyproject.toml` (MODIFY)

**Acceptance Criteria**:
- OpenAI Agents SDK is installed and importable
- Environment variable OPENAI_API_KEY is configured

---

### T-314: Create Agent Configuration
**Status**: [ ]
**Priority**: P1
**Depends On**: T-313, T-307

**Description**: Configure OpenAI agent with system prompt

**Files to Create/Modify**:
- `backend/src/agent/__init__.py` (CREATE)
- `backend/src/agent/agent.py` (CREATE)

**Acceptance Criteria**:
- Agent has appropriate system prompt for task management
- Agent is configured to use MCP tools
- Agent handles conversation context

---

### T-315: Create Agent Runner
**Status**: [ ]
**Priority**: P1
**Depends On**: T-314, T-308-T-312

**Description**: Create runner to execute agent with MCP tools

**Files to Create/Modify**:
- `backend/src/agent/runner.py` (CREATE)

**Acceptance Criteria**:
- Runner can execute agent with user message
- Runner passes user_id to MCP tools
- Runner returns agent response and tool calls

---

## Phase 3.4: Chat API

### T-316: Create Chat Service
**Status**: [ ]
**Priority**: P1
**Depends On**: T-305, T-315

**Description**: Create service to orchestrate chat interactions

**Files to Create/Modify**:
- `backend/src/services/chat_service.py` (CREATE)

**Acceptance Criteria**:
- Service can process chat message
- Service manages conversation history
- Service persists messages to database
- Service returns response and tool calls

---

### T-317: Create Chat Endpoint
**Status**: [ ]
**Priority**: P1
**Depends On**: T-316

**Description**: Create POST /api/v1/chat endpoint

**Files to Create/Modify**:
- `backend/src/api/v1/chat.py` (CREATE)
- `backend/src/api/v1/__init__.py` (MODIFY)
- `backend/src/main.py` (MODIFY)

**Acceptance Criteria**:
- Endpoint accepts message and conversation_id
- Endpoint requires JWT authentication
- Endpoint returns conversation_id, response, tool_calls

---

### T-318: Create Conversation Endpoints
**Status**: [ ]
**Priority**: P2
**Depends On**: T-305

**Description**: Create endpoints for conversation management

**Files to Create/Modify**:
- `backend/src/api/v1/chat.py` (MODIFY)

**Acceptance Criteria**:
- GET /api/v1/conversations lists conversations
- GET /api/v1/conversations/{id} returns conversation with messages
- DELETE /api/v1/conversations/{id} deletes conversation

---

## Phase 3.5: Frontend

### T-319: Install ChatKit Dependencies
**Status**: [ ]
**Priority**: P1
**Depends On**: None

**Description**: Add OpenAI ChatKit to frontend dependencies

**Files to Create/Modify**:
- `frontend/package.json` (MODIFY)

**Acceptance Criteria**:
- ChatKit is installed and importable
- No dependency conflicts

---

### T-320: Create Chat API Client
**Status**: [ ]
**Priority**: P1
**Depends On**: T-317

**Description**: Create API client for chat endpoints

**Files to Create/Modify**:
- `frontend/src/lib/api/chat.ts` (CREATE)

**Acceptance Criteria**:
- Client can send chat messages
- Client includes JWT token
- Client handles errors

---

### T-321: Create Chat Hook
**Status**: [ ]
**Priority**: P1
**Depends On**: T-320

**Description**: Create React hook for chat state management

**Files to Create/Modify**:
- `frontend/src/lib/hooks/use-chat.ts` (CREATE)

**Acceptance Criteria**:
- Hook manages conversation state
- Hook handles sending messages
- Hook handles loading/error states

---

### T-322: Create Chat Interface Component
**Status**: [ ]
**Priority**: P1
**Depends On**: T-319, T-321

**Description**: Create main chat UI component

**Files to Create/Modify**:
- `frontend/src/components/chat/chat-interface.tsx` (CREATE)
- `frontend/src/components/chat/message-list.tsx` (CREATE)
- `frontend/src/components/chat/message-input.tsx` (CREATE)

**Acceptance Criteria**:
- Chat interface displays messages
- Chat interface accepts user input
- Chat interface shows loading states
- Chat interface handles errors

---

### T-323: Create Chat Page
**Status**: [ ]
**Priority**: P1
**Depends On**: T-322

**Description**: Create chat page with navigation

**Files to Create/Modify**:
- `frontend/src/app/chat/page.tsx` (CREATE)

**Acceptance Criteria**:
- Page is protected (requires authentication)
- Page loads conversation history
- Page allows sending messages
- Navigation from dashboard to chat

---

### T-324: Add Chat Navigation
**Status**: [ ]
**Priority**: P2
**Depends On**: T-323

**Description**: Add navigation link to chat from dashboard

**Files to Create/Modify**:
- `frontend/src/app/dashboard/page.tsx` (MODIFY)

**Acceptance Criteria**:
- Dashboard has link/button to chat
- Users can easily navigate between dashboard and chat

---

## Phase 3.6: Testing & Integration

### T-325: Test MCP Tools
**Status**: [ ]
**Priority**: P1
**Depends On**: T-308-T-312

**Description**: Write tests for all MCP tools

**Files to Create/Modify**:
- `backend/tests/unit/test_mcp_tools.py` (CREATE)

**Acceptance Criteria**:
- All 5 tools have test coverage
- Tests verify user isolation
- Tests verify error handling

---

### T-326: Test Chat Endpoint
**Status**: [ ]
**Priority**: P1
**Depends On**: T-317

**Description**: Write integration tests for chat endpoint

**Files to Create/Modify**:
- `backend/tests/integration/test_chat_api.py` (CREATE)

**Acceptance Criteria**:
- Test chat message handling
- Test conversation creation
- Test authentication requirement

---

### T-327: Test Frontend Chat
**Status**: [ ]
**Priority**: P2
**Depends On**: T-322

**Description**: Write tests for frontend chat components

**Files to Create/Modify**:
- `frontend/src/__tests__/components/chat-interface.test.tsx` (CREATE)

**Acceptance Criteria**:
- Test message display
- Test message sending
- Test loading states

---

### T-328: End-to-End Testing
**Status**: [ ]
**Priority**: P1
**Depends On**: T-325, T-326, T-327

**Description**: Verify complete chat flow works

**Acceptance Criteria**:
- User can create task via chat
- User can list tasks via chat
- User can complete task via chat
- User can delete task via chat
- User can update task via chat
- Conversation persists after refresh

---

## Summary

| Phase | Tasks | Priority |
|-------|-------|----------|
| 3.1 Database | T-301 to T-305 | P1 |
| 3.2 MCP Server | T-306 to T-312 | P1 |
| 3.3 AI Agent | T-313 to T-315 | P1 |
| 3.4 Chat API | T-316 to T-318 | P1/P2 |
| 3.5 Frontend | T-319 to T-324 | P1/P2 |
| 3.6 Testing | T-325 to T-328 | P1/P2 |

**Total Tasks**: 28
**P1 Tasks**: 23
**P2 Tasks**: 5
