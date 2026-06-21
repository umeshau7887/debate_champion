"""
Agent that can debate on any motion.
"""
from typing import List
import uuid
from abc import ABC, abstractmethod
from dataclasses import replace
from pydantic_ai import Agent
import logging
import os

from data_model import DebateRound
from utils.prompt_service import PromptService
from enum import Enum, auto
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

from utils.save_for_evals import record_ai_response

logger = logging.getLogger(__name__)

## the types of writers
class AutoName(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

class Debater(AutoName):
    FOR_THE_MOTION = auto()
    AGAINST_THE_MOTION = auto()

class AbstractDebater(ABC):
    def __init__(self, debater: Debater):
        self.id = f"{debater.name} Agent {uuid.uuid4()}"
        self.debater = debater
        logger.info(f"Created {self.id}")
        self.model_name = os.environ.get("OLLAMA_MODEL_NAME", "gemma4")
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    @property
    def name(self) -> str:
        return self.debater.name.replace("_", " ").title()

    @abstractmethod
    async def debate_on_the_motion(self, motion: str, words_count: int, age: int, rounds: List[DebateRound]) -> str:
        pass



class ZeroshotDebater(AbstractDebater):
    def __init__(self, debater: Debater):
        super().__init__(debater)
        # the prompt files are named by the debater name
        system_prompt_file = f"{self.debater.name}_system_prompt".lower()
        system_prompt = PromptService.render_prompt(system_prompt_file)

        model = OllamaModel(
            model_name = self.model_name,
            provider=OllamaProvider(base_url=self.base_url)
        )

        self.agent = Agent(model,
                           output_type=str,
                           #model_settings=llms.default_model_settings(),
                           retries=2,
                           system_prompt=system_prompt)

    async def debate_on_the_motion(self, motion: str, words_count: int, age: int, debate_history: List[DebateRound], current_round: int, total_rounds: int) -> str:

        # the prompt is the same for all writers, but the content_type is parameterized in this file
        prompt_vars = {
            "prompt_name": f"debate_user_prompt",
            "motion": motion,
            "words_count": words_count,
            "age": age,
            "debate_history": debate_history,
            "current_round": current_round,
            "total_rounds": total_rounds,
        }
        prompt = PromptService.render_prompt(**prompt_vars)


        result = await self.agent.run(prompt)
        logger.info(result.usage)
        record_ai_response(self.name, prompt, result.output)

        return result.output


class ForTheMotionDebator(ZeroshotDebater):
    def __init__(self):
        super().__init__(Debater.FOR_THE_MOTION)

class AgainstTheMotionDebater(ZeroshotDebater):
    def __init__(self):
        super().__init__(Debater.AGAINST_THE_MOTION)

class DebaterFactory:
    @staticmethod
    def create_debater(debater: Debater) -> AbstractDebater:
        match debater:
            case Debater.FOR_THE_MOTION:
                return ForTheMotionDebator()
            case Debater.AGAINST_THE_MOTION:
                return AgainstTheMotionDebater()