from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Task(BaseModel):
    task_id: str
    goal_prompt: str
    # Persona and goal given to the user simulator
    instruction: str
    reference_image_url: Optional[str] = None
    scene_image_url: Optional[str] = None
    # Ground truth seen only by the judge
    expected_state: Dict[str, Any] = {}
    required_plan_elements: List[str]
    constraints: List[str] = []


class ElementVerdict(BaseModel):
    element: str
    passed: bool
    reason: str


class JudgeResult(BaseModel):
    reward: float
    elements: List[ElementVerdict]
    judge_cost: Optional[float] = None


class RunResult(BaseModel):
    task_index: int
    trial: int
    reward: float
    info: Dict[str, Any]
    traj: List[Dict[str, Any]]
