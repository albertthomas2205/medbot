from .models import PrivilegeModel
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PrivilegeModel
from .serializer import PrivilegeSerializer
import logging
logger = logging.getLogger(__name__)

def hasFeatureAccess(user, feature_code):
    try:
        feature = PrivilegeModel.objects.get(code=feature_code)
        if user.role == 'admin':
            return feature.allow_admin
        elif user.role == 'nurse':
            return feature.allow_nurse
        return False
    except PrivilegeModel.DoesNotExist:
        return False
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_privileges(request):
    try:
        if request.user.role not in ['admin']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'manage_privileges_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        privileges = PrivilegeModel.objects.all()
        serializer = PrivilegeSerializer(privileges, many=True)
        return Response({
            'status': 'success',
            'message': 'Privileges fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_privileges: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_privilege(request):
    try:
        if request.user.role not in ['admin']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'manage_privileges_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        privilege_id = request.data.get('id')
        code = request.data.get('code')

        if privilege_id:
            instance = PrivilegeModel.objects.filter(id=privilege_id).first()
            if not instance:
                return Response({
                    'status': 'error',
                    'message': 'Privilege not found.',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = PrivilegeSerializer(instance, data=request.data, partial=True)
            operation = "updated"
        else:
            # Check for duplicate code
            if PrivilegeModel.objects.filter(code=code).exists():
                return Response({
                    'status': 'error',
                    'message': 'Privilege with this code already exists.',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer = PrivilegeSerializer(data=request.data)
            operation = "created"

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': f"Privilege {operation} successfully.",
                'data': serializer.data
            }, status=status.HTTP_200_OK if privilege_id else status.HTTP_201_CREATED)

        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in create_or_update_privilege: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view_all_privileges_crud
# patient_data_handling_crud