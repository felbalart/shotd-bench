import argparse
import json
import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from math import comb
from typing import List

from dotenv import load_dotenv

load_dotenv()

from shotd_bench.rollout import run_rollout
from shotd_bench.tasks import TASKS
from shotd_bench.types import RunResult


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the photography benchmark")
    parser.add_argument("--model", default="claude-opus-5-5", help="The agent model")
    parser.add_argument("--model-provider", default="anthropic")
    parser.add_argument("--user-model", default="claude-sonnet-5-5", help="The user simulator model")
    parser.add_argument("--user-model-provider", default="anthropic")
    parser.add_argument("--judge-model", default="claude-opus-5-5", help="The model that grades plans")
    parser.add_argument("--judge-model-provider", default="anthropic")
    parser.add_argument("--task-ids", type=int, nargs="+", help="Indexes into TASKS to run (default: all)")
    parser.add_argument("--num-trials", type=int, default=1)
    parser.add_argument("--max-concurrency", type=int, default=1, help="Number of tasks to run in parallel")
    parser.add_argument("--log-dir", default="results")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    idxs = args.task_ids or list(range(len(TASKS)))
    os.makedirs(args.log_dir, exist_ok=True)
    time_str = datetime.now().strftime("%m%d%H%M%S")
    out_path = f"{args.log_dir}/{args.model.split('/')[-1]}_user-{args.user_model}_{time_str}.json"
    print(f"Running tasks {idxs} x {args.num_trials} trial(s)")

    def _run(job: tuple[int, int]) -> RunResult:
        trial, idx = job
        print(f"Running task {idx} ({TASKS[idx].task_id})")
        try:
            res = run_rollout(
                task=TASKS[idx],
                model=args.model,
                provider=args.model_provider,
                user_model=args.user_model,
                user_provider=args.user_model_provider,
                judge_model=args.judge_model,
                judge_provider=args.judge_model_provider,
            )
            result = RunResult(task_index=idx, trial=trial, **res)
        except Exception as e:
            result = RunResult(
                task_index=idx,
                trial=trial,
                reward=0.0,
                info={"error": str(e), "traceback": traceback.format_exc()},
                traj=[],
            )
        status = "✅" if result.reward == 1 else "❌"
        print(status, f"task {idx} ({TASKS[idx].task_id})", result.info.get("error", ""))
        for verdict in result.info.get("judge", {}).get("elements", []):
            print("   ", "✔" if verdict["passed"] else "✘", verdict["element"], "—", verdict["reason"])
        return result

    jobs = [(trial, idx) for trial in range(args.num_trials) for idx in idxs]
    with ThreadPoolExecutor(max_workers=args.max_concurrency) as executor:
        results = list(executor.map(_run, jobs))

    display_metrics(results)
    with open(out_path, "w") as f:
        json.dump([r.model_dump() for r in results], f, indent=2)
    print(f"\n📄 Results saved to {out_path}")


def display_metrics(results: List[RunResult]) -> None:
    num_trials = len({r.trial for r in results})
    print(f"\n🏆 Average reward: {sum(r.reward for r in results) / len(results)}")
    # Pass^k from https://arxiv.org/abs/2406.12045
    successes: dict[int, int] = {}
    for r in results:
        successes[r.task_index] = successes.get(r.task_index, 0) + (r.reward == 1)
    print("📈 Pass^k")
    for k in range(1, num_trials + 1):
        pass_k = sum(comb(c, k) / comb(num_trials, k) for c in successes.values()) / len(successes)
        print(f"  k={k}: {pass_k}")


if __name__ == "__main__":
    main()
