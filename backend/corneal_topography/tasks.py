import logging
from celery import shared_task
from .services.examination_service import ExaminationService
from .services.cache_service import CacheService

logger = logging.getLogger(__name__)

@shared_task
def process_examination_data(examination_data: dict) -> None:
    """
    Process examination data asynchronously.

    Args:
        examination_data: Dictionary containing examination data
    """
    try:
        examination_service = ExaminationService()
        cache_service = CacheService()

        # Process the examination data
        record = examination_service.create_or_update_examination(**examination_data)

        # Update cache
        cache_service.set_examination(
            record.patient_id,
            record.examination_date.isoformat(),
            record
        )

        logger.info(
            "Successfully processed examination data for patient %s",
            examination_data.get('patient_id')
        )
    except Exception as e:
        logger.error(
            "Failed to process examination data: %s",
            str(e),
            exc_info=True
        )
        raise
