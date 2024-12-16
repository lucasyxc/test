"""
Data models for corneal topography examination data.
Contains dataclasses representing the structure of corneal measurement data.
"""
from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class CornealTopographyData:
    """
    Represents corneal topography measurement data for a single examination.

    Attributes:
        eye_type: Type of eye measurement ('right', 'left')
        measurement_type: Type of measurement ('axial', 'tangential', 'difference')
        k1: First keratometry reading (in diopters)
        k1_axis: Axis of first keratometry reading (in degrees)
        k2: Second keratometry reading (in diopters)
        k2_axis: Axis of second keratometry reading (in degrees)
        delta_k: Difference between K2 and K1 (in diopters)
        pinge: Flatness index
        xiee: Steepness index
        is_index: Irregularity index
        sai: Surface asymmetry index
        sri: Surface regularity index
        pupil: Pupil diameter (in mm)
        pupil_area: Pupil area (in mm²)
        hvid: Horizontal visible iris diameter (in mm)
        tfsq: Tear film surface quality
        ctfsq: Corneal tear film surface quality
    """
    eye_type: Literal['right', 'left']
    measurement_type: Literal['axial', 'tangential', 'difference'] = 'axial'
    k1: Optional[float] = None
    k1_axis: Optional[int] = None
    k2: Optional[float] = None
    k2_axis: Optional[int] = None
    delta_k: Optional[float] = None
    pinge: Optional[float] = None
    xiee: Optional[float] = None
    is_index: Optional[float] = None
    sai: Optional[float] = None
    sri: Optional[float] = None
    pupil: Optional[float] = None
    pupil_area: Optional[float] = None
    hvid: Optional[float] = None
    tfsq: Optional[float] = None
    ctfsq: Optional[float] = None
