import json
from typing import Any, Dict, List

from litellm import completion

from shotd_bench.types import ElementVerdict, JudgeResult, Task
from shotd_bench.user import image_parts

SYSTEM_PROMPT = """You are an expert photography judge grading a photography plan written by a consultant for a user who will take the photo with a phone.

You receive the user's goal, the photos the user shared and a list of required plan elements. Most elements are target attributes of the photo the user wants, taken from the evaluator's ground truth for the reference photo; positions in frame are approximate x, y coordinates from 0 to 1, measured from the top-left corner. For each required element, decide whether following the plan would produce a photo that matches it. An element passes only if the plan addresses it specifically and actionably, and the advice is feasible in the scene visible in the user's current photo. Vague or generic advice does not pass.

Reply with JSON only, in this format:
{"elements": [{"index": 1, "passed": true, "reason": "<one sentence>"}, ...]}
Include exactly one entry per required element, in the same order."""


def judge_plan(task: Task, plan: Dict[str, Any], model: str, provider: str) -> JudgeResult:
    elements = "\n".join(f"{i}. {e}" for i, e in enumerate(task.required_plan_elements, 1))
    labeled_images = []
    if task.reference_image:
        labeled_images.append(("Reference photo the user shared:", task.reference_image))
    if task.scene_image:
        labeled_images.append(("Photo of the user's current scene:", task.scene_image))
    content: List[Dict[str, Any]] = [
        {"type": "text", "text": f"User's goal: {task.goal}"},
        *image_parts(labeled_images),
        {
            "type": "text",
            "text": (
                f"Required plan elements:\n{elements}\n\n"
                f"Plan submitted by the consultant:\n{json.dumps(plan, indent=2)}"
            ),
        },
    ]
    res = completion(
        model=model,
        custom_llm_provider=provider,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
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
    return JudgeResult(
        reward=1.0 if all(r.passed for r in results) else 0.0,
        score=sum(r.passed for r in results) / len(results),
        elements=results,
        judge_cost=res._hidden_params["response_cost"],
    )
