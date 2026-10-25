# DRAFT tasks written from the one-line descriptions in shotdirector-benchmark/task_definition/c02-c05.md.
# They are not loaded by any split: they have no photos yet, and the scenes below are placeholders.
# To use one, add its reference_image_url and scene_image_url, rewrite the instruction and ground truth
# to match what the scene photo actually shows, and move it into tasks_test.py.

from tau_bench.envs.photography.task import PhotographyTask

TASKS_DRAFT = [
    # c02: physical obstacles make the desired shot difficult
    PhotographyTask(
        task_id="c02",
        goal_prompt="I want a photo of myself with the lake and the sunset behind me.",
        instruction=(
            "You want a waist-up photo of yourself with the lake and the sunset behind you, to share with "
            "your family. You are at a lakeside viewpoint with your phone. A metal railing and a lamppost are "
            "in the way of the view, and you cannot climb over the railing. You found a reference photo you "
            "like and just took a photo of the viewpoint. You are patient but don't know much about photography."
        ),
        reference_image_url=None,
        scene_image_url=None,
        expected_state={
            "composition": {
                "shot_type": "waist_up_portrait_with_scenery",
                "obstacles": "railing_and_lamppost_not_blocking_subject_or_view",
            },
            "lighting": {"goal": "subject_face_visible_against_bright_sunset"},
            "background": {"goal": "lake_and_sunset_clearly_visible"},
        },
        required_plan_elements=[
            "Identifies the obstacles that block the shot",
            "A camera position or angle that keeps the obstacles out of the frame or minimizes them",
            "A subject position that keeps both the person and the sunset visible",
            "Handles the backlighting so the subject's face is visible",
            "Does not require crossing the railing or other infeasible actions",
        ],
        constraints=[
            "The user cannot climb over the railing.",
            "The plan must respect the physical conditions visible in the scene.",
        ],
    ),
    # c03: vague idea, developed through multi-turn clarification. The agent should guide the user to
    # take and share a scene photo. Needs env support for the user sharing a photo mid-conversation;
    # today the env attaches photos only to the first message.
    PhotographyTask(
        task_id="c03",
        goal_prompt="I want a cool photo of myself for my profile but I'm not sure what.",
        instruction=(
            "You want a nice photo of yourself for your social media profile, but you have no clear idea of "
            "the style. When asked, you prefer something relaxed and natural rather than formal. You are at "
            "home with your phone and have not taken any photo yet. Only share details about your room if the "
            "consultant asks for them."
        ),
        reference_image_url=None,
        scene_image_url=None,
        expected_state={
            "clarified_intent": "relaxed_natural_profile_photo",
            "composition": {"shot_type": "head_and_shoulders_or_half_body"},
            "lighting": {"goal": "soft_flattering_light_on_face"},
            "background": {"goal": "uncluttered_and_casual"},
        },
        required_plan_elements=[
            "Asks clarifying questions to establish the style and purpose before planning",
            "Asks the user for a photo or description of the scene before giving scene-specific advice",
            "A plan that matches the relaxed, natural style the user chose",
            "Suitable lighting for the face",
            "Feasible actions based on the scene the user described or showed",
        ],
        constraints=[
            "The agent must not invent details of the scene before the user provides them.",
        ],
    ),
    # c04: multiple subjects (a group of four)
    PhotographyTask(
        task_id="c04",
        goal_prompt="I want a nice photo of me and my three friends.",
        instruction=(
            "You want a nice photo of yourself and three friends to remember your trip. You are all in a "
            "park in the afternoon and will use your phone. One of the friends is much taller than the others. "
            "You would like everyone to be in the photo, including you. You found a reference group photo you "
            "like and just took a photo of the spot."
        ),
        reference_image_url=None,
        scene_image_url=None,
        expected_state={
            "composition": {
                "shot_type": "group_of_four_full_or_three_quarter",
                "subject_visibility": "all_four_faces_clearly_visible",
                "arrangement": "balanced_heights",
            },
            "lighting": {"goal": "even_light_on_all_faces_without_harsh_shadows"},
            "background": {"goal": "clean_and_non_distracting"},
        },
        required_plan_elements=[
            "An arrangement of the four people that keeps every face visible and balances their heights",
            "Framing that fits the whole group without cutting anyone off",
            "Lighting that is even across all faces",
            "A way to include the user in the photo (for example a timer and a stable support)",
            "Feasible actions based on the observed scene",
        ],
        constraints=[
            "Everyone, including the user, should be in the photo.",
            "The plan must respect the physical conditions visible in the scene.",
        ],
    ),
    # c05: competing goals and constraints; prioritize the user's primary intent
    PhotographyTask(
        task_id="c05",
        goal_prompt="I want a photo of me with the whole city skyline at night, and my face has to look good.",
        instruction=(
            "You want a photo of yourself on a rooftop at night with the city skyline behind you. Your main "
            "priority is that your face looks good and sharp, because the photo is for your dating profile; "
            "fitting the entire skyline is a nice-to-have. You only have your phone, no tripod, and a friend "
            "can hold the phone. You found a reference photo you like and just took a photo of the rooftop."
        ),
        reference_image_url=None,
        scene_image_url=None,
        expected_state={
            "primary_goal": "flattering_sharp_face",
            "secondary_goal": "skyline_visible_even_if_partial",
            "lighting": {"goal": "face_lit_well_against_dark_background"},
            "composition": {"shot_type": "half_body_portrait_with_skyline"},
        },
        required_plan_elements=[
            "Recognizes the conflict between a sharp, well-lit face and fitting the whole skyline at night",
            "Prioritizes the face, as the user's primary goal",
            "A practical way to light the face at night with what is available",
            "Handholding technique or settings that keep the photo sharp without a tripod",
            "Feasible actions based on the observed scene",
        ],
        constraints=[
            "No tripod is available.",
            "The plan must respect the physical conditions visible in the scene.",
        ],
    ),
]
