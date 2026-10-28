from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Task(BaseModel):
    task_id: str
    # Name of the task's folder in tasks_media/
    name: str
    goal: str
    # Persona and goal given to the user simulator
    instruction: str
    # Image file paths or URLs
    reference_image: Optional[str] = None
    scene_image: Optional[str] = None
    # Ground truth seen only by the judge
    constraints: Dict[str, Any]
    required_plan_elements: List[str]


class ElementVerdict(BaseModel):
    element: str
    passed: bool
    reason: str


class JudgeResult(BaseModel):
    reward: float
    # Fraction of required plan elements that passed
    score: float
    elements: List[ElementVerdict]
    judge_cost: Optional[float] = None


class RunResult(BaseModel):
    task_index: int
    trial: int
    reward: float
    info: Dict[str, Any]
    traj: List[Dict[str, Any]]
