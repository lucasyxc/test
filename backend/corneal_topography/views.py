import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.db import transaction
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models.patient import PInfo
from .models.examination import PatientExaminationRecords, PatientReviewReminder
from .services.cache_service import CacheService
from .services.file_service import FileService
from .services.ocr_service import OCRService
from .services.data_processing_service import DataProcessingService
from .services.examination_service import ExaminationService
from .services.rate_limiter import rate_limit
from django.conf import settings

logger = logging.getLogger(__name__)

# Singleton OCR service instance
_ocr_service = None

def get_ocr_service():
    """Get or create OCR service instance."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service

@csrf_exempt
@rate_limit(key_prefix="corneal_topography")
def jt_Medmontcorneal(request):
    """Handle corneal topography examination data processing."""
    if request.method != 'POST':
        logger.warning("Invalid request method: %s", request.method)
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        logger.info("Processing corneal topography request")

        # Initialize services
        file_service = FileService()
        cache_service = CacheService()
        ocr_service = get_ocr_service()
        data_processing_service = DataProcessingService()
        examination_service = ExaminationService()

        # Validate request parameters
        required_fields = ['organization_id', 'gkid', 'type', 'eye']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]
        if missing_fields:
            logger.error("Missing required fields: %s", ", ".join(missing_fields))
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=400)

        # Process file upload
        if 'file' not in request.FILES:
            logger.error("No file provided in request")
            return JsonResponse({"error": "No file provided"}, status=400)

        fundus_photo = request.FILES['file']
        success, error_msg, file_url = file_service.validate_and_save_file(fundus_photo)
        if not success:
            logger.error("File processing failed: %s", error_msg)
            return JsonResponse({"error": error_msg}, status=400)

        # Get and validate request parameters
        organization_id = request.POST['organization_id']
        patient_gkid = request.POST['gkid']
        exam_type = request.POST['type']
        eye_r_l_d = request.POST['eye']

        logger.info("Processing data for patient %s from organization %s", patient_gkid, organization_id)

        # Get patient data with caching
        patient = cache_service.get_patient(patient_gkid, organization_id)
        if not patient:
            try:
                patient = PInfo.objects.filter(gkid=patient_gkid, organizationid=organization_id).first()
                if not patient:
                    logger.error("Patient not found: %s", patient_gkid)
                    return JsonResponse({"error": "Patient not found"}, status=404)
                cache_service.set_patient(patient_gkid, organization_id, patient)
            except Exception as e:
                logger.error("Error retrieving patient: %s", str(e))
                return JsonResponse({"error": "Error retrieving patient"}, status=500)

        # Process OCR and extract measurements
        try:
            ocr_results = ocr_service.process_image(file_url)
            measurements = data_processing_service.extract_measurements(ocr_results, eye_r_l_d)
        except Exception as e:
            logger.error("Error processing image data: %s", str(e))
            return JsonResponse({"error": "Error processing image data"}, status=500)

        # Prepare examination data
        current_date = datetime.now().date()
        examination_data = {
            'patient_id': patient.id,
            'organization_id': organization_id,
            'examination_date': current_date,
            'photo_path': file_url,
            'exam_type': exam_type,
            'eye_position': eye_r_l_d,
            'measurements': measurements
        }

        try:
            # Import task at module level to avoid circular imports
            from .tasks import process_examination_data

            # Process examination data asynchronously
            process_examination_data.delay(examination_data)

            response_data = {
                "time": current_date.strftime('%Y-%m-%d'),
                "patient_name": patient.name,
                "createStatus": "Success",
                "checkStatus": "Medmonte300",
                "patient_creation_time": patient.createDate.strftime('%Y-%m-%d') if patient.createDate else None
            }
            return JsonResponse({"success": True, "data": response_data}, status=200)

        except Exception as e:
            logger.error("Error scheduling examination processing: %s", str(e))
            return JsonResponse({"error": "Internal server error"}, status=500)

    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return JsonResponse({"error": "Internal server error"}, status=500)
