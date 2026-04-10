from core.guarded_pipeline import run_guarded_pipeline
from core.input_utils import extract_query_text
from core.logging_utils import get_logger


logger = get_logger("team58.analyzer")


def analyzer_tool(data):
    query = extract_query_text(data)
    logger.info("analyzer:start")
    result = run_guarded_pipeline(query)
    logger.info("analyzer:done")
    return result
