from typing import Any, Dict, List, Optional

from tau_bench.types import Action, Task


class PhotographyTask(Task):
    # Photography tasks are graded by an LLM judge, not by replaying actions
    user_id: str = "photography_user"
    actions: List[Action] = []
    outputs: List[str] = []

    task_id: str
    goal_prompt: str
    reference_image_url: Optional[str] = None
    scene_image_url: Optional[str] = None
    # Evaluator-only ground truth: never shown to the agent or the user
    expected_state: Dict[str, Any] = {}
    required_plan_elements: List[str]
    constraints: List[str] = []
