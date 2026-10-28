import json
import os
from typing import Any, Dict, List, Optional

from litellm import completion

from shotd_bench.judge import judge_plan
from shotd_bench.tools import SUBMIT_PLAN, SUBMIT_PLAN_TOOL
from shotd_bench.types import ElementVerdict, JudgeResult, Task
from shotd_bench.user import UserSimulator, image_parts

with open(os.path.join(os.path.dirname(__file__), "policy.md")) as f:
    POLICY = f.read()


def run_rollout(
    task: Task,
    model: str,
    provider: str,
    user_model: str,
    user_provider: str,
    judge_model: str,
    judge_provider: str,
    max_num_steps: int = 30,
) -> Dict[str, Any]:
    """Run one conversation between the agent and the simulated user, then judge the plan."""
    labeled_images = []
    if task.reference_image:
        labeled_images.append(("Reference photo of the result I want:", task.reference_image))
    if task.scene_image:
        labeled_images.append(("Photo I just took of where I am:", task.scene_image))

    user = UserSimulator(model=user_model, provider=user_provider)
    first_message = user.reset(instruction=task.instruction, labeled_images=labeled_images)
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": POLICY},
        {"role": "user", "content": [{"type": "text", "text": first_message}, *image_parts(labeled_images)]},
    ]
    agent_cost = 0.0
    plan: Optional[Dict[str, Any]] = None

    for _ in range(max_num_steps):
        res = completion(
            model=model, custom_llm_provider=provider, messages=messages, tools=[SUBMIT_PLAN_TOOL]
        )
        agent_cost += res._hidden_params["response_cost"] or 0
        message = res.choices[0].message.model_dump()
        if message.get("tool_calls"):
            # The policy allows one tool call per turn
            message["tool_calls"] = message["tool_calls"][:1]
            call = message["tool_calls"][0]
            name = call["function"]["name"]
            if name == SUBMIT_PLAN:
                plan = json.loads(call["function"]["arguments"])
                observation = "Plan submitted"
            else:
                observation = f"Unknown tool {name}"
            messages += [message, {"role": "tool", "tool_call_id": call["id"], "name": name, "content": observation}]
            if plan is not None:
                break
        else:
            reply = user.step(message["content"])
            messages += [message, {"role": "user", "content": reply}]
            if "###STOP###" in reply:
                break

    if plan is None:
        result = JudgeResult(
            reward=0.0,
            score=0.0,
            elements=[
                ElementVerdict(element=e, passed=False, reason="No plan was submitted.")
                for e in task.required_plan_elements
            ],
        )
    else:
        result = judge_plan(task=task, plan=plan, model=judge_model, provider=judge_provider)

    return {
        "reward": result.reward,
        "info": {
            "task": task.model_dump(),
            "plan": plan,
            "judge": result.model_dump(),
            "agent_cost": agent_cost,
            "user_cost": user.total_cost,
        },
        # Log image paths instead of the inlined base64 data
        "traj": [
            messages[0],
            {"role": "user", "content": [{"type": "text", "text": first_message}, *image_parts(labeled_images, inline=False)]},
            *messages[2:],
        ],
    }
