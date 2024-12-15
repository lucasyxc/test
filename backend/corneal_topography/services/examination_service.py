import logging
from datetime import date
from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models.examination import PatientExaminationRecords
from ..models.patient import PInfo

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
    ) -> PatientExaminationRecords:
        """
        Create or update an examination record with atomic transaction.

        Args:
            patient_id: Patient's ID
            organization_id: Organization ID
            examination_date: Date of examination
            photo_path: Path to stored photo
            **kwargs: Additional examination data

        Returns:
            PatientExaminationRecords: Created or updated examination record
        """
        try:
            # Get patient instance
            patient = PInfo.objects.get(id=patient_id, organizationid=organization_id)

            # Check for existing record
            record = PatientExaminationRecords.objects.filter(
                patient_id=patient,
                examination_date=examination_date
            ).first()

            if not record:
                record = PatientExaminationRecords(
                    patient_id=patient,
                    examination_date=examination_date,
                    file_url=photo_path
                )

            # Update fields from kwargs
            for field, value in kwargs.items():
                if hasattr(record, field) and value is not None:
                    setattr(record, field, value)

            # Save the record
            record.save()

            # Update patient's examination count and date
            patient.total_exam_count = patient.total_exam_count + 1 if not record.id else patient.total_exam_count
            patient.latestexamdate = examination_date
            patient.save()

            self.logger.info(
                f"Successfully processed examination for patient {patient_id} "
                f"on {examination_date}"
            )

            return record

        except PInfo.DoesNotExist:
            error_msg = f"Patient {patient_id} not found in organization {organization_id}"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)
        except Exception as e:
            self.logger.error(
                f"Error processing examination for patient {patient_id}: {str(e)}"
            )
            raise
