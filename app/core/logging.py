import logging
from app.core.config import settings

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("ai_rag_data_pipeline")
logger.setLevel(settings.log_level)
if not logger.handlers:
    logger.addHandler(handler)

logger.debug("Logging initialized with level %s", settings.log_level)
