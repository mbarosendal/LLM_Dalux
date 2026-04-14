from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

# Extractor methods


def _extract_collection_payload(payload: object) -> tuple[list[dict], list[dict], dict]:
    """Normalize common Dalux collection envelopes into items, links, and metadata."""
    if not isinstance(payload, dict):
        return [], [], {}

    items = payload.get("items", [])
    links = payload.get("links", [])
    metadata = payload.get("metadata", {})

    normalized_items = (
        [item for item in items if isinstance(item, dict)]
        if isinstance(items, list)
        else []
    )
    normalized_links = (
        [link for link in links if isinstance(link, dict)]
        if isinstance(links, list)
        else []
    )
    normalized_metadata = metadata if isinstance(metadata, dict) else {}

    return normalized_items, normalized_links, normalized_metadata


# Normalizer methods


def _normalize_user_object(user: dict) -> dict:
    first_name = user.get("firstName", "No name")
    last_name = user.get("lastName", "")
    return {
        "userId": user.get("userId", "N/A"),
        "name": f"{first_name} {last_name}".strip(),
        "email": user.get("email", "N/A"),
        "companyId": user.get("companyId", "N/A"),
    }


def _normalize_task_object(task: dict) -> dict:
    type_info = task.get("type") or {}
    created_by = task.get("createdBy") or {}

    return {
        "taskId": task.get("taskId", "N/A"),
        "subject": task.get("subject", "No subject"),
        "typeName": type_info.get("name", "N/A"),
        "number": task.get("number", "N/A"),
        "created": convert_to_danish_time(task.get("created", "N/A")),
        "createdByUserId": created_by.get("userId", "N/A"),
    }


# Helper methods


def convert_to_danish_time(iso_timestamp: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        danish_dt = dt.astimezone(ZoneInfo("Europe/Copenhagen"))
        return danish_dt.isoformat()
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        return iso_timestamp


def infer_task_change_status(
    action: str | None,
    status: str | None,
    has_description: bool,
) -> str:
    """Infer a human-friendly task change status based on action, status, and description in data."""
    action_value = (action or "").strip().lower()
    status_value = (status or "").strip().lower()

    if action_value == "approve" and has_description:
        return "approved, with follow up"
    if action_value == "approve" and status_value == "closed":
        return "approved"
    # if action_value == "assign" and has_description: # and has fields.userdefinedfields.items.name == sikkerhedskategori?
    #     return "new"
    if action_value == "assign" and status_value == "open":
        return "ongoing"
    if action_value == "update" and has_description:
        return "ongoing"  # + ", with follow up" ?
    if action_value == "reject" and status_value == "open":
        return "rejected"
    if action_value == "complete" and status_value == "open":
        return "ready"
    # if action_value == "other" and status_value == "closed":
    #     return "archived"
    if action_value == "other" and status_value == "closed":
        return "expired"
    if status_value in {"closed", "open"}:
        return "unknown"
    return "unknown"


def _status_priority(item: dict) -> int:
    status = (item.get("status") or item.get("fields", {}).get("status") or "").lower()
    return 2 if status == "closed" else 1 if status == "open" else 0


def _find_latest_change(item: dict, task_latest: dict[str, dict]) -> None:
    task_id = item.get("taskId")
    timestamp = item.get("timestamp")

    if not task_id or not timestamp:
        return

    existing = task_latest.get(task_id)

    # First time we see this new task
    if not existing:
        task_latest[task_id] = item
        return

    old_timestamp = existing.get("timestamp")
    if not old_timestamp:
        task_latest[task_id] = item
        return

    # New item wins if timestamp is newer, or if same timestamp but higher status priority (closed > open).
    if timestamp > old_timestamp or (
        timestamp == old_timestamp
        and _status_priority(item) >= _status_priority(existing)
    ):
        task_latest[task_id] = item


# Per-tool orchestrators to build final tool responses after extracting and normalizing data


def transform_tasks_collection_payload(
    payload: object,
    project_label: str,
    bookmark: str | None = None,
) -> dict:
    # 1) Extract top-level collection envelope into items, links, and metadata
    tasks, links, metadata = _extract_collection_payload(payload)
    # 2) Normalize each task object by extracting relevant fields and flattening nested structures
    items = [_normalize_task_object(task) for task in tasks]
    page_label = " (paginated via bookmark)" if bookmark else ""
    summary = (
        f"Found {len(items)} task(s) for {project_label}{page_label}."
        if items
        else f"No tasks found for {project_label}."
    )
    # 3) Build final transformed payload with summary, normalized data, and original links/metadata
    return {
        "summary": summary,
        "data": {"items": items},
        "links": links,
        "metadata": metadata,
    }


def transform_task_payload(payload: object, task_id: str, project_label: str) -> dict:
    task = (
        _normalize_task_object(payload)
        if isinstance(payload, dict) and payload
        else None
    )
    summary = (
        f"Found task for {project_label}."
        if task
        else f"No task found for task ID {task_id} in {project_label}."
    )
    return {
        "summary": summary,
        "data": {"task": task},
    }


def transform_task_changes_collection_payload(
    payload: object, project_label: str
) -> dict:
    changes, links, _ = _extract_collection_payload(payload)
    items = []
    task_latest: dict[str, dict] = {}

    for change in changes:
        fields = change.get("fields", {}) or {}
        action = change.get("action")
        status = fields.get("status")
        description = change.get("description") or ""

        inferred = infer_task_change_status(
            action if isinstance(action, str) else None,
            status if isinstance(status, str) else None,
            bool(description),
        )

        item = {
            "taskId": change.get("taskId"),
            # "timestamp": dk,
            "timestamp": convert_to_danish_time(change.get("timestamp")),
            "action": action,
            "status": status,
            "inferredStatus": inferred,
            "description": description,
            "modifiedByUserId": (fields.get("modifiedBy") or {}).get("userId"),
            "assignedToRoleId": (fields.get("assignedTo") or {}).get("roleId"),
            "assignedToRoleName": (fields.get("assignedTo") or {}).get("roleName"),
            "currentResponsibleUserId": (fields.get("currentResponsible") or {}).get(
                "userId"
            ),
        }
        items.append(item)

        _find_latest_change(item, task_latest)

    task_summary = [
        {
            "taskId": task_id,
            "finalStatus": latest.get("inferredStatus", "unknown"),
            "latestTimestamp": latest.get("timestamp"),
            "assignedToRoleId": latest.get("assignedToRoleId"),
            "assignedToRoleName": latest.get("assignedToRoleName"),
            "currentResponsibleUserId": latest.get("currentResponsibleUserId"),
        }
        for task_id, latest in task_latest.items()
    ]

    changes_summary = (
        f"Found {len(items)} task change event(s) for {project_label}."
        if items
        else f"No task changes found for {project_label}."
    )

    return {
        "summary": changes_summary,
        "data": {"items": items, "taskSummaries": task_summary},
        "links": links,
        "metadata": {},
    }


def transform_users_collection_payload(payload: object, project_label: str) -> dict:
    users, links, metadata = _extract_collection_payload(payload)
    items = [_normalize_user_object(user) for user in users]
    summary = (
        f"Found {len(items)} user(s) for {project_label}."
        if items
        else f"No users found for {project_label}."
    )
    return {
        "summary": summary,
        "data": {"items": items},
        "links": links,
        "metadata": metadata,
    }


def transform_user_payload(payload: object, user_id: str, project_label: str) -> dict:
    user = (
        _normalize_user_object(payload)
        if isinstance(payload, dict) and payload
        else None
    )
    summary = (
        f"Found user for {project_label}."
        if user
        else f"No user found for userId {user_id} in {project_label}."
    )
    return {
        "summary": summary,
        "data": {"user": user},
    }
