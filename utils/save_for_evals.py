import logging

logger = logging.getLogger(__name__)

def record_ai_response(target, ai_input, ai_response):
    """Record AI interaction for evaluations.

    This is synchronous because callers in the codebase invoke it
    without awaiting. Keeps logging simple and predictable.
    """
    logger.info("AI Response",
                extra={
                    "target": target,
                    "ai_input": ai_input,
                    "ai_response": ai_response,
                })