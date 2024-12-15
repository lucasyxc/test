from django.db import models
from django.utils import timezone
from .patient import PInfo

class PatientExaminationRecords(models.Model):
    """Model for storing patient examination records."""
    patient_id = models.ForeignKey(PInfo, on_delete=models.CASCADE)
    examination_date = models.DateField(default=timezone.now)
    file_url = models.CharField(max_length=255, null=True, blank=True)
    exam_type = models.CharField(max_length=50, null=True, blank=True)
    eye_position = models.CharField(max_length=10, null=True, blank=True)

    # Right eye measurements
    corneal_topography_right_eye_k1 = models.FloatField(null=True, blank=True)
    corneal_topography_right_eye_k1_axis = models.FloatField(null=True, blank=True)
    corneal_topography_right_eye_k2 = models.FloatField(null=True, blank=True)
    corneal_topography_right_eye_k2_axis = models.FloatField(null=True, blank=True)
    corneal_topography_right_eye_delta_k = models.FloatField(null=True, blank=True)
    corneal_topography_right_pinge = models.FloatField(null=True, blank=True)
    corneal_topography_right_xiee = models.FloatField(null=True, blank=True)
    corneal_topography_right_is = models.FloatField(null=True, blank=True)
    corneal_topography_right_sai = models.FloatField(null=True, blank=True)
    corneal_topography_right_sri = models.FloatField(null=True, blank=True)
    corneal_topography_right_pupil = models.FloatField(null=True, blank=True)
    corneal_topography_right_pupil_area = models.FloatField(null=True, blank=True)
    corneal_topography_right_hvid = models.FloatField(null=True, blank=True)
    corneal_topography_right_tfsq = models.FloatField(null=True, blank=True)
    corneal_topography_right_ctfsq = models.FloatField(null=True, blank=True)

    # Left eye measurements
    corneal_topography_left_eye_k1 = models.FloatField(null=True, blank=True)
    corneal_topography_left_eye_k1_axis = models.FloatField(null=True, blank=True)
    corneal_topography_left_eye_k2 = models.FloatField(null=True, blank=True)
    corneal_topography_left_eye_k2_axis = models.FloatField(null=True, blank=True)
    corneal_topography_left_eye_delta_k = models.FloatField(null=True, blank=True)
    corneal_topography_left_pinge = models.FloatField(null=True, blank=True)
    corneal_topography_left_xiee = models.FloatField(null=True, blank=True)
    corneal_topography_left_is = models.FloatField(null=True, blank=True)
    corneal_topography_left_sai = models.FloatField(null=True, blank=True)
    corneal_topography_left_sri = models.FloatField(null=True, blank=True)
    corneal_topography_left_pupil = models.FloatField(null=True, blank=True)
    corneal_topography_left_pupil_area = models.FloatField(null=True, blank=True)
    corneal_topography_left_hvid = models.FloatField(null=True, blank=True)
    corneal_topography_left_tfsq = models.FloatField(null=True, blank=True)
    corneal_topography_left_ctfsq = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'patient_examination_records'
        indexes = [
            models.Index(fields=['patient_id', 'examination_date']),
        ]

class PatientReviewReminder(models.Model):
    """Model for storing patient review reminders."""
    patient_id = models.ForeignKey(PInfo, on_delete=models.CASCADE)
    examination_record = models.ForeignKey(PatientExaminationRecords, on_delete=models.CASCADE)
    last_review_date = models.DateField()
    review_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patient_review_reminder'
        indexes = [
            models.Index(fields=['patient_id', 'review_date']),
        ]
