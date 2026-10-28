"""Loads tasks from tasks_media/. Each task folder holds a ground_truth*.json file,
the user's current scene photo (initial.*) and the reference photo (reference.*)."""

import glob
import json
import os
from typing import Any, Dict, List, Optional

from shotd_bench.types import Task

TASKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks_media")

INSTRUCTION = (
    "You want to take a photo like your reference photo. Your goal: {goal}. "
    "You are at the place shown in the photo you just took, and you will take the photo with your phone. "
    "You want your photo to look as much like the reference as possible. "
    "You are friendly and want clear, practical instructions."
)

# Ground truth constraints that become required plan elements, with their labels
CONSTRAINT_LABELS = {
    "goal": "Goal",
    "framing": "Framing",
    "arrangement": "Subject arrangement",
    "camera": "Camera",
    "lighting": "Lighting",
    "environment": "Environment and background",
}
SUBJECT_LABELS = {
    "position": "position in frame",
    "pose": "pose",
    "expression": "expression",
}


def known_value(constraint: Optional[Dict[str, Any]]) -> Any:
    if not constraint or constraint.get("status") == "unknown":
        return None
    return constraint.get("value")


def describe(value: Any) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{k.replace('_', ' ')} {describe(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " and ".join(describe(v) for v in value)
    return str(value).replace("_", " ")


def required_plan_elements(constraints: Dict[str, Any]) -> List[str]:
    elements = []
    for key, label in CONSTRAINT_LABELS.items():
        value = known_value(constraints.get(key))
        if value is not None:
            elements.append(f"{label}: {describe(value)}")
    for subject in constraints.get("subjects", []):
        parts = []
        for key, label in SUBJECT_LABELS.items():
            value = known_value(subject.get(key))
            if value is not None:
                parts.append(f"{label}: {describe(value)}")
        if parts:
            elements.append(f"Subject {subject['id']}: " + "; ".join(parts))
    elements.append("Feasible actions based on the observed scene")
    return elements


def find_image(folder: str, stem: str) -> Optional[str]:
    matches = sorted(glob.glob(os.path.join(folder, f"{stem}.*")))
    return matches[0] if matches else None


def load_task(folder: str) -> Task:
    (gt_path,) = glob.glob(os.path.join(folder, "ground_truth*.json"))
    with open(gt_path) as f:
        ground_truth = json.load(f)
    constraints = ground_truth["constraints"]
    goal = describe(known_value(constraints.get("goal")) or "a photo like the reference")
    return Task(
        task_id=ground_truth["task_id"],
        name=os.path.basename(folder),
        goal=goal,
        instruction=INSTRUCTION.format(goal=goal),
        reference_image=find_image(folder, "reference"),
        scene_image=find_image(folder, "initial"),
        constraints=constraints,
        required_plan_elements=required_plan_elements(constraints),
    )


TASKS = [
    load_task(folder)
    for folder in sorted(glob.glob(os.path.join(TASKS_DIR, "*")))
    if glob.glob(os.path.join(folder, "ground_truth*.json"))
]
