import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

from .models.patient import PInfo
from .services.file_service import FileService
from .services.examination_service import ExaminationService
from .models.examination import CornealTopographyData

logger = logging.getLogger(__name__)

@csrf_exempt
def jt_medmontcorneal(request):
    """Handle corneal topography examination data."""
    if request.method != 'POST':
        logger.warning("Invalid request method: %s", request.method)
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # Initialize services
        file_service = FileService()
        examination_service = ExaminationService()

        # Extract and validate required fields
        organization_id = request.POST.get('organization_id')
        patient_gkid = request.POST.get('gkid')
        eye_type = request.POST.get('type')
        eye_side = request.POST.get('eye')

        if not patient_gkid:
            logger.error("Missing patient GKID")
            return JsonResponse({"error": "Missing patient ID"}, status=400)

        # Process file upload
        try:
            fundus_photo = request.FILES['file']
            filename, file_url = file_service.save_file(fundus_photo)
        except (KeyError, ValidationError) as e:
            logger.error("File upload error: %s", str(e))
            return JsonResponse({"error": str(e)}, status=400)

        # Get patient information
        try:
            patient = PInfo.objects.filter(
                gkid=patient_gkid,
                organizationid=organization_id
            ).first()
            if not patient:
                logger.error("Patient not found: %s", patient_gkid)
                return JsonResponse({"error": "Patient not found"}, status=404)
            logger.info("Found patient: %s, ID: %s", patient.name, patient.id)
        except Exception as e:
            logger.error("Patient lookup failed: %s", str(e))
            return JsonResponse({"error": "Patient lookup failed"}, status=500)

        # Process examination data
        current_date = datetime.now().date()
        examination_data = {
            'patient_id': patient.id,
            'organization_id': organization_id,
            'examination_date': current_date,
            'photo_path': file_url,
            'brand': 'Medmonte300',
            'device': request.POST.get('device'),
        }

        # Extract measurements based on eye side
        eye_data = {}
        for field in CornealTopographyData.__dataclass_fields__:
            if field != 'delta_k':  # delta_k is calculated automatically
                value = request.POST.get(f'corneal_topography_{eye_side}_{field}')
                if value:
                    try:
                        eye_data[field] = float(value)
                    except ValueError:
                        logger.warning("Invalid value for %s: %s", field, value)

        # Add eye-specific data
        if eye_side == 'right':
            examination_data['right_eye_data'] = eye_data
            examination_data['right_first'] = True
        else:
            examination_data['left_eye_data'] = eye_data
            examination_data['left_first'] = True

        # Create or update examination record
        try:
            record = examination_service.create_or_update_examination(**examination_data)
        except Exception as e:
            logger.error("Failed to save examination: %s", str(e))
            return JsonResponse({"error": "Failed to save examination"}, status=500)

        # Update patient information
        patient.total_exam_count += 1
        patient.latestexamdate = current_date
        patient.save()

        # Prepare response
        response_data = {
            "time": current_date.strftime('%Y-%m-%d'),
            "patient_name": patient.name,
            "createStatus": "当日新建" if record else "当日已有",
            "checkStatus": "Medmonte300",
            "patient_creation_time": patient.createDate.strftime('%Y-%m-%d') if patient.createDate else None
        }

        logger.info("Successfully processed examination for patient %s", patient_gkid)
        return JsonResponse({"success": True, "data": response_data}, status=200)

    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return JsonResponse({"error": "Internal server error", "details": str(e)}, status=500)
