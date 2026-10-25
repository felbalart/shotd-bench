from typing import Any, Dict, List, Tuple

from litellm import completion

SYSTEM_PROMPT = """You are a user chatting with a photography consultant.

Instruction: {instruction}

Rules:
- Just generate one line at a time to simulate the user's message.
- Do not give away all the instruction at once. Only provide the information that is necessary for the current step.
- Do not hallucinate information that is not provided in the instruction or visible in your photos. If something cannot be seen and is not in the instruction, say you are not sure.
- Your photos are attached to your first message automatically, so never paste links or describe the photos as attachments.
- Do not repeat the exact instruction in the conversation. Instead, use your own words to convey the same information.
- Do not end the conversation yourself before the consultant has given you a complete photography plan. Once your goal is satisfied, generate '###STOP###' as a standalone message.
- Try to make the conversation as natural as possible, and stick to the personality in the instruction."""


def image_parts(labeled_urls: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = []
    for label, url in labeled_urls:
        parts.append({"type": "text", "text": label})
        parts.append({"type": "image_url", "image_url": {"url": url}})
    return parts


class UserSimulator:
    """LLM-simulated user who can see the photos they share with the agent."""

    def __init__(self, model: str, provider: str) -> None:
        self.model = model
        self.provider = provider
        self.messages: List[Dict[str, Any]] = []
        self.total_cost = 0.0

    def reset(self, instruction: str, labeled_images: List[Tuple[str, str]]) -> str:
        greeting = "Consultant: Hi! How can I help you today?"
        content: Any = greeting
        if labeled_images:
            content = [
                {"type": "text", "text": "(Note only you can see: these are the photos you will share with the consultant.)"},
                *image_parts(labeled_images),
                {"type": "text", "text": greeting},
            ]
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(instruction=instruction)},
            {"role": "user", "content": content},
        ]
        self.total_cost = 0.0
        return self._generate()

    def step(self, content: str) -> str:
        self.messages.append({"role": "user", "content": content})
        return self._generate()

    def _generate(self) -> str:
        res = completion(model=self.model, custom_llm_provider=self.provider, messages=self.messages)
        message = res.choices[0].message
        self.messages.append(message.model_dump())
        self.total_cost += res._hidden_params["response_cost"] or 0
        return message.content
