# Tasks from https://github.com/felbalart/shotdirector-benchmark (task_definition/ and tasks/)

from tau_bench.envs.photography.task import PhotographyTask

TASKS_TEST = [
    PhotographyTask(
        task_id="c01",
        goal_prompt="I want a professional headshot for my LinkedIn.",
        instruction=(
            "You want a professional headshot for your LinkedIn profile that looks polished, "
            "approachable and suitable for a professional setting. You are at home in your living room "
            "and will take the photo with your phone. You found a reference headshot in the style you like, "
            "and you just took a photo of the room where you are. You can move yourself, the phone and the "
            "furniture around the room. You are friendly and want clear, practical instructions."
        ),
        reference_image_url="https://images.squarespace-cdn.com/content/v1/5ec689480cc22c2d441e152f/1769094966114-SC6CYMZZOQ54RLHYV680/nlalor-photography-professional-headshot-2025-westport-ct-80.jpg",
        scene_image_url="https://raw.githubusercontent.com/felbalart/shotdirector-benchmark/refs/heads/main/tasks/c01/input_resources/c01_img01.jpg",
        expected_state={
            "photography_context": "professional_linkedin_headshot",
            "composition": {
                "shot_type": "head_and_shoulders",
                "subject_visibility": "face_and_shoulders_visible",
            },
            "lighting": {"goal": "clear_and_reasonably_even_facial_lighting"},
            "background": {"goal": "clean_and_non_distracting"},
            "pose": {"goal": "composed_and_approachable"},
        },
        required_plan_elements=[
            "Appropriate framing for a professional headshot",
            "Suitable lighting for clear facial visibility",
            "A clean and non-distracting background",
            "A composed yet approachable pose",
            "Feasible actions based on the observed scene",
        ],
        constraints=[
            "The plan must respect the physical conditions visible in the scene.",
        ],
    ),
]
