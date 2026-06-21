import logging
import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv

from debate_engine import DebateEngine
from utils.guardrails import InputGuardrailException
from utils.json_to_text import format_debate_data

## make sure logging starts first
load_dotenv()

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


def sendMail(motion: str, debate_result: str) -> None:
    from utils.mail_service import MailService

    mail_service = MailService()
    subject = f"Debate Result for Motion: {motion}"
    body = debate_result

    # Send the email to a predefined recipient
    recipient_email = os.environ.get("MAIL_RECEPIENT")
    if recipient_email:
        success = mail_service.send_mail(
            to_email=recipient_email,
            subject=subject,
            body=body,
            is_html=False
        )
        if success:
            logging.info(f"Debate result email sent to {recipient_email}")
        else:
            logging.error("Failed to send debate result email.")
    else:
        logging.warning("MAIL_RECEPIENT environment variable not set. Email not sent.")


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
            debateEngine = DebateEngine(motion=motion, total_rounds=1, words_count_turn=50, age=9)

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

            rounds_json = json.dumps([round.model_dump() for round in debateSession.rounds], indent=4)
            formatted_debate_data = format_debate_data(rounds_json)
            sendMail(motion, formatted_debate_data)

        except InputGuardrailException as e:
            logger.warning(e)
        except Exception as e:
            logger.error(e)

if __name__ == "__main__":
    asyncio.run(app_main())