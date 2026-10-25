# shotd-bench

A benchmark for photography guidance agents. The agent acts as a professional photography consultant and helps a simulated user plan how to take a specific photo with their phone. It works from the user's request, a reference photo of the result they want, and a photo of where the user is now.

The tasks come from [shotdirector-benchmark](https://github.com/felbalart/shotdirector-benchmark). The conversation loop is adapted from [τ-bench](https://github.com/sierra-research/tau-bench).

## How it works

1. The simulated user states their goal. The reference photo and the scene photo are attached to their first message. The user simulator sees the same photos, so it can answer questions about its own scene.
2. The agent can ask the user questions, then calls the `submit_photography_plan` tool. The plan covers framing and composition, lighting, background, subject and pose, camera settings, and ordered steps. Submitting the plan ends the conversation.
3. An LLM judge sees the goal, both photos, the task's ground truth and the plan, and decides pass or fail for each of the task's required plan elements. The reward is 1 only if every element passes. If the agent never submits a plan, the reward is 0.

## Setup

```bash
git clone https://github.com/felbalart/shotd-bench && cd shotd-bench
pip install -r requirements.txt
```

Create a `.env` file with your API key. `run.py` loads it automatically, and it is gitignored.

```bash
ANTHROPIC_API_KEY=...
```

## Run

```bash
python run.py --task-ids 0
```

By default, Claude Opus 5.5 (`claude-opus-5-5`) is the agent and the judge, and Claude Sonnet 5.5 (`claude-sonnet-5-5`) is the user simulator. Any model and provider that [litellm](https://docs.litellm.ai/docs/providers) supports can be used instead. It must accept images.

| Flag | Default | Description |
| --- | --- | --- |
| `--model`, `--model-provider` | `claude-opus-5-5`, `anthropic` | The agent model |
| `--user-model`, `--user-model-provider` | `claude-sonnet-5-5`, `anthropic` | The user simulator model |
| `--judge-model`, `--judge-model-provider` | `claude-opus-5-5`, `anthropic` | The model that grades plans |
| `--task-ids` | all tasks | Positions in `TASKS` to run, such as `0 2` |
| `--num-trials` | `1` | Runs per task; Pass^k is reported for k up to this number |
| `--max-concurrency` | `1` | Number of tasks to run in parallel |
| `--log-dir` | `results` | Where result files are saved |

The terminal shows each task's judge verdicts. The results file holds each task's full conversation, plan, verdicts and costs.

## Tasks

| Index | ID | Status | Description |
| --- | --- | --- | --- |
| 0 | c01 | Runnable | Professional LinkedIn headshot in a living room at night |
| – | c02–c05 | Draft | Written from short descriptions; they need photos and a review |

Runnable tasks are in [`shotd_bench/tasks.py`](shotd_bench/tasks.py). Drafts are in [`shotd_bench/tasks_draft.py`](shotd_bench/tasks_draft.py) and are not run.

To add a task, append a `Task` to `TASKS` with:

- `task_id`, `goal_prompt` and `instruction` (the persona and goal given to the user simulator)
- `reference_image_url` and `scene_image_url` (public image URLs)
- `expected_state`, `required_plan_elements` and `constraints` (ground truth seen only by the judge)

Photos can only be shared with the user's first message, so tasks where the agent asks the user to take a new photo partway through aren't supported yet.

## Code

| File | Contents |
| --- | --- |
| [`run.py`](run.py) | Command line interface, parallel runs and metrics |
| [`shotd_bench/rollout.py`](shotd_bench/rollout.py) | The agent loop for one task |
| [`shotd_bench/user.py`](shotd_bench/user.py) | The LLM user simulator |
| [`shotd_bench/judge.py`](shotd_bench/judge.py) | The LLM judge |
| [`shotd_bench/tools.py`](shotd_bench/tools.py) | The `submit_photography_plan` tool schema |
| [`shotd_bench/policy.md`](shotd_bench/policy.md) | The agent's system prompt |
| [`shotd_bench/types.py`](shotd_bench/types.py) | Task and result types |

## License

MIT. See [`LICENSE`](LICENSE). Based on τ-bench ([Yao et al., 2024](https://arxiv.org/abs/2406.12045)).
