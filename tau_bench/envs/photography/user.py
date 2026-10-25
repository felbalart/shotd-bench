from typing import Any, Dict, List, Optional

from tau_bench.envs.user import LLMUserSimulationEnv


def image_parts(labeled_urls: List[tuple[str, str]]) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = []
    for label, url in labeled_urls:
        parts.append({"type": "text", "text": label})
        parts.append({"type": "image_url", "image_url": {"url": url}})
    return parts


class PhotographyUserSimulationEnv(LLMUserSimulationEnv):
    """LLM user that can see the photos it shares with the agent."""

    def build_system_prompt(self, instruction: Optional[str]) -> str:
        return (
            super().build_system_prompt(instruction)
            + """
- You are chatting with a photography consultant. Your photos are attached to your first message automatically, so never paste links or describe the photos as attachments.
- Answer questions about your scene based on what you can see in your photos. If something cannot be seen and is not in the instruction, say you are not sure.
- Do not end the conversation yourself before the consultant has given you a complete photography plan."""
        )

    def reset(
        self,
        instruction: Optional[str] = None,
        labeled_images: Optional[List[tuple[str, str]]] = None,
    ) -> str:
        greeting = "Hi! How can I help you today?"
        if labeled_images:
            content: Any = [
                {
                    "type": "text",
                    "text": "(Note only you can see: these are the photos you will share with the consultant.)",
                },
                *image_parts(labeled_images),
                {"type": "text", "text": f"Consultant: {greeting}"},
            ]
        else:
            content = greeting
        self.messages = [
            {
                "role": "system",
                "content": self.build_system_prompt(instruction=instruction),
            },
            {"role": "user", "content": content},
        ]
        # The base class calls reset() with no instruction on construction; skip that wasted call
        if instruction is None:
            return ""
        return self.generate_next_message(self.messages)
