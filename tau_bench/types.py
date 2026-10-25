# Copyright Sierra

from pydantic import BaseModel, SerializeAsAny
from typing import List, Dict, Any, Optional, Union

RESPOND_ACTION_NAME = "respond"
RESPOND_ACTION_FIELD_NAME = "content"


class Action(BaseModel):
    name: str
    kwargs: Dict[str, Any]


class Task(BaseModel):
    user_id: str
    actions: List[Action]
    instruction: str
    outputs: List[str]


class RewardOutputInfo(BaseModel):
    r_outputs: float
    outputs: Dict[str, bool]


class RewardActionInfo(BaseModel):
    r_actions: float
    gt_data_hash: str


class ElementVerdict(BaseModel):
    element: str
    passed: bool
    reason: str


class RewardJudgeInfo(BaseModel):
    r_judge: float
    elements: List[ElementVerdict]
    judge_cost: Optional[float] = None


class RewardResult(BaseModel):
    reward: float
    info: Union[RewardOutputInfo, RewardActionInfo, RewardJudgeInfo]
    actions: List[Action]


class SolveResult(BaseModel):
    reward: float
    messages: List[Dict[str, Any]]
    info: Dict[str, Any]
    total_cost: Optional[float] = None


class EnvInfo(BaseModel):
    # SerializeAsAny keeps fields of Task subclasses (e.g. PhotographyTask) in results
    task: SerializeAsAny[Task]
    source: Optional[str] = None
    user_cost: Optional[float] = None
    reward_info: Optional[RewardResult] = None


class EnvResponse(BaseModel):
    observation: str
    reward: float
    done: bool
    info: EnvInfo


class EnvResetResponse(BaseModel):
    # A list of content parts (text and image_url) for multimodal environments
    observation: Union[str, List[Dict[str, Any]]]
    info: EnvInfo


class EnvRunResult(BaseModel):
    task_id: int
    reward: float
    info: Dict[str, Any]
    traj: List[Dict[str, Any]]
    trial: int


class RunConfig(BaseModel):
    model_provider: str
    user_model_provider: str
    model: str
    user_model: str = "gpt-4o"
    num_trials: int = 1
    env: str = "retail"
    agent_strategy: str = "tool-calling"
    temperature: float = 0.0
    task_split: str = "test"
    start_index: int = 0
    end_index: int = -1
    task_ids: Optional[List[int]] = None
    log_dir: str = "results"
    max_concurrency: int = 1
    seed: int = 10
    shuffle: int = 0
    user_strategy: str = "llm"
    few_shot_displays_path: Optional[str] = None
    judge_model: Optional[str] = None
    judge_model_provider: Optional[str] = None
