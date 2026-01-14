# Kafka Topics Documentation

## Overview

The Todo application uses Apache Kafka for event-driven communication between services. Events are published via Dapr's pub/sub component and consumed by event handler endpoints.

## Topics

### 1. task-events

**Purpose**: Track all task lifecycle events for analytics, logging, and audit trail.

| Property | Value |
|----------|-------|
| Partitions | 3 |
| Replication Factor | 1 (local) / 3 (cloud) |
| Retention | 7 days |
| Cleanup Policy | delete |

**Event Types**:

```json
// task.created
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "todo-app/backend",
  "id": "uuid-v4",
  "time": "2025-01-14T12:00:00Z",
  "data": {
    "task_id": 123,
    "user_id": "user_abc123",
    "title": "Complete project",
    "description": "Finish the todo app",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_date": "2025-01-20T18:00:00Z"
  }
}

// task.updated
{
  "specversion": "1.0",
  "type": "task.updated",
  "source": "todo-app/backend",
  "id": "uuid-v4",
  "time": "2025-01-14T14:00:00Z",
  "data": {
    "task_id": 123,
    "user_id": "user_abc123",
    "changes": {
      "title": "Complete project v2",
      "priority": "urgent"
    }
  }
}

// task.completed
{
  "specversion": "1.0",
  "type": "task.completed",
  "source": "todo-app/backend",
  "id": "uuid-v4",
  "time": "2025-01-14T16:00:00Z",
  "data": {
    "task_id": 123,
    "user_id": "user_abc123",
    "completed": true
  }
}

// task.uncompleted
{
  "specversion": "1.0",
  "type": "task.uncompleted",
  "source": "todo-app/backend",
  "id": "uuid-v4",
  "time": "2025-01-14T17:00:00Z",
  "data": {
    "task_id": 123,
    "user_id": "user_abc123",
    "completed": false
  }
}

// task.deleted
{
  "specversion": "1.0",
  "type": "task.deleted",
  "source": "todo-app/backend",
  "id": "uuid-v4",
  "time": "2025-01-14T18:00:00Z",
  "data": {
    "task_id": 123,
    "user_id": "user_abc123"
  }
}
```

**Consumer**: `/api/v1/events/tasks`

---

### 2. reminders

**Purpose**: Handle task reminders for due dates and overdue notifications.

| Property | Value |
|----------|-------|
| Partitions | 1 |
| Replication Factor | 1 (local) / 3 (cloud) |
| Retention | 24 hours |
| Cleanup Policy | delete |

**Event Types**:

```json
// reminder.due_soon
{
  "specversion": "1.0",
  "type": "reminder.due_soon",
  "source": "todo-app/backend",
  "id": "uuid-v4",
  "time": "2025-01-14T08:00:00Z",
  "data": {
    "task_id": 123,
    "user_id": "user_abc123",
    "title": "Complete project",
    "due_date": "2025-01-14T18:00:00Z"
  }
}

// reminder.overdue
{
  "specversion": "1.0",
  "type": "reminder.overdue",
  "source": "todo-app/backend",
  "id": "uuid-v4",
  "time": "2025-01-15T09:00:00Z",
  "data": {
    "task_id": 123,
    "user_id": "user_abc123",
    "title": "Complete project",
    "due_date": "2025-01-14T18:00:00Z"
  }
}
```

**Consumer**: `/api/v1/events/reminders`

---

### 3. task-updates

**Purpose**: Real-time synchronization events for multi-device/multi-tab support.

| Property | Value |
|----------|-------|
| Partitions | 3 |
| Replication Factor | 1 (local) / 3 (cloud) |
| Retention | 1 hour |
| Cleanup Policy | delete |

**Event Types**:

```json
// task.sync
{
  "event_type": "task.sync",
  "user_id": "user_abc123",
  "action": "create",  // create, update, delete, complete
  "task_id": 123,
  "task_data": {
    "id": 123,
    "title": "New task",
    "completed": false
  },
  "timestamp": "2025-01-14T12:00:00Z"
}
```

**Consumer**: `/api/v1/events/task-updates`

---

## Event Schema (CloudEvents)

All events follow the [CloudEvents specification](https://cloudevents.io/):

```json
{
  "specversion": "1.0",
  "type": "event.type.name",
  "source": "todo-app/backend",
  "id": "unique-event-id",
  "time": "RFC3339-timestamp",
  "datacontenttype": "application/json",
  "data": {
    // Event-specific payload
  }
}
```

## Dapr Configuration

### Pub/Sub Component (Local)

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

### Subscriptions

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: taskpubsub
  topic: task-events
  route: /api/v1/events/tasks
  scopes:
    - backend
```

## Publishing Events

Events are published from the backend service using the EventProducer class:

```python
from src.events.producer import event_producer

# Publish task created event
await event_producer.publish_task_created(
    task_id=task.id,
    user_id=user_id,
    data=task_data.model_dump()
)
```

## Consuming Events

Events are consumed via HTTP endpoints that Dapr calls:

```python
@router.post("/tasks")
async def handle_task_event(request: Request) -> dict[str, str]:
    event = await request.json()
    event_type = event.get("type", "unknown")

    # Process event based on type
    if event_type == "task.created":
        # Handle task creation
        pass

    return {"status": "ok"}
```

## Monitoring Kafka

### View Topics

```bash
kubectl get kafkatopics -n kafka
```

### Consume Messages (Debug)

```bash
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

### Topic Statistics

```bash
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe --topic task-events
```
