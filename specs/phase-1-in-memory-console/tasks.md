# Tasks: Phase 1 - In-Memory Python Console Todo App

**Input**: Design documents from `/specs/phase-1-in-memory-console/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are REQUIRED - following TDD approach (Red-Green-Refactor)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure: `todo_hackathon/src/todo_hackathon/` and `todo_hackathon/tests/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with pytest dependency in pyproject.toml
- [ ] T003 [P] Configure pytest in pyproject.toml with test discovery settings
- [ ] T004 [P] Create tests directory structure: tests/__init__.py, tests/unit/, tests/integration/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create Todo model in src/todo_hackathon/models.py using dataclass
- [ ] T006 [P] Create in-memory storage interface in src/todo_hackathon/storage.py
- [ ] T007 [P] Implement TodoStorage class with create, get, get_all methods in src/todo_hackathon/storage.py
- [ ] T008 Configure error handling infrastructure (custom exceptions) in src/todo_hackathon/exceptions.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and View Todos (Priority: P1) 🎯 MVP

**Goal**: Users can create new todos and view their list of todos

**Independent Test**: Create a todo, list todos, verify todo appears with correct ID, title, and status

### Tests for User Story 1 (REQUIRED - TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Unit test for Todo model creation in tests/unit/test_models.py
- [ ] T010 [P] [US1] Unit test for storage create operation in tests/unit/test_storage.py
- [ ] T011 [P] [US1] Unit test for storage get_all operation in tests/unit/test_storage.py
- [ ] T012 [P] [US1] Integration test for create and list workflow in tests/integration/test_create_list.py

### Implementation for User Story 1

- [ ] T013 [US1] Implement Todo dataclass with id, title, description, completed, created_at, updated_at in src/todo_hackathon/models.py
- [ ] T014 [US1] Implement TodoStorage.create() method in src/todo_hackathon/storage.py
- [ ] T015 [US1] Implement TodoStorage.get_all() method in src/todo_hackathon/storage.py
- [ ] T016 [US1] Implement ID generation logic (sequential starting from 1) in src/todo_hackathon/storage.py
- [ ] T017 [US1] Implement timestamp generation (created_at, updated_at) in src/todo_hackathon/models.py or storage.py
- [ ] T018 [US1] Create command handler for 'add' command in src/todo_hackathon/commands.py
- [ ] T019 [US1] Create command handler for 'list' command in src/todo_hackathon/commands.py
- [ ] T020 [US1] Implement CLI parser for 'add' and 'list' commands in src/todo_hackathon/cli.py
- [ ] T021 [US1] Add validation for non-empty title in src/todo_hackathon/commands.py
- [ ] T022 [US1] Implement empty list message display in src/todo_hackathon/commands.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Update Todo Status (Priority: P2)

**Goal**: Users can mark todos as completed or incomplete to track progress

**Independent Test**: Create a todo, mark it complete, verify status change, mark incomplete, verify status change

### Tests for User Story 2 (REQUIRED - TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US2] Unit test for storage update operation (complete status) in tests/unit/test_storage.py
- [ ] T024 [P] [US2] Integration test for complete/incomplete workflow in tests/integration/test_status_update.py

### Implementation for User Story 2

- [ ] T025 [US2] Implement TodoStorage.update() method for status changes in src/todo_hackathon/storage.py
- [ ] T026 [US2] Implement updated_at timestamp update on status change in src/todo_hackathon/storage.py
- [ ] T027 [US2] Create command handler for 'complete' command in src/todo_hackathon/commands.py
- [ ] T028 [US2] Create command handler for 'incomplete' command in src/todo_hackathon/commands.py
- [ ] T029 [US2] Implement CLI parser for 'complete' and 'incomplete' commands in src/todo_hackathon/cli.py
- [ ] T030 [US2] Update list command to display completed status ([x] vs [ ]) in src/todo_hackathon/commands.py
- [ ] T031 [US2] Add error handling for todo not found in status update commands in src/todo_hackathon/commands.py

**Checkpoint**: At this point, User Story 2 should be fully functional and testable independently

---

## Phase 5: User Story 3 - Update Todo Details (Priority: P2)

**Goal**: Users can update the title and description of existing todos

**Independent Test**: Create a todo, update title, verify change, update description, verify change, check updated_at timestamp

### Tests for User Story 3 (REQUIRED - TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T032 [P] [US3] Unit test for storage update operation (title/description) in tests/unit/test_storage.py
- [ ] T033 [P] [US3] Integration test for update workflow in tests/integration/test_update_details.py

### Implementation for User Story 3

- [ ] T034 [US3] Extend TodoStorage.update() method to handle title updates in src/todo_hackathon/storage.py
- [ ] T035 [US3] Extend TodoStorage.update() method to handle description updates in src/todo_hackathon/storage.py
- [ ] T036 [US3] Create command handler for 'update' command in src/todo_hackathon/commands.py
- [ ] T037 [US3] Implement CLI parser for 'update' command with field and value arguments in src/todo_hackathon/cli.py
- [ ] T038 [US3] Add validation for update operations (field exists, value valid) in src/todo_hackathon/commands.py
- [ ] T039 [US3] Ensure updated_at timestamp updates on any field change in src/todo_hackathon/storage.py
- [ ] T040 [US3] Add error handling for todo not found in update command in src/todo_hackathon/commands.py

**Checkpoint**: At this point, User Story 3 should be fully functional and testable independently

---

## Phase 6: User Story 4 - Delete Todo (Priority: P3)

**Goal**: Users can delete todos to remove tasks that are no longer relevant

**Independent Test**: Create multiple todos, delete one, verify it's removed, verify others remain, try to access deleted todo

### Tests for User Story 4 (REQUIRED - TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T041 [P] [US4] Unit test for storage delete operation in tests/unit/test_storage.py
- [ ] T042 [P] [US4] Integration test for delete workflow in tests/integration/test_delete.py

### Implementation for User Story 4

- [ ] T043 [US4] Implement TodoStorage.delete() method in src/todo_hackathon/storage.py
- [ ] T044 [US4] Create command handler for 'delete' command in src/todo_hackathon/commands.py
- [ ] T045 [US4] Implement CLI parser for 'delete' command in src/todo_hackathon/cli.py
- [ ] T046 [US4] Add error handling for todo not found in delete command in src/todo_hackathon/commands.py
- [ ] T047 [US4] Update list command to exclude deleted todos (implicit, but verify) in src/todo_hackathon/commands.py

**Checkpoint**: At this point, User Story 4 should be fully functional and testable independently

---

## Phase 7: User Story 1 Enhancement - View Single Todo (Priority: P1)

**Goal**: Users can view detailed information about a single todo

**Independent Test**: Create a todo, view it by ID, verify all fields are displayed correctly

### Tests for User Story 1 Enhancement (REQUIRED - TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T048 [P] [US1] Unit test for storage get operation in tests/unit/test_storage.py
- [ ] T049 [P] [US1] Integration test for view single todo workflow in tests/integration/test_view_todo.py

### Implementation for User Story 1 Enhancement

- [ ] T050 [US1] Implement TodoStorage.get() method in src/todo_hackathon/storage.py
- [ ] T051 [US1] Create command handler for 'view' command in src/todo_hackathon/commands.py
- [ ] T052 [US1] Implement CLI parser for 'view' command in src/todo_hackathon/cli.py
- [ ] T053 [US1] Format todo details display (all fields) in src/todo_hackathon/commands.py
- [ ] T054 [US1] Add error handling for todo not found in view command in src/todo_hackathon/commands.py

**Checkpoint**: View functionality complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, error handling improvements, and user experience enhancements

- [ ] T055 Create main entry point with interactive loop in src/todo_hackathon/main.py
- [ ] T056 Implement 'help' command to show available commands in src/todo_hackathon/commands.py
- [ ] T057 Implement 'exit' command to quit application in src/todo_hackathon/cli.py
- [ ] T058 [P] Add comprehensive error messages for all error scenarios in src/todo_hackathon/commands.py
- [ ] T059 [P] Add input validation for all commands in src/todo_hackathon/cli.py
- [ ] T060 Create integration test for full user workflow (all commands) in tests/integration/test_full_workflow.py
- [ ] T061 Update pyproject.toml with entry point configuration for todo-hackathon command
- [ ] T062 Add docstrings to all public functions and classes
- [ ] T063 Verify 80%+ test coverage with pytest --cov
- [ ] T064 Update README.md with installation and usage instructions

**Checkpoint**: Phase 1 complete and ready for review

---

## Dependencies

### User Story Completion Order

1. **User Story 1** (P1) - Must be completed first (MVP)
2. **User Story 2** (P2) - Can start after US1, depends on storage update method
3. **User Story 3** (P2) - Can start after US1, depends on storage update method
4. **User Story 4** (P3) - Can start after US1, independent of US2/US3

### Parallel Execution Opportunities

- **Setup Phase**: T003, T004 can run in parallel
- **Foundation Phase**: T006, T007, T008 can run in parallel after T005
- **Within User Stories**: Test tasks marked [P] can run in parallel with implementation tasks
- **User Stories 2, 3, 4**: Can be developed in parallel after User Story 1 is complete

## Implementation Strategy

### MVP Scope
- **Minimum**: User Story 1 only (Create and View Todos)
- **Recommended**: User Stories 1 + 2 (Create, View, Complete/Incomplete)
- **Full Phase 1**: All 4 user stories

### Incremental Delivery
1. Complete Phase 1-2 (Setup + Foundation)
2. Complete Phase 3 (User Story 1) → MVP ready
3. Complete Phase 4 (User Story 2) → Enhanced MVP
4. Complete Phase 5-6 (User Stories 3-4) → Full CRUD
5. Complete Phase 7-8 (Enhancements + Polish) → Production ready

## Task Summary

- **Total Tasks**: 64
- **Setup Tasks**: 4
- **Foundation Tasks**: 4
- **User Story 1 Tasks**: 14 (6 tests + 8 implementation)
- **User Story 2 Tasks**: 9 (2 tests + 7 implementation)
- **User Story 3 Tasks**: 8 (2 tests + 6 implementation)
- **User Story 4 Tasks**: 7 (2 tests + 5 implementation)
- **Polish Tasks**: 10

