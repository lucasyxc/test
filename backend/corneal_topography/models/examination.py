from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class CornealTopographyData:
    """Data class for corneal topography measurements."""
    k1: Optional[float] = None
    k1_axis: Optional[float] = None
    k2: Optional[float] = None
    k2_axis: Optional[float] = None
    delta_k: Optional[float] = None
    pinge: Optional[float] = None
    xiee: Optional[float] = None
    is_value: Optional[float] = None  # Using is_value as 'is' is a Python keyword
    sai: Optional[float] = None
    sri: Optional[float] = None
    pupil: Optional[float] = None
    pupil_area: Optional[float] = None
    hvid: Optional[float] = None
    tfsq: Optional[float] = None
    ctfsq: Optional[float] = None

@dataclass
class ExaminationRecord:
    """Data class for patient examination records."""
    patient_id: int
    organization_id: str
    examination_date: date
    right_eye: Optional[CornealTopographyData] = None
    left_eye: Optional[CornealTopographyData] = None
    photo_path: Optional[str] = None
    brand: Optional[str] = None
    device: Optional[str] = None
    right_first: Optional[bool] = None
    left_first: Optional[bool] = None

    def calculate_delta_k(self) -> None:
        """Calculate delta_k for both eyes if k1 and k2 are available."""
        if self.right_eye and self.right_eye.k1 is not None and self.right_eye.k2 is not None:
            self.right_eye.delta_k = round(self.right_eye.k2 - self.right_eye.k1, 2)

        if self.left_eye and self.left_eye.k1 is not None and self.left_eye.k2 is not None:
            self.left_eye.delta_k = round(self.left_eye.k2 - self.left_eye.k1, 2)
