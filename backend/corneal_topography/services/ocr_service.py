"""
Service for handling OCR processing of corneal topography images.
Uses PaddleOCR for text detection and recognition with rotation handling.
"""
import os
import logging
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image
from paddleocr import PaddleOCR
from django.conf import settings

logger = logging.getLogger(__name__)

class OCRService:
    """Service for processing corneal topography images using OCR."""

    def __init__(self, ocr_engine=None):
        """Initialize OCR service with optional OCR engine for testing."""
        try:
            self.ppocr = ocr_engine if ocr_engine is not None else PaddleOCR(
                use_angle_cls=True,  # Enable rotation detection
                lang='ch',  # Support Chinese text
                show_log=False,  # Disable PaddleOCR's internal logging
            )
            logger.info("OCR service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OCR service: {str(e)}")
            raise

    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image file and extract text content with position information.

        Args:
            image_path: Path to the image file

        Returns:
            Dict containing OCR results with text and positions

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image format is invalid
            Exception: For other processing errors
        """
        try:
            if not os.path.exists(image_path):
                error_msg = f"Image file not found: {image_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            # Validate and open image
            self._validate_image(image_path)

            # Perform OCR with rotation detection
            logger.info(f"Starting OCR processing for {image_path}")
            results = self.ppocr.ocr(image_path, cls=True)

            if not results:
                logger.warning(f"No text detected in image: {image_path}")
                return {"text_blocks": [], "rotation_angle": 0}

            # Parse and structure results
            processed_results = self._parse_ocr_results(results)
            logger.info(f"OCR processing completed for {image_path}")

            return processed_results

        except Exception as e:
            error_msg = f"OCR processing failed: {str(e)}"
            logger.error(error_msg)
            raise

    def _validate_image(self, image_path: str) -> None:
        """
        Validate image file format and readability.

        Args:
            image_path: Path to the image file

        Raises:
            ValueError: If image format is invalid
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            logger.debug(f"Image validation successful: {image_path}")
        except Exception as e:
            error_msg = f"Invalid image file: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _parse_ocr_results(self, results: List) -> Dict[str, Any]:
        """
        Parse OCR results into structured format.

        Args:
            results: Raw OCR results from PaddleOCR

        Returns:
            Dict containing structured OCR results
        """
        text_blocks = []
        rotation_angle = 0

        try:
            for idx, result in enumerate(results):
                if result is None:
                    continue

                for line in result:
                    if line is None:
                        continue

                    position = line[0]  # Coordinates of text box
                    text = line[1][0]   # Extracted text
                    confidence = line[1][1]  # Confidence score

                    text_blocks.append({
                        'text': text,
                        'confidence': float(confidence),
                        'position': position,
                        'block_id': idx
                    })

            logger.debug(f"Parsed {len(text_blocks)} text blocks from OCR results")
            return {
                'text_blocks': text_blocks,
                'rotation_angle': rotation_angle
            }

        except Exception as e:
            error_msg = f"Error parsing OCR results: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def get_text_by_region(self, results: Dict[str, Any], region: Tuple[float, float, float, float]) -> Optional[str]:
        """
        Extract text from a specific region in the OCR results.

        Args:
            results: Processed OCR results
            region: Tuple of (x_min, y_min, x_max, y_max) defining the region

        Returns:
            Extracted text if found in region, None otherwise
        """
        try:
            x_min, y_min, x_max, y_max = region

            for block in results['text_blocks']:
                pos = block['position']
                # Check if text block is within the specified region
                if (pos[0][0] >= x_min and pos[0][1] >= y_min and
                    pos[2][0] <= x_max and pos[2][1] <= y_max):
                    return block['text']

            return None

        except Exception as e:
            logger.error(f"Error extracting text from region: {str(e)}")
            return None
