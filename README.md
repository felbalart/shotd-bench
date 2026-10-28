# shotd-bench

A benchmark for photography guidance agents. The agent acts as a professional photography consultant and helps a simulated user plan how to take a specific photo with their phone. It works from the user's request, a reference photo of the result they want, and a photo of where the user is now.

The tasks come from [shotdirector-benchmark](https://github.com/felbalart/shotdirector-benchmark). The conversation loop is adapted from [τ-bench](https://github.com/sierra-research/tau-bench).

## How it works

1. The simulated user states their goal. The reference photo and the scene photo are attached to their first message. The user simulator sees the same photos, so it can answer questions about its own scene.
2. The agent can ask the user questions, then calls the `submit_photography_plan` tool. The plan covers framing and composition, lighting, background, subject and pose, camera settings, and ordered steps. Submitting the plan ends the conversation.
3. An LLM judge sees the goal, both photos and the plan, and decides pass or fail for each of the task's required plan elements. The reward is 1 only if every element passes. The element score, the fraction of elements that passed, is reported too. If the agent never submits a plan, both are 0.

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
python run.py --task-ids 1
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

Each subfolder of [`tasks_media/`](tasks_media) is one task, and [`shotd_bench/tasks.py`](shotd_bench/tasks.py) loads them all, sorted by folder name. A task folder contains:

- `ground_truth*.json`: the target constraints of the reference photo (goal, framing, arrangement, camera, lighting, environment, and each subject's position, pose and expression). Each constraint has a `value` and a `status`.
- `initial.*`: the photo the user just took of their scene.
- `reference.*`: the photo the user wants theirs to look like.

Other files in the folder are ignored.

From the JSON, `tasks.py` derives:

- **The required plan elements:** one per constraint and one per subject, skipping any with `status: "unknown"`, plus "Feasible actions based on the observed scene".
- **The user simulator's instruction:** a fixed template filled in with the goal.

`--task-ids` takes positions in this sorted list. To add a task, add a folder; no code changes are needed.

Local images are sent to the models inline as base64, so each one must be under the provider's size limit (5 MB for Anthropic). Result files store image paths, not image data.

## Code

| File | Contents |
| --- | --- |
| [`run.py`](run.py) | Command line interface, parallel runs and metrics |
| [`shotd_bench/rollout.py`](shotd_bench/rollout.py) | The agent loop for one task |
| [`shotd_bench/user.py`](shotd_bench/user.py) | The LLM user simulator |
| [`shotd_bench/judge.py`](shotd_bench/judge.py) | The LLM judge |
| [`shotd_bench/tools.py`](shotd_bench/tools.py) | The `submit_photography_plan` tool schema |
| [`shotd_bench/policy.md`](shotd_bench/policy.md) | The agent's system prompt |
| [`shotd_bench/tasks.py`](shotd_bench/tasks.py) | Loads tasks from `tasks_media/` |
| [`shotd_bench/types.py`](shotd_bench/types.py) | Task and result types |

## License

MIT. See [`LICENSE`](LICENSE). Based on τ-bench ([Yao et al., 2024](https://arxiv.org/abs/2406.12045)).
