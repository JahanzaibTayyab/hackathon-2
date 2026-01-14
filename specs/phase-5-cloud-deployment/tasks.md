# Phase V: Advanced Cloud Deployment - Tasks

## Implementation Tasks Breakdown

**Phase**: Phase V - Advanced Cloud Deployment
**From Plan**: plan.md
**Status**: Tasks Defined - Ready for Implementation

---

## Task Naming Convention

- **T-A##**: Part A (Advanced Features & Kafka)
- **T-B##**: Part B (Local Dapr Deployment)
- **T-C##**: Part C (Cloud Deployment)
- **T-D##**: Documentation

---

## Part A: Advanced Features & Kafka Integration

### A1. Database Schema Updates

#### T-A01: Create Database Migration Script
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: None

**Description**: Create migration script to add new columns to tasks table.

**Implementation Steps**:
1. Create `backend/scripts/migrate_phase5.py`
2. Add columns: due_date, priority, tags, recurrence_pattern, next_occurrence, reminder_sent
3. Set defaults for existing records
4. Test migration locally
5. Test rollback capability

**SQL Changes**:
```sql
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern JSONB;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS next_occurrence TIMESTAMP;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE;
```

**Acceptance Criteria**:
- [ ] Migration runs without errors
- [ ] Existing data preserved
- [ ] New columns have correct defaults
- [ ] Migration is idempotent

---

#### T-A02: Update Task Model
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-A01

**Description**: Update SQLModel Task class with new fields.

**Files to Modify**:
- `backend/src/models/task.py`

**Implementation**:
```python
from sqlalchemy import Column, ARRAY, String
from sqlalchemy.dialects.postgresql import JSON

class Task(SQLModel, table=True):
    # ... existing fields ...
    due_date: datetime | None = None
    priority: str = Field(default="medium")
    tags: list[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    recurrence_pattern: dict | None = Field(default=None, sa_column=Column(JSON))
    next_occurrence: datetime | None = None
    reminder_sent: bool = False
```

**Acceptance Criteria**:
- [ ] Model includes all new fields
- [ ] Type hints correct
- [ ] Default values appropriate
- [ ] SQLModel generates correct SQL

---

#### T-A03: Update Task Schemas
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-A02

**Description**: Update Pydantic schemas for API request/response.

**Files to Modify**:
- `backend/src/schemas/task.py`

**New Schemas**:
```python
class RecurrencePattern(BaseModel):
    type: Literal["daily", "weekly", "monthly", "yearly"]
    interval: int = 1
    days_of_week: list[int] | None = None  # 0-6 for weekly
    day_of_month: int | None = None  # 1-31 for monthly
    end_date: datetime | None = None
    occurrences: int | None = None

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    tags: list[str] = []
    recurrence_pattern: RecurrencePattern | None = None

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    completed: bool
    due_date: datetime | None
    priority: str
    tags: list[str]
    recurrence_pattern: dict | None
    created_at: datetime
    updated_at: datetime
```

**Acceptance Criteria**:
- [ ] All new fields in schemas
- [ ] Validation constraints correct
- [ ] Serialization works

---

### A2. Backend API Updates

#### T-A04: Update Task Service
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-A03

**Description**: Update task service with search, filter, sort logic.

**Files to Modify**:
- `backend/src/services/task_service.py`

**New Methods**:
```python
async def get_tasks(
    self,
    user_id: str,
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc"
) -> list[Task]:
    # Build query with filters
    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    if priority:
        query = query.where(Task.priority == priority)

    if tags:
        query = query.where(Task.tags.contains(tags))

    if due_before:
        query = query.where(Task.due_date <= due_before)

    if due_after:
        query = query.where(Task.due_date >= due_after)

    if search:
        search_filter = or_(
            Task.title.ilike(f"%{search}%"),
            Task.description.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Apply sorting
    sort_column = getattr(Task, sort_by, Task.created_at)
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    result = await self.session.execute(query)
    return result.scalars().all()
```

**Acceptance Criteria**:
- [ ] Filtering by all criteria works
- [ ] Search returns correct results
- [ ] Sorting by all fields works
- [ ] Combined filters work correctly

---

#### T-A05: Update Tasks Router
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-A04

**Description**: Update API endpoints with query parameters.

**Files to Modify**:
- `backend/src/api/v1/tasks.py`

**Updated Endpoint**:
```python
@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    status: str | None = Query(None, regex="^(pending|completed)$"),
    priority: str | None = Query(None, regex="^(low|medium|high|urgent)$"),
    tags: str | None = Query(None, description="Comma-separated tags"),
    due_before: datetime | None = Query(None),
    due_after: datetime | None = Query(None),
    search: str | None = Query(None, min_length=1, max_length=100),
    sort_by: str = Query("created_at", regex="^(created_at|due_date|priority|title)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    user_id: str = Depends(get_current_user_id),
    task_service: TaskService = Depends(get_task_service)
):
    tags_list = tags.split(",") if tags else None
    return await task_service.get_tasks(
        user_id=user_id,
        status=status,
        priority=priority,
        tags=tags_list,
        due_before=due_before,
        due_after=due_after,
        search=search,
        sort_by=sort_by,
        order=order
    )
```

**Acceptance Criteria**:
- [ ] Query parameters validated
- [ ] All filters accessible via API
- [ ] API documentation updated

---

#### T-A06: Implement Recurring Task Logic
**Priority**: High
**Estimated Complexity**: High
**Dependencies**: T-A04

**Description**: Implement logic for recurring task creation and next instance generation.

**Files to Create**:
- `backend/src/services/recurrence_service.py`

**Implementation**:
```python
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class RecurrenceService:
    def calculate_next_occurrence(
        self,
        pattern: dict,
        from_date: datetime
    ) -> datetime | None:
        rec_type = pattern.get("type")
        interval = pattern.get("interval", 1)

        if rec_type == "daily":
            return from_date + timedelta(days=interval)
        elif rec_type == "weekly":
            days = pattern.get("days_of_week", [from_date.weekday()])
            # Calculate next occurrence from days_of_week
            return self._next_weekly(from_date, days, interval)
        elif rec_type == "monthly":
            return from_date + relativedelta(months=interval)
        elif rec_type == "yearly":
            return from_date + relativedelta(years=interval)
        return None

    def should_create_next(self, pattern: dict, current_count: int) -> bool:
        end_date = pattern.get("end_date")
        max_occurrences = pattern.get("occurrences")

        if end_date and datetime.utcnow() > end_date:
            return False
        if max_occurrences and current_count >= max_occurrences:
            return False
        return True

    async def create_next_instance(self, original_task: Task) -> Task | None:
        if not original_task.recurrence_pattern:
            return None

        next_date = self.calculate_next_occurrence(
            original_task.recurrence_pattern,
            original_task.due_date or datetime.utcnow()
        )

        if not next_date:
            return None

        new_task = Task(
            user_id=original_task.user_id,
            title=original_task.title,
            description=original_task.description,
            due_date=next_date,
            priority=original_task.priority,
            tags=original_task.tags,
            recurrence_pattern=original_task.recurrence_pattern,
            completed=False
        )
        return new_task
```

**Acceptance Criteria**:
- [ ] Daily recurrence calculates correctly
- [ ] Weekly recurrence handles day selection
- [ ] Monthly recurrence handles edge cases (31st)
- [ ] Yearly recurrence works
- [ ] End conditions respected

---

### A3. Frontend Updates

#### T-A07: Create Priority Select Component
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: None

**Description**: Create dropdown component for task priority selection.

**Files to Create**:
- `frontend/src/components/tasks/priority-select.tsx`

**Implementation**:
```tsx
"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const priorities = [
  { value: "low", label: "Low", color: "bg-gray-400" },
  { value: "medium", label: "Medium", color: "bg-blue-400" },
  { value: "high", label: "High", color: "bg-orange-400" },
  { value: "urgent", label: "Urgent", color: "bg-red-500" },
];

interface PrioritySelectProps {
  value: string;
  onChange: (value: string) => void;
}

export function PrioritySelect({ value, onChange }: PrioritySelectProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger>
        <SelectValue placeholder="Select priority" />
      </SelectTrigger>
      <SelectContent>
        {priorities.map((p) => (
          <SelectItem key={p.value} value={p.value}>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${p.color}`} />
              {p.label}
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

**Acceptance Criteria**:
- [ ] Visual priority indicators
- [ ] Accessible keyboard navigation
- [ ] State controlled via props

---

#### T-A08: Create Date Picker Component
**Priority**: High
**Estimated Complexity**: Medium
**Dependencies**: None

**Description**: Create date/time picker for due dates.

**Files to Create**:
- `frontend/src/components/tasks/date-picker.tsx`

**Dependencies to Add**:
```bash
pnpm add date-fns @radix-ui/react-popover
```

**Acceptance Criteria**:
- [ ] Calendar popup works
- [ ] Time selection available
- [ ] Clear button available
- [ ] Accessible

---

#### T-A09: Create Tag Input Component
**Priority**: High
**Estimated Complexity**: Medium
**Dependencies**: None

**Description**: Create component for adding/removing tags with auto-suggest.

**Files to Create**:
- `frontend/src/components/tasks/tag-input.tsx`

**Features**:
- Multi-select tags
- Create new tags inline
- Remove tags with X or backspace
- Auto-suggest existing tags

**Acceptance Criteria**:
- [ ] Add tags via input
- [ ] Remove tags
- [ ] Auto-suggest works
- [ ] Visual tag chips

---

#### T-A10: Create Recurrence Picker Component
**Priority**: Medium
**Estimated Complexity**: High
**Dependencies**: T-A08

**Description**: Create component for configuring task recurrence patterns.

**Files to Create**:
- `frontend/src/components/tasks/recurrence-picker.tsx`

**UI Elements**:
- Toggle: Enable/disable recurrence
- Type select: Daily, Weekly, Monthly, Yearly
- Interval input: Every X days/weeks/months/years
- Day selector: For weekly (checkboxes for Mon-Sun)
- Day of month: For monthly (1-31)
- End condition: Never, Date, After X occurrences

**Acceptance Criteria**:
- [ ] All recurrence types configurable
- [ ] Weekly day selection works
- [ ] End conditions work
- [ ] Pattern serializes correctly

---

#### T-A11: Create Task Filters Component
**Priority**: High
**Estimated Complexity**: Medium
**Dependencies**: T-A07

**Description**: Create filter panel for advanced task filtering.

**Files to Create**:
- `frontend/src/components/tasks/task-filters.tsx`

**Filters**:
- Status: All, Pending, Completed
- Priority: Multi-select
- Tags: Multi-select with existing tags
- Due date range: Today, This week, This month, Custom
- Clear all filters button

**Acceptance Criteria**:
- [ ] All filters functional
- [ ] Filters combinable
- [ ] Clear all resets state
- [ ] Filter state in URL (optional)

---

#### T-A12: Create Search Component
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: None

**Description**: Create search input with debounce.

**Files to Create**:
- `frontend/src/components/tasks/task-search.tsx`

**Features**:
- Debounced input (300ms)
- Clear button
- Search icon
- Loading indicator

**Acceptance Criteria**:
- [ ] Debounce prevents excessive API calls
- [ ] Clear resets search
- [ ] Results update as typing

---

#### T-A13: Update Task Form
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-A07, T-A08, T-A09, T-A10

**Description**: Update task creation/edit form with all new fields.

**Files to Modify**:
- `frontend/src/components/tasks/task-form.tsx`

**Form Fields**:
- Title (existing)
- Description (existing)
- Due date (new)
- Priority (new)
- Tags (new)
- Recurrence (new)

**Acceptance Criteria**:
- [ ] All fields in form
- [ ] Validation works
- [ ] Edit loads existing values
- [ ] Submit includes new fields

---

#### T-A14: Update Task Item Display
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-A13

**Description**: Update task list item to display new fields.

**Files to Modify**:
- `frontend/src/components/tasks/task-item.tsx`

**Display Elements**:
- Priority indicator (color dot)
- Due date (relative: "Due in 2 days")
- Overdue indicator (red text)
- Tags (chips)
- Recurring icon

**Acceptance Criteria**:
- [ ] All fields displayed
- [ ] Overdue tasks highlighted
- [ ] Tags clickable to filter

---

#### T-A15: Update React Query Hooks
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-A05

**Description**: Update React Query hooks to support new query parameters.

**Files to Modify**:
- `frontend/src/lib/hooks/use-tasks.ts`

**Updated Hook**:
```typescript
interface TaskFilters {
  status?: string;
  priority?: string;
  tags?: string[];
  due_before?: Date;
  due_after?: Date;
  search?: string;
  sort_by?: string;
  order?: string;
}

export function useTasks(filters: TaskFilters = {}) {
  const queryKey = ["tasks", filters];

  return useQuery({
    queryKey,
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.status) params.set("status", filters.status);
      if (filters.priority) params.set("priority", filters.priority);
      if (filters.tags?.length) params.set("tags", filters.tags.join(","));
      if (filters.search) params.set("search", filters.search);
      // ... other params

      const response = await apiClient.get(`/tasks?${params}`);
      return response.data;
    }
  });
}
```

**Acceptance Criteria**:
- [ ] Filters passed to API
- [ ] Cache invalidation correct
- [ ] Optimistic updates work

---

### A4. Event System Setup

#### T-A16: Create Event Schemas
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-A03

**Description**: Define Pydantic schemas for Kafka events.

**Files to Create**:
- `backend/src/events/schemas.py`

**Event Schemas**:
```python
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class TaskEvent(BaseModel):
    event_type: str  # task.created, task.updated, task.completed, task.deleted
    task_id: UUID
    user_id: str
    timestamp: datetime
    data: dict

class ReminderEvent(BaseModel):
    event_type: str  # reminder.due_soon, reminder.overdue
    task_id: UUID
    user_id: str
    due_date: datetime
    title: str
```

**Acceptance Criteria**:
- [ ] All event types defined
- [ ] CloudEvents compatible structure
- [ ] Serialization works

---

#### T-A17: Create Dapr Client Wrapper
**Priority**: High
**Estimated Complexity**: Medium
**Dependencies**: T-A16

**Description**: Create wrapper for Dapr pub/sub operations.

**Files to Create**:
- `backend/src/core/dapr.py`
- `backend/src/events/producer.py`

**Implementation**:
```python
import httpx
from typing import Any

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "taskpubsub"

class DaprClient:
    def __init__(self):
        self.base_url = f"http://localhost:{DAPR_HTTP_PORT}"

    async def publish(self, topic: str, data: dict):
        url = f"{self.base_url}/v1.0/publish/{PUBSUB_NAME}/{topic}"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()

    async def get_state(self, store: str, key: str) -> Any:
        url = f"{self.base_url}/v1.0/state/{store}/{key}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 204:
                return None
            return response.json()

    async def save_state(self, store: str, key: str, value: Any):
        url = f"{self.base_url}/v1.0/state/{store}"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=[{
                "key": key,
                "value": value
            }])
            response.raise_for_status()

dapr_client = DaprClient()
```

**Acceptance Criteria**:
- [ ] Publish to topic works
- [ ] State operations work
- [ ] Error handling implemented
- [ ] Retry logic for failures

---

#### T-A18: Create Event Producer
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-A17

**Description**: Create producer class to publish task events.

**Files to Create**:
- `backend/src/events/producer.py`

**Implementation**:
```python
from datetime import datetime
from uuid import UUID
from .schemas import TaskEvent
from ..core.dapr import dapr_client

class EventProducer:
    async def publish_task_created(self, task_id: UUID, user_id: str, data: dict):
        event = TaskEvent(
            event_type="task.created",
            task_id=task_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            data=data
        )
        await dapr_client.publish("task-events", event.model_dump(mode="json"))

    async def publish_task_updated(self, task_id: UUID, user_id: str, data: dict):
        # Similar implementation
        pass

    async def publish_task_completed(self, task_id: UUID, user_id: str):
        # Similar implementation
        pass

    async def publish_task_deleted(self, task_id: UUID, user_id: str):
        # Similar implementation
        pass

event_producer = EventProducer()
```

**Acceptance Criteria**:
- [ ] All event types publishable
- [ ] Timestamps correct
- [ ] JSON serialization works

---

#### T-A19: Integrate Events into Task Service
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-A18

**Description**: Publish events from task service on CRUD operations.

**Files to Modify**:
- `backend/src/services/task_service.py`

**Integration Points**:
```python
async def create_task(self, user_id: str, task_data: TaskCreate) -> Task:
    task = Task(**task_data.model_dump(), user_id=user_id)
    self.session.add(task)
    await self.session.commit()

    # Publish event
    await event_producer.publish_task_created(
        task_id=task.id,
        user_id=user_id,
        data=task_data.model_dump()
    )

    return task
```

**Acceptance Criteria**:
- [ ] Events published on create
- [ ] Events published on update
- [ ] Events published on delete
- [ ] Events published on complete
- [ ] Graceful degradation if Dapr unavailable

---

#### T-A20: Create Event Consumer Endpoints
**Priority**: Medium
**Estimated Complexity**: Medium
**Dependencies**: T-A19

**Description**: Create HTTP endpoints for Dapr to deliver events.

**Files to Create**:
- `backend/src/api/v1/events.py`

**Implementation**:
```python
from fastapi import APIRouter, Request

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/tasks")
async def handle_task_event(request: Request):
    """Handle task-events topic messages"""
    event = await request.json()
    event_type = event.get("event_type")

    # Process event (logging, analytics, etc.)
    logger.info(f"Received task event: {event_type}")

    return {"status": "ok"}

@router.post("/reminders")
async def handle_reminder_event(request: Request):
    """Handle reminders topic messages"""
    event = await request.json()

    # Create in-app notification
    # TODO: Notification service integration

    return {"status": "ok"}
```

**Acceptance Criteria**:
- [ ] Endpoints accessible by Dapr
- [ ] Events processed correctly
- [ ] Idempotent handling
- [ ] Logging for debugging

---

### A5. Testing

#### T-A21: Write Backend Unit Tests
**Priority**: High
**Estimated Complexity**: Medium
**Dependencies**: T-A06

**Description**: Unit tests for new backend functionality.

**Test Files**:
- `backend/tests/unit/test_task_model.py`
- `backend/tests/unit/test_recurrence_service.py`
- `backend/tests/unit/test_event_schemas.py`

**Test Cases**:
- Task model with new fields
- Recurrence calculations for all types
- Event schema validation
- Filter/search logic

**Acceptance Criteria**:
- [ ] >80% code coverage for new code
- [ ] All edge cases covered
- [ ] Tests pass in CI

---

#### T-A22: Write Frontend Unit Tests
**Priority**: Medium
**Estimated Complexity**: Medium
**Dependencies**: T-A14

**Description**: Unit tests for new frontend components.

**Test Files**:
- `frontend/src/components/tasks/__tests__/priority-select.test.tsx`
- `frontend/src/components/tasks/__tests__/task-filters.test.tsx`
- `frontend/src/components/tasks/__tests__/task-search.test.tsx`

**Acceptance Criteria**:
- [ ] Components render correctly
- [ ] User interactions work
- [ ] State updates correctly

---

---

## Part B: Local Dapr Deployment

### B1. Minikube Setup

#### T-B01: Update Minikube Configuration
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: Part A complete

**Description**: Start Minikube with resources for Dapr + Kafka.

**Commands**:
```bash
# Delete existing cluster if needed
minikube delete

# Start with more resources
minikube start --cpus=6 --memory=12288 --driver=docker

# Enable required addons
minikube addons enable metrics-server
```

**Acceptance Criteria**:
- [ ] Minikube running with 6 CPUs, 12GB RAM
- [ ] Sufficient resources for Dapr + Kafka + App

---

### B2. Dapr Installation

#### T-B02: Install Dapr on Minikube
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-B01

**Description**: Install Dapr control plane on Minikube.

**Commands**:
```bash
# Install Dapr CLI (if not installed)
brew install dapr/tap/dapr-cli

# Initialize Dapr on Kubernetes
dapr init -k --wait

# Verify installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
# dapr-operator          dapr-system  True     Running  1         1.13.x   1m
# dapr-sidecar-injector  dapr-system  True     Running  1         1.13.x   1m
# dapr-placement-server  dapr-system  True     Running  1         1.13.x   1m
# dapr-sentry            dapr-system  True     Running  1         1.13.x   1m
```

**Acceptance Criteria**:
- [ ] All Dapr components running
- [ ] Sidecar injector working
- [ ] mTLS enabled

---

### B3. Kafka Deployment

#### T-B03: Deploy Strimzi Operator
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-B01

**Description**: Install Strimzi Kafka operator on Minikube.

**Commands**:
```bash
# Create namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator
kubectl wait deployment/strimzi-cluster-operator \
  --for=condition=available \
  --timeout=300s \
  -n kafka
```

**Acceptance Criteria**:
- [ ] Strimzi operator running
- [ ] CRDs installed

---

#### T-B04: Create Kafka Cluster
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-B03

**Description**: Deploy Kafka cluster using Strimzi.

**Files to Create**:
- `helm-chart/kafka/kafka-cluster.yaml`

**Manifest**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1  # Single replica for local dev
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

**Acceptance Criteria**:
- [ ] Kafka broker running
- [ ] Zookeeper running
- [ ] Topic operator available

---

#### T-B05: Create Kafka Topics
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-B04

**Description**: Create required Kafka topics.

**Files to Create**:
- `helm-chart/kafka/topics.yaml`

**Manifest**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: 86400000  # 24 hours
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 3600000  # 1 hour
```

**Acceptance Criteria**:
- [ ] All 3 topics created
- [ ] Correct retention settings
- [ ] Topics listed in Kafka

---

### B4. Dapr Components

#### T-B06: Create Dapr Pub/Sub Component
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-B05

**Description**: Configure Dapr to use Strimzi Kafka for pub/sub.

**Files to Create**:
- `helm-chart/dapr-components/pubsub.yaml`

**Manifest**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-app-consumer"
    - name: authType
      value: "none"
```

**Acceptance Criteria**:
- [ ] Component applied successfully
- [ ] Dapr connects to Kafka

---

#### T-B07: Create Dapr Subscription
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-B06

**Description**: Configure Dapr subscriptions for event routing.

**Files to Create**:
- `helm-chart/dapr-components/subscription.yaml`

**Manifest**:
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: taskpubsub
  topic: task-events
  route: /events/tasks
  scopes:
    - backend
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: reminders-subscription
spec:
  pubsubname: taskpubsub
  topic: reminders
  route: /events/reminders
  scopes:
    - backend
```

**Acceptance Criteria**:
- [ ] Subscriptions created
- [ ] Events route to correct endpoints

---

### B5. Helm Chart Updates

#### T-B08: Add Dapr Annotations to Deployments
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-B02

**Description**: Update Helm templates with Dapr sidecar annotations.

**Files to Modify**:
- `helm-chart/todo-app/templates/frontend-deployment.yaml`
- `helm-chart/todo-app/templates/backend-deployment.yaml`

**Annotations to Add**:
```yaml
spec:
  template:
    metadata:
      annotations:
        {{- if .Values.dapr.enabled }}
        dapr.io/enabled: "true"
        dapr.io/app-id: "{{ .Chart.Name }}-frontend"
        dapr.io/app-port: "3000"
        dapr.io/enable-mtls: "true"
        {{- end }}
```

**Acceptance Criteria**:
- [ ] Frontend has Dapr sidecar
- [ ] Backend has Dapr sidecar
- [ ] Sidecars healthy

---

#### T-B09: Update Helm Values for Dapr
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-B08

**Description**: Add Dapr configuration to values.yaml.

**Files to Modify**:
- `helm-chart/todo-app/values.yaml`

**New Values**:
```yaml
dapr:
  enabled: true

kafka:
  brokers: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
  topics:
    events: task-events
    reminders: reminders
    updates: task-updates
```

**Acceptance Criteria**:
- [ ] Dapr toggleable via values
- [ ] Kafka config in values

---

### B6. Local Deployment & Testing

#### T-B10: Deploy Application with Dapr
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-B09

**Description**: Full deployment on Minikube with Dapr.

**Steps**:
```bash
# Apply Dapr components
kubectl apply -f helm-chart/dapr-components/

# Update Helm deployment
helm upgrade todo-release helm-chart/todo-app \
  --set dapr.enabled=true \
  --wait

# Verify sidecars
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].name}' | tr ' ' '\n' | grep daprd
```

**Acceptance Criteria**:
- [ ] All pods running with Dapr sidecars
- [ ] Application functional
- [ ] Events published to Kafka

---

#### T-B11: Verify Event Flow
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-B10

**Description**: Test that events flow through Kafka via Dapr.

**Verification Steps**:
```bash
# Check Kafka topics have messages
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning \
  --max-messages 5

# Create a task via API
curl -X POST http://localhost:3000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test event"}'

# Verify event in Kafka
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

**Acceptance Criteria**:
- [ ] Events visible in Kafka
- [ ] Event contains correct data
- [ ] Consumer receives events

---

---

## Part C: Cloud Deployment

### C1. Cloud Infrastructure

#### T-C01: Select Cloud Provider
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: Part B complete

**Description**: Choose and document cloud provider decision.

**Options**:
1. **Azure AKS** (Recommended)
   - Best Dapr integration
   - Azure Container Registry included
   - Azure Service Bus alternative to Kafka

2. **Google Cloud GKE**
   - Good managed Kubernetes
   - Artifact Registry for containers
   - Pub/Sub as Kafka alternative

3. **Oracle Cloud OKE**
   - Free tier available
   - Container Registry included
   - Streaming service for Kafka

**Decision**: Azure AKS (recommended for Dapr support)

**Acceptance Criteria**:
- [ ] Cloud provider selected
- [ ] Account created
- [ ] Free credits/tier confirmed

---

#### T-C02: Create Cloud Kubernetes Cluster
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-C01

**Description**: Provision managed Kubernetes cluster.

**Azure AKS Commands**:
```bash
# Create resource group
az group create --name todo-app-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group todo-app-rg \
  --name todo-app-aks \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys \
  --enable-addons monitoring

# Get credentials
az aks get-credentials --resource-group todo-app-rg --name todo-app-aks
```

**Acceptance Criteria**:
- [ ] Cluster created and healthy
- [ ] kubectl connected
- [ ] 3 nodes running

---

#### T-C03: Create Container Registry
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-C02

**Description**: Create private container registry.

**Azure ACR Commands**:
```bash
# Create ACR
az acr create \
  --resource-group todo-app-rg \
  --name todoappacr$(date +%s) \
  --sku Basic

# Attach to AKS
az aks update \
  --resource-group todo-app-rg \
  --name todo-app-aks \
  --attach-acr todoappacr
```

**Acceptance Criteria**:
- [ ] Registry created
- [ ] AKS can pull images
- [ ] Push access configured

---

### C2. Managed Kafka

#### T-C04: Set Up Redpanda Cloud
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-C01

**Description**: Create managed Kafka cluster on Redpanda Cloud.

**Steps**:
1. Create Redpanda Cloud account
2. Create new cluster (Serverless tier for cost)
3. Create topics: task-events, reminders, task-updates
4. Create SASL credentials
5. Get bootstrap server URL

**Configuration Output**:
```
KAFKA_BROKERS=<cluster-id>.any.us-east-1.mpx.prd.cloud.redpanda.com:9092
KAFKA_USERNAME=<username>
KAFKA_PASSWORD=<password>
```

**Acceptance Criteria**:
- [ ] Redpanda cluster created
- [ ] All 3 topics created
- [ ] SASL credentials working

---

#### T-C05: Create Kafka Secrets in Kubernetes
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-C04

**Description**: Store Kafka credentials in Kubernetes secrets.

**Commands**:
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=brokers='<redpanda-bootstrap-url>' \
  --from-literal=username='<sasl-username>' \
  --from-literal=password='<sasl-password>'
```

**Acceptance Criteria**:
- [ ] Secret created
- [ ] Accessible by pods

---

### C3. Dapr on Cloud

#### T-C06: Install Dapr on Cloud Cluster
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-C02

**Description**: Install Dapr on cloud Kubernetes.

**Azure AKS (with extension)**:
```bash
az k8s-extension create \
  --cluster-type managedClusters \
  --cluster-name todo-app-aks \
  --resource-group todo-app-rg \
  --name dapr \
  --extension-type Microsoft.Dapr
```

**Generic (Helm)**:
```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --wait
```

**Acceptance Criteria**:
- [ ] Dapr running on cloud
- [ ] All components healthy

---

#### T-C07: Deploy Cloud Dapr Components
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-C05, T-C06

**Description**: Apply Dapr components with cloud Kafka config.

**Files to Create**:
- `helm-chart/dapr-components/cloud/pubsub.yaml`

**Cloud Pub/Sub Config**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: taskpubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      secretKeyRef:
        name: kafka-secrets
        key: brokers
    - name: consumerGroup
      value: "todo-app-consumer"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: tls
      value: "true"
```

**Acceptance Criteria**:
- [ ] Components applied
- [ ] Dapr connects to Redpanda

---

### C4. CI/CD Pipeline

#### T-C08: Create GitHub Actions Workflow
**Priority**: Critical
**Estimated Complexity**: High
**Dependencies**: T-C03

**Description**: Create CI/CD pipeline for automated deployments.

**Files to Create**:
- `.github/workflows/deploy.yml`

**Workflow**:
```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: todoappacr.azurecr.io
  FRONTEND_IMAGE: todo-frontend
  BACKEND_IMAGE: todo-backend

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 9

      - name: Build Frontend
        run: |
          cd frontend
          pnpm install --frozen-lockfile
          pnpm build
          pnpm test

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install uv
        run: pip install uv

      - name: Build Backend
        run: |
          cd backend
          uv sync
          uv run pytest

  docker:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Login to ACR
        uses: azure/docker-login@v1
        with:
          login-server: ${{ env.REGISTRY }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and Push Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:latest

      - name: Build and Push Backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:latest

  deploy-staging:
    needs: docker
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Get AKS Credentials
        run: |
          az aks get-credentials \
            --resource-group todo-app-rg \
            --name todo-app-aks

      - name: Deploy to Staging
        run: |
          helm upgrade --install todo-app ./helm-chart/todo-app \
            --namespace staging \
            --create-namespace \
            --set frontend.image.repository=${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }} \
            --set frontend.image.tag=${{ github.sha }} \
            --set backend.image.repository=${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }} \
            --set backend.image.tag=${{ github.sha }} \
            --set dapr.enabled=true \
            --wait

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Get AKS Credentials
        run: |
          az aks get-credentials \
            --resource-group todo-app-rg \
            --name todo-app-aks

      - name: Deploy to Production
        run: |
          helm upgrade --install todo-app ./helm-chart/todo-app \
            --namespace production \
            --create-namespace \
            --set frontend.image.repository=${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }} \
            --set frontend.image.tag=${{ github.sha }} \
            --set backend.image.repository=${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }} \
            --set backend.image.tag=${{ github.sha }} \
            --set dapr.enabled=true \
            --wait
```

**Acceptance Criteria**:
- [ ] Build stage passes
- [ ] Docker images pushed
- [ ] Staging deployment works
- [ ] Production deployment (with approval) works

---

#### T-C09: Configure GitHub Secrets
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-C08

**Description**: Add required secrets to GitHub repository.

**Secrets Required**:
- `AZURE_CREDENTIALS` - Service principal JSON
- `ACR_USERNAME` - Registry username
- `ACR_PASSWORD` - Registry password

**Commands to Create Service Principal**:
```bash
az ad sp create-for-rbac \
  --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/todo-app-rg \
  --sdk-auth
```

**Acceptance Criteria**:
- [ ] All secrets added
- [ ] CI/CD can authenticate

---

#### T-C10: Configure GitHub Environments
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-C09

**Description**: Set up staging and production environments.

**Steps**:
1. Go to Repository Settings → Environments
2. Create "staging" environment
3. Create "production" environment with:
   - Required reviewers
   - Wait timer (optional)

**Acceptance Criteria**:
- [ ] Staging environment created
- [ ] Production environment with approval

---

### C5. Production Deployment

#### T-C11: Create Kubernetes Secrets in Cloud
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: T-C05

**Description**: Create all application secrets in cloud cluster.

**Commands**:
```bash
# Database secret
kubectl create secret generic db-secrets \
  --namespace production \
  --from-literal=database-url='<neon-connection-string>'

# Auth secret
kubectl create secret generic auth-secrets \
  --namespace production \
  --from-literal=better-auth-secret='<secret>' \
  --from-literal=better-auth-url='https://todo-app.example.com'

# OpenAI secret
kubectl create secret generic openai-secrets \
  --namespace production \
  --from-literal=openai-api-key='<api-key>'

# Repeat for staging namespace
```

**Acceptance Criteria**:
- [ ] All secrets in staging
- [ ] All secrets in production

---

#### T-C12: Deploy Application to Production
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-C07, T-C08, T-C11

**Description**: Initial production deployment.

**Steps**:
1. Push to main branch
2. Wait for CI/CD to complete staging
3. Approve production deployment
4. Verify application

**Verification**:
```bash
# Check pods
kubectl get pods -n production

# Check services
kubectl get svc -n production

# Check Dapr
dapr status -k

# Test application
curl https://todo-app.example.com/health
```

**Acceptance Criteria**:
- [ ] All pods running
- [ ] Application accessible
- [ ] Dapr sidecars healthy
- [ ] Kafka events flowing

---

### C6. Observability

#### T-C13: Configure Logging
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-C12

**Description**: Set up log aggregation for cloud deployment.

**Azure**: Use Azure Monitor (enabled during cluster creation)

**Verification**:
```bash
# View logs in Azure Portal or:
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "ContainerLog | take 100"
```

**Acceptance Criteria**:
- [ ] Logs accessible
- [ ] Structured logging visible

---

#### T-C14: Configure Metrics and Alerts
**Priority**: Medium
**Estimated Complexity**: Medium
**Dependencies**: T-C13

**Description**: Set up metrics collection and alerting.

**Azure Monitor Alerts**:
- Pod restart count > 3
- CPU usage > 80%
- Memory usage > 80%
- HTTP 5xx error rate > 5%

**Acceptance Criteria**:
- [ ] Metrics visible
- [ ] Alerts configured

---

---

## Part D: Documentation

#### T-D01: Update Architecture Documentation
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-C12

**Description**: Document final architecture with diagrams.

**Files to Create**:
- `docs/architecture.md` - System architecture
- `docs/event-flow.md` - Event-driven flow diagrams

**Acceptance Criteria**:
- [ ] Architecture diagram accurate
- [ ] Event flow documented

---

#### T-D02: Create Kafka Topics Documentation
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-A16

**Description**: Document Kafka topics, schemas, and retention.

**Files to Create**:
- `docs/kafka-topics.md`

**Content**:
- Topic list with descriptions
- Event schemas (JSON)
- Producer/consumer documentation
- Retention policies

**Acceptance Criteria**:
- [ ] All topics documented
- [ ] Schemas complete

---

#### T-D03: Create Dapr Setup Guide
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-B10

**Description**: Document Dapr installation and configuration.

**Files to Create**:
- `docs/dapr-setup.md`

**Content**:
- Installation steps
- Component configurations
- Troubleshooting

**Acceptance Criteria**:
- [ ] Local setup documented
- [ ] Cloud setup documented

---

#### T-D04: Create CI/CD Documentation
**Priority**: High
**Estimated Complexity**: Low
**Dependencies**: T-C08

**Description**: Document CI/CD pipeline and deployment process.

**Files to Create**:
- `docs/cicd.md`

**Content**:
- Pipeline stages
- Required secrets
- Deployment process
- Rollback procedures

**Acceptance Criteria**:
- [ ] Pipeline documented
- [ ] Rollback instructions

---

#### T-D05: Update README
**Priority**: Critical
**Estimated Complexity**: Low
**Dependencies**: All tasks

**Description**: Update main README with Phase V information.

**Updates**:
- New features list
- Cloud deployment instructions
- Environment variables
- Quick start guide

**Acceptance Criteria**:
- [ ] README comprehensive
- [ ] All features documented

---

#### T-D06: Record Demo Video
**Priority**: Critical
**Estimated Complexity**: Medium
**Dependencies**: T-C12

**Description**: Create 90-second demo video showcasing Phase V.

**Video Content**:
- Show cloud deployment (AKS cluster)
- Demonstrate advanced feature (recurring task)
- Show Kafka events (via logs or dashboard)
- Demonstrate Dapr integration

**Acceptance Criteria**:
- [ ] Under 90 seconds
- [ ] All required elements shown
- [ ] Clear narration/captions

---

## Task Summary

| Part | Total Tasks | Critical | High | Medium |
|------|-------------|----------|------|--------|
| A: Advanced Features | 22 | 8 | 10 | 4 |
| B: Local Dapr | 11 | 8 | 3 | 0 |
| C: Cloud Deployment | 14 | 10 | 2 | 2 |
| D: Documentation | 6 | 2 | 4 | 0 |
| **Total** | **53** | **28** | **19** | **6** |

---

## Recommended Execution Order

### Week 1: Part A (Advanced Features)
1. T-A01 → T-A02 → T-A03 (Database + Models)
2. T-A04 → T-A05 (API updates)
3. T-A07 → T-A08 → T-A09 → T-A10 (Frontend components)
4. T-A11 → T-A12 → T-A13 → T-A14 → T-A15 (Integration)
5. T-A06 (Recurring logic)
6. T-A16 → T-A17 → T-A18 → T-A19 → T-A20 (Events)
7. T-A21 → T-A22 (Testing)

### Week 2: Part B + C (Deployment)
1. T-B01 → T-B02 → T-B03 → T-B04 → T-B05 (Minikube + Kafka)
2. T-B06 → T-B07 → T-B08 → T-B09 → T-B10 → T-B11 (Dapr local)
3. T-C01 → T-C02 → T-C03 (Cloud infra)
4. T-C04 → T-C05 → T-C06 → T-C07 (Cloud Kafka + Dapr)
5. T-C08 → T-C09 → T-C10 (CI/CD)
6. T-C11 → T-C12 → T-C13 → T-C14 (Production)

### Final: Documentation
1. T-D01 → T-D02 → T-D03 → T-D04 → T-D05 → T-D06

---

**Status**: Tasks Defined - Ready for Implementation
**Approver**: Development Team
**Date**: 2026-01-14
