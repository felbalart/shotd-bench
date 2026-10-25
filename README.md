# shotd-bench: a photography environment for τ-bench

shotd-bench is a fork of [τ-bench](https://github.com/sierra-research/tau-bench) that adds a **`photography`** environment. In it, an agent acts as a professional photography consultant. It helps a simulated user plan how to take a specific photo with their phone, using the user's request, a reference photo of the result they want, and a photo of where they are now.

The tasks come from [shotdirector-benchmark](https://github.com/felbalart/shotdirector-benchmark), a benchmark for real-time mobile phone photography guidance. The original `retail` and `airline` environments are still included.

## How the photography environment works

Each task gives the user:

- **A goal**, such as "I want a professional headshot for my LinkedIn."
- **A reference photo** showing the kind of result they want.
- **A scene photo** they just took of the place where they are.

A run goes like this:

1. The simulated user states the goal. Both photos are attached to their first message. The user simulator sees the same photos, so it can answer questions about its own scene.
2. The agent studies the photos, can ask the user questions, and then calls the `submit_photography_plan` tool. The plan covers framing and composition, lighting, background, subject and pose, camera settings, and ordered steps. Submitting the plan ends the conversation.
3. An LLM judge grades the plan. It sees the goal, both photos, the task's ground truth and the plan, and decides pass or fail for each of the task's required plan elements (for example "Suitable lighting for clear facial visibility" or "Feasible actions based on the observed scene"). The reward is 1 only if every element passes, matching τ-bench's pass/fail scoring. If the agent never submits a plan, the reward is 0.

The results file records each element's verdict and the judge's reason, along with the judge's cost.

### Tasks

| ID | Status | Description |
| --- | --- | --- |
| c01 | Runnable | Professional LinkedIn headshot in a living room at night |
| c02–c05 | Draft, not runnable | Written from short descriptions; they need photos and a review before use |

Runnable tasks are in [`tau_bench/envs/photography/tasks_test.py`](tau_bench/envs/photography/tasks_test.py). Drafts are in [`tasks_draft.py`](tau_bench/envs/photography/tasks_draft.py) and are not loaded by any run.

To add a task, append a `PhotographyTask` to `TASKS_TEST` with:

- `task_id`, `goal_prompt` and `instruction` (the persona and goal given to the user simulator)
- `reference_image_url` and `scene_image_url` (public image URLs)
- `expected_state`, `required_plan_elements` and `constraints` (ground truth seen only by the judge)

### Limitations

- Only the `tool-calling` agent strategy is supported, because the other agents can't pass images through.
- Only the `llm` and `human` user strategies are supported.
- Photos can only be shared with the user's first message, so tasks where the agent asks the user to take a new photo partway through aren't supported yet.

## Setup

1. Clone this repository:

```bash
git clone https://github.com/felbalart/shotd-bench && cd shotd-bench
```

2. Install from source, which also installs the required packages:

```bash
pip install -e .
```

3. Create a `.env` file in the repository root with the API keys for the providers you use. `run.py` loads it automatically, and it is gitignored.

```bash
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

## Run

Run the photography environment with Claude Opus 5.5 as the agent and the judge, and Claude Sonnet 5.5 as the user simulator:

```bash
python run.py --env photography --agent-strategy tool-calling \
  --model claude-opus-5-5 --model-provider anthropic \
  --user-model claude-sonnet-5-5 --user-model-provider anthropic \
  --judge-model claude-opus-5-5 --judge-model-provider anthropic \
  --user-strategy llm
```

If you leave out `--judge-model` and `--judge-model-provider`, the judge uses the user simulator's model.

Useful flags:

- `--task-ids 0 2` runs only the tasks at those positions in the task list. `--start-index` and `--end-index` select a range.
- `--max-concurrency 10` runs tasks in parallel. Set it according to your API rate limits.
- `--num-trials 4` runs each task several times and reports Pass^k.

Results are saved to `results/`, which you can change with `--log-dir`. Each file contains every task's full conversation, reward and judge verdicts.

### Retail and airline

The original environments work as in τ-bench:

```bash
python run.py --env retail --agent-strategy tool-calling \
  --model claude-opus-5-5 --model-provider anthropic \
  --user-model claude-sonnet-5-5 --user-model-provider anthropic \
  --user-strategy llm
```

They also support the `act`, `react` and `few-shot` agent strategies and the `react`, `verify` and `reflection` user strategies. See the [τ-bench README](https://github.com/sierra-research/tau-bench#readme) for details, the leaderboard and the auto error identification tool.

Note that these retail and airline tasks are outdated. Sierra maintains fixed versions in [τ³-bench](https://github.com/sierra-research/tau2-bench).

## Changes from τ-bench

Besides the photography environment, this fork:

- Doesn't send `temperature` to Anthropic models, because current Claude models reject sampling parameters.
- Loads API keys from `.env` through `python-dotenv`.
- Adds `mcp` as a dependency, which recent versions of `litellm` need.

## License

MIT, as in the original τ-bench. See [`LICENSE`](LICENSE).

## Citation

This work builds on τ-bench. If you use it, please cite the original papers:

```bibtex
@misc{yao2024tau,
      title={$\tau$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains}, 
      author={Shunyu Yao and Noah Shinn and Pedram Razavi and Karthik Narasimhan},
      year={2024},
      eprint={2406.12045},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2406.12045}, 
}
@misc{barres2025tau2,
      title={$\tau^2$-Bench: Evaluating Conversational Agents in a Dual-Control Environment}, 
      author={Victor Barres and Honghua Dong and Soham Ray and Xujie Si and Karthik Narasimhan},
      year={2025},
      eprint={2506.07982},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2506.07982}, 
}
```
