import json
from typing import Any, Dict, List

from litellm import completion

from tau_bench.envs.photography.task import PhotographyTask
from tau_bench.envs.photography.user import image_parts
from tau_bench.types import ElementVerdict, RewardJudgeInfo

JUDGE_SYSTEM_PROMPT = """You are an expert photography judge grading a photography plan written by a consultant for a user who will take the photo with a phone.

You receive the user's goal, the photos the user shared, the evaluator's ground truth and a list of required plan elements. For each required element, decide whether the plan satisfies it. An element passes only if the plan addresses it specifically and actionably, and the advice is feasible in the scene visible in the user's photo. Vague or generic advice does not pass.

Reply with JSON only, in this format:
{"elements": [{"index": 1, "passed": true, "reason": "<one sentence>"}, ...]}
Include exactly one entry per required element, in the same order."""


def judge_plan(
    task: PhotographyTask, plan: Dict[str, Any], model: str, provider: str
) -> RewardJudgeInfo:
    elements = "\n".join(
        f"{i}. {element}" for i, element in enumerate(task.required_plan_elements, 1)
    )
    labeled_images = []
    if task.reference_image_url:
        labeled_images.append(("Reference photo the user shared:", task.reference_image_url))
    if task.scene_image_url:
        labeled_images.append(("Photo of the user's current scene:", task.scene_image_url))
    content: List[Dict[str, Any]] = [
        {"type": "text", "text": f"User's goal: {task.goal_prompt}"},
        *image_parts(labeled_images),
        {
            "type": "text",
            "text": (
                f"Ground truth expected state:\n{json.dumps(task.expected_state, indent=2)}\n\n"
                f"Constraints:\n{json.dumps(task.constraints, indent=2)}\n\n"
                f"Required plan elements:\n{elements}\n\n"
                f"Plan submitted by the consultant:\n{json.dumps(plan, indent=2)}"
            ),
        },
    ]
    res = completion(
        model=model,
        custom_llm_provider=provider,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        max_tokens=16000,
    )
    text = res.choices[0].message.content
    try:
        verdicts = json.loads(text[text.index("{") : text.rindex("}") + 1])["elements"]
    except (ValueError, KeyError) as e:
        raise ValueError(f"Could not parse judge output: {text}") from e
    if len(verdicts) != len(task.required_plan_elements):
        raise ValueError(
            f"Judge returned {len(verdicts)} verdicts for {len(task.required_plan_elements)} elements: {text}"
        )
    results = [
        ElementVerdict(element=element, passed=bool(v["passed"]), reason=v["reason"])
        for element, v in zip(task.required_plan_elements, verdicts)
    ]
    return RewardJudgeInfo(
        r_judge=1.0 if all(r.passed for r in results) else 0.0,
        elements=results,
        judge_cost=res._hidden_params["response_cost"],
    )
