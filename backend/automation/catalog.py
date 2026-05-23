from dataclasses import dataclass
from typing import Dict, Iterable, List, Set


@dataclass(frozen=True)
class Capability:
    key: str
    app: str
    label: str
    kind: str
    keywords: tuple[str, ...]


CAPABILITIES: Dict[str, Capability] = {
    "forms.new_submission": Capability(
        "forms.new_submission",
        "forms",
        "New form response",
        "trigger",
        ("form", "lead", "inquiry", "submit", "booking", "webhook"),
    ),
    "schedule.daily": Capability(
        "schedule.daily",
        "schedule",
        "Daily scheduled time",
        "trigger",
        ("daily", "every evening", "every morning", "summary"),
    ),
    "gmail.new_email": Capability(
        "gmail.new_email",
        "gmail",
        "New business inquiry email",
        "trigger",
        ("gmail", "email", "inquiry", "reply"),
    ),
    "google_sheets.add_row": Capability(
        "google_sheets.add_row",
        "google_sheets",
        "Save row to Google Sheets",
        "action",
        ("sheet", "spreadsheet", "save", "lead", "sales"),
    ),
    "telegram.send_message": Capability(
        "telegram.send_message",
        "telegram",
        "Send Telegram notification",
        "action",
        ("telegram", "notify", "alert", "message me"),
    ),
    "whatsapp.send_message": Capability(
        "whatsapp.send_message",
        "whatsapp",
        "Send WhatsApp message",
        "action",
        ("whatsapp", "reminder", "customer message", "appointment"),
    ),
    "gmail.send_reply": Capability(
        "gmail.send_reply",
        "gmail",
        "Send Gmail reply",
        "action",
        ("auto reply", "reply", "gmail", "email"),
    ),
    "database.save_record": Capability(
        "database.save_record",
        "database",
        "Save record to database",
        "action",
        ("database", "save lead", "save customer", "store"),
    ),
}


SUPPORTED_APPS: Set[str] = {capability.app for capability in CAPABILITIES.values()}


def infer_capabilities(prompt: str) -> List[Capability]:
    text = prompt.lower()
    matches = [
        capability
        for capability in CAPABILITIES.values()
        if any(keyword in text for keyword in capability.keywords)
    ]

    if not any(item.kind == "trigger" for item in matches):
        matches.insert(0, CAPABILITIES["forms.new_submission"])

    if not any(item.kind == "action" for item in matches):
        matches.append(CAPABILITIES["telegram.send_message"])

    return dedupe(matches)


def dedupe(items: Iterable[Capability]) -> List[Capability]:
    seen: Set[str] = set()
    result: List[Capability] = []
    for item in items:
        if item.key not in seen:
            result.append(item)
            seen.add(item.key)
    return result

