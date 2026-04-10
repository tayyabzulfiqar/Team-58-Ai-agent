from core.logging_utils import get_logger
from tools.cleaner_tool import cleaner_tool
from tools.analyzer_tool import analyzer_tool


logger = get_logger("team58.data")


class DataAgent:
    def run(self, input_data):
        logger.info("data:start")
        cleaned = cleaner_tool(input_data)
        analyzed = analyzer_tool(cleaned)
        logger.info("data:done")
        return analyzed
