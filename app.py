import logging
import json
import re
from pathlib import Path

from debate_engine import DebateEngine
from utils.guardrails import InputGuardrailException

## make sure logging starts first
def setup_logging(config_file: str = "logging.json"):
    import json
    import logging.config

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Load the JSON configuration
    with open(config_file, 'r') as f:
        config = json.load(f)

    # Apply the configuration
    logging.config.dictConfig(config)
setup_logging()
##

import asyncio

async def async_input(user_prompt: str) -> str:
    result = await asyncio.to_thread(input, user_prompt)
    return result.strip()

def sanitize_filename(motion: str) -> str:
    """Convert motion to a filesystem-safe filename."""
    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r'[^\w\s-]', '', motion)
    sanitized = re.sub(r'[\s-]+', '_', sanitized)
    return sanitized[:50]  # Limit to 50 chars

async def app_main() -> None:
    logger = logging.getLogger(__name__)
    logger.info("Starting application")
    
    # Create results folder if it doesn't exist
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    while True:
        motion = await async_input("Enter motion to debate about (EMPTY to quit): ")
        if len(motion) == 0:
            return

        try:
            logger.info(f"Will ask AI agents to debate {motion}")
            debateEngine = DebateEngine(motion=motion, total_rounds=5, words_count_turn=50, age=9)

            debateSession = await debateEngine.run_debate()

            # Save result to JSON file in results folder
            safe_motion = sanitize_filename(motion)
            output_file = results_dir / f"debate_{safe_motion}.json"
            with open(output_file, "w") as f:
                json_data = debateSession.model_dump_json(indent=4)
                f.write(json_data)
            logger.info(f"Debate result saved to {output_file}")

            print("******START*********\n")
            print(debateSession.model_dump_json(indent=4))
            print("******END*********\n")
        except InputGuardrailException as e:
            logger.warning(e)
        except Exception as e:
            logger.error(e)

if __name__ == "__main__":
    asyncio.run(app_main())