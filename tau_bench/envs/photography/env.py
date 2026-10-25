import random
from typing import Any, Dict, List, Optional, Union

from tau_bench.envs.base import Env
from tau_bench.envs.photography.judge import judge_plan
from tau_bench.envs.photography.rules import RULES
from tau_bench.envs.photography.task import PhotographyTask
from tau_bench.envs.photography.tools import ALL_TOOLS
from tau_bench.envs.photography.user import PhotographyUserSimulationEnv, image_parts
from tau_bench.envs.photography.wiki import WIKI
from tau_bench.envs.user import UserStrategy
from tau_bench.types import (
    ElementVerdict,
    EnvInfo,
    EnvResetResponse,
    RewardJudgeInfo,
    RewardResult,
)

SUBMIT_PLAN_TOOL = "submit_photography_plan"


class PhotographyDomainEnv(Env):
    def __init__(
        self,
        user_strategy: Union[str, UserStrategy] = UserStrategy.LLM,
        user_model: str = "gpt-4o",
        user_provider: Optional[str] = None,
        task_split: str = "test",
        task_index: Optional[int] = None,
        judge_model: Optional[str] = None,
        judge_provider: Optional[str] = None,
    ):
        match task_split:
            case "test":
                from tau_bench.envs.photography.tasks_test import TASKS_TEST as tasks
            case _:
                raise ValueError(f"Unknown task split: {task_split}")
        user_strategy = UserStrategy(user_strategy)
        if user_strategy not in (UserStrategy.LLM, UserStrategy.HUMAN):
            raise ValueError(
                f"The photography env only supports the llm and human user strategies, not {user_strategy.value}"
            )
        super().__init__(
            data_load_func=lambda: {},
            tools=ALL_TOOLS,
            tasks=tasks,
            wiki=WIKI,
            rules=RULES,
            # Load the human user so the base class makes no LLM call; replaced below
            user_strategy=UserStrategy.HUMAN,
            user_model=user_model,
            user_provider=user_provider,
            task_index=task_index,
        )
        if user_strategy == UserStrategy.LLM:
            self.user = PhotographyUserSimulationEnv(model=user_model, provider=user_provider)
        self.terminate_tools = [SUBMIT_PLAN_TOOL]
        self.judge_model = judge_model or user_model
        self.judge_provider = judge_provider or user_provider

    def reset(self, task_index: Optional[int] = None) -> EnvResetResponse:
        if task_index is None:
            task_index = random.randrange(len(self.tasks))
        self.task_index = task_index
        self.data = self.data_load_func()
        self.task = self.tasks[task_index]
        self.actions = []
        task: PhotographyTask = self.task
        labeled_images = []
        if task.reference_image_url:
            labeled_images.append(("Reference photo of the result I want:", task.reference_image_url))
        if task.scene_image_url:
            labeled_images.append(("Photo I just took of where I am:", task.scene_image_url))
        if isinstance(self.user, PhotographyUserSimulationEnv):
            first_message = self.user.reset(
                instruction=task.instruction, labeled_images=labeled_images
            )
        else:
            urls = "".join(f"\n{label} {url}" for label, url in labeled_images)
            first_message = self.user.reset(instruction=task.instruction + urls)
        observation: Union[str, List[Dict[str, Any]]] = first_message
        if labeled_images:
            observation = [
                {"type": "text", "text": first_message},
                *image_parts(labeled_images),
            ]
        return EnvResetResponse(observation=observation, info=EnvInfo(task=task, source="user"))

    def calculate_reward(self) -> RewardResult:
        task: PhotographyTask = self.task
        plans = [a for a in self.actions if a.name == SUBMIT_PLAN_TOOL]
        if not plans:
            info = RewardJudgeInfo(
                r_judge=0.0,
                elements=[
                    ElementVerdict(element=e, passed=False, reason="No plan was submitted.")
                    for e in task.required_plan_elements
                ],
            )
        else:
            info = judge_plan(
                task=task,
                plan=plans[-1].kwargs,
                model=self.judge_model,
                provider=self.judge_provider,
            )
        return RewardResult(reward=info.r_judge, info=info, actions=[])
