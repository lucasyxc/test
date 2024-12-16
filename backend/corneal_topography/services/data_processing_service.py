"""
Service for processing and extracting measurements from OCR results of corneal topography images.
"""
import logging
import re
from typing import Dict, Any, Optional, List
from ..models.examination_data import CornealTopographyData

logger = logging.getLogger(__name__)

class DataProcessingService:
    """Service for extracting and processing corneal topography measurements from OCR results."""

    # Regular expressions for matching measurement patterns
    PATTERNS = {
        'k1': r'K1[:\s]*(\d+\.?\d*)',
        'k2': r'K2[:\s]*(\d+\.?\d*)',
        'axis': r'Axis[:\s]*(\d+)',
        'pupil': r'Pupil[:\s]*(\d+\.?\d*)',
        'delta_k': r'ΔK[:\s]*(\d+\.?\d*)',
    }

    def extract_measurements(self, ocr_results: Dict[str, Any], eye: str) -> CornealTopographyData:
        """
        Extract measurements from OCR results for specified eye.

        Args:
            ocr_results: Dictionary containing OCR results
            eye: 'right' or 'left' to specify which eye's measurements to extract

        Returns:
            CornealTopographyData object containing extracted measurements

        Raises:
            ValueError: If invalid eye parameter or if required measurements are missing
        """
        try:
            logger.info(f"Extracting measurements for {eye} eye")

            # Validate eye parameter
            if eye not in ['right', 'left']:
                raise ValueError(f"Invalid eye parameter: {eye}")

            # Initialize measurements dictionary
            measurements = {
                'k1': None,
                'k1_axis': None,
                'k2': None,
                'k2_axis': None,
                'delta_k': None,
                'pupil': None,
                'pupil_area': None,
                'hvid': None,
                'is_index': None,
                'sai': None,
                'sri': None,
                'pinge': None,
                'xiee': None,
                'tfsq': None,
                'ctfsq': None,
            }

            # Extract text blocks
            text_blocks = ocr_results.get('text_blocks', [])
            if not text_blocks:
                logger.warning("No text blocks found in OCR results")
                return self._create_topography_data(measurements, eye)

            # Process each text block
            combined_text = ' '.join(block['text'] for block in text_blocks)

            # Extract measurements using patterns
            measurements.update(self._extract_basic_measurements(combined_text))
            measurements.update(self._extract_advanced_indices(combined_text))

            # Validate critical measurements
            if not all(measurements[key] for key in ['k1', 'k2']):
                logger.warning("Critical measurements (K1, K2) missing from OCR results")

            logger.info(f"Successfully extracted measurements for {eye} eye")
            return self._create_topography_data(measurements, eye)

        except Exception as e:
            error_msg = f"Error extracting measurements: {str(e)}"
            logger.error(error_msg)
            raise

    def _extract_basic_measurements(self, text: str) -> Dict[str, Optional[float]]:
        """Extract basic measurements (K1, K2, axis) from text."""
        measurements = {}

        try:
            # Extract K1 and its axis
            k1_match = re.search(self.PATTERNS['k1'], text)
            if k1_match:
                measurements['k1'] = float(k1_match.group(1))
                axis_match = re.search(self.PATTERNS['axis'], text[k1_match.end():])
                if axis_match:
                    measurements['k1_axis'] = int(axis_match.group(1))

            # Extract K2 and its axis
            k2_match = re.search(self.PATTERNS['k2'], text)
            if k2_match:
                measurements['k2'] = float(k2_match.group(1))
                axis_match = re.search(self.PATTERNS['axis'], text[k2_match.end():])
                if axis_match:
                    measurements['k2_axis'] = int(axis_match.group(1))

            # Extract ΔK
            delta_k_match = re.search(self.PATTERNS['delta_k'], text)
            if delta_k_match:
                measurements['delta_k'] = float(delta_k_match.group(1))

            # Extract pupil measurements
            pupil_match = re.search(self.PATTERNS['pupil'], text)
            if pupil_match:
                measurements['pupil'] = float(pupil_match.group(1))

        except ValueError as e:
            logger.error(f"Error converting measurement to float: {str(e)}")
        except Exception as e:
            logger.error(f"Error extracting basic measurements: {str(e)}")

        return measurements


    def _extract_advanced_indices(self, text: str) -> Dict[str, Optional[float]]:
        """Extract advanced corneal indices from text."""
        indices = {}

        # Define patterns for advanced indices
        advanced_patterns = {
            'is_index': r'IS[:\s]*(\d+\.?\d*)',
            'sai': r'SAI[:\s]*(\d+\.?\d*)',
            'sri': r'SRI[:\s]*(\d+\.?\d*)',
            'pinge': r'平光[值度]*[:\s]*(\d+\.?\d*)',  # Chinese character for "flat"
            'xiee': r'斜[光度]*[:\s]*(\d+\.?\d*)',    # Chinese character for "oblique"
        }

        try:
            for key, pattern in advanced_patterns.items():
                match = re.search(pattern, text)
                if match:
                    try:
                        indices[key] = float(match.group(1))
                    except ValueError:
                        logger.warning(f"Could not convert {key} value to float")
                        indices[key] = None

        except Exception as e:
            logger.error(f"Error extracting advanced indices: {str(e)}")

        return indices

    def _create_topography_data(self, measurements: Dict[str, Optional[float]], eye: str) -> CornealTopographyData:
        """
        Create CornealTopographyData object from measurements.

        Args:
            measurements: Dictionary of measurements
            eye: Type of eye ('right' or 'left')

        Returns:
            CornealTopographyData object
        """
        try:
            # Convert measurement values to appropriate types
            k1_axis = int(measurements.get('k1_axis')) if measurements.get('k1_axis') is not None else None
            k2_axis = int(measurements.get('k2_axis')) if measurements.get('k2_axis') is not None else None

            return CornealTopographyData(
                eye_type=eye,
                k1=measurements.get('k1'),
                k1_axis=k1_axis,
                k2=measurements.get('k2'),
                k2_axis=k2_axis,
                delta_k=measurements.get('delta_k'),
                pupil=measurements.get('pupil'),
                pupil_area=measurements.get('pupil_area'),
                hvid=measurements.get('hvid'),
                is_index=measurements.get('is_index'),
                sai=measurements.get('sai'),
                sri=measurements.get('sri'),
                pinge=measurements.get('pinge'),
                xiee=measurements.get('xiee'),
                tfsq=measurements.get('tfsq'),
                ctfsq=measurements.get('ctfsq')
            )
        except Exception as e:
            error_msg = f"Error creating CornealTopographyData object: {str(e)}"
            logger.error(error_msg)
            raise
