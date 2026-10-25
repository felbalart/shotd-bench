SUBMIT_PLAN = "submit_photography_plan"

SUBMIT_PLAN_TOOL = {
    "type": "function",
    "function": {
        "name": SUBMIT_PLAN,
        "description": (
            "Submit the final photography plan for the user. This ends the conversation, "
            "so only call it once you have enough information and the plan is complete."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "framing_and_composition": {
                    "type": "string",
                    "description": "Shot type, framing, camera position, height and angle, and orientation.",
                },
                "lighting": {
                    "type": "string",
                    "description": "How to use or adjust the available light sources.",
                },
                "background": {
                    "type": "string",
                    "description": "What the background should look like and what to move, remove or avoid.",
                },
                "subject_and_pose": {
                    "type": "string",
                    "description": "Subject placement, pose, expression and clothing, if there is a subject.",
                },
                "camera_settings": {
                    "type": "string",
                    "description": "Phone camera mode and settings, such as portrait mode, zoom, focus or exposure.",
                },
                "steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Ordered, actionable steps the user should follow to set up and take the photo.",
                },
            },
            "required": ["framing_and_composition", "lighting", "background", "steps"],
        },
    },
}
