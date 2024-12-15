import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models.patient import PInfo
from .models.examination import PatientExaminationRecords, PatientReviewReminder
from .services.cache_service import CacheService
from .services.file_service import FileService
from .services.examination_service import ExaminationService
from .services.rate_limiter import rate_limit
from django.conf import settings

logger = logging.getLogger(__name__)

@csrf_exempt
@rate_limit(key_prefix="corneal_topography")
def jt_medmontcorneal(request):
    """Handle corneal topography examination data."""
    if request.method != 'POST':
        logger.warning("Invalid request method: %s", request.method)
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        logger.info("Processing corneal topography request")
        file_service = FileService()
        cache_service = CacheService()
        examination_service = ExaminationService()

        # Validate and process file
        if 'file' not in request.FILES:
            logger.error("No file provided in request")
            return JsonResponse({"error": "No file provided"}, status=400)

        fundus_photo = request.FILES['file']
        file_result = file_service.process_file(fundus_photo)
        if not file_result.get('success'):
            return JsonResponse({"error": file_result.get('error')}, status=400)

        # Get request parameters
        organization_id = request.POST.get('organization_id')
        patient_gkid = request.POST.get('gkid')
        exam_type = request.POST.get('type')
        eye_r_l_d = request.POST.get('eye')

        logger.info("Processing data for patient %s from organization %s", patient_gkid, organization_id)

        # Validate required parameters
        if not patient_gkid:
            logger.error("Missing patient ID in request")
            return JsonResponse({"error": "Missing patient ID"}, status=400)

        # Try to get patient from cache first
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

        # Process examination data
        current_date = datetime.now().date()
        examination_data = {
            'patient_id': patient.id,
            'organization_id': organization_id,
            'examination_date': current_date,
            'photo_path': file_result.get('file_url'),
            'exam_type': exam_type,
            'eye_position': eye_r_l_d
        }

        try:
            # Import task at module level to avoid circular imports
            from .tasks import process_examination_data

            # Always call the task, let Celery handle ALWAYS_EAGER
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
            logger.error("Unexpected error: %s", str(e))
            return JsonResponse({"error": "Internal server error"}, status=500)

    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return JsonResponse({"error": "Internal server error"}, status=500)
