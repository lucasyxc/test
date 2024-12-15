from django.db import models
from datetime import date
from typing import Optional

class PInfo(models.Model):
    """Patient information model."""
    gkid = models.CharField(max_length=100, unique=True)
    organizationid = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    createDate = models.DateField(default=date.today)
    latestexamdate = models.DateField(null=True, blank=True)
    total_exam_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'patient_info'
        unique_together = ('gkid', 'organizationid')
        indexes = [
            models.Index(fields=['gkid', 'organizationid']),
            models.Index(fields=['latestexamdate']),
        ]

    def __str__(self):
        return f"{self.name} (GKID: {self.gkid})"
