import logging
from datetime import date
from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models.examination import ExaminationRecord, CornealTopographyData

logger = logging.getLogger(__name__)

class ExaminationService:
    """Service for handling examination records."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @transaction.atomic
    def create_or_update_examination(
        self,
        patient_id: int,
        organization_id: str,
        examination_date: date,
        photo_path: Optional[str] = None,
        **kwargs
    ) -> ExaminationRecord:
        """
        Create or update an examination record with atomic transaction.

        Args:
            patient_id: Patient's ID
            organization_id: Organization ID
            examination_date: Date of examination
            photo_path: Path to stored photo
            **kwargs: Additional examination data

        Returns:
            ExaminationRecord: Created or updated examination record
        """
        try:
            # Create examination record
            record = ExaminationRecord(
                patient_id=patient_id,
                organization_id=organization_id,
                examination_date=examination_date,
                photo_path=photo_path
            )

            # Process right eye data if available
            if 'right_eye_data' in kwargs:
                record.right_eye = CornealTopographyData(**kwargs['right_eye_data'])

            # Process left eye data if available
            if 'left_eye_data' in kwargs:
                record.left_eye = CornealTopographyData(**kwargs['left_eye_data'])

            # Calculate delta_k values
            record.calculate_delta_k()

            # Save to database (implementation depends on your ORM)
            self._save_to_database(record)

            self.logger.info(
                f"Successfully processed examination for patient {patient_id} "
                f"on {examination_date}"
            )

            return record

        except Exception as e:
            self.logger.error(
                f"Error processing examination for patient {patient_id}: {str(e)}"
            )
            raise

    def _save_to_database(self, record: ExaminationRecord) -> None:
        """
        Save examination record to database.
        This is a placeholder method - implement according to your ORM.
        """
        # Implementation depends on your database models
        pass
