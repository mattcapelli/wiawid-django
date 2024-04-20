import boto3
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.utils import randomlongstr

import logging
logger = logging.getLogger('WiaWid')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sign_files(request):
    
    data = request.data
    files_to_sign = data.get('filesToSign')

    if not files_to_sign:
        return Response(
            {'success': False, 'message': "Missing the 'files_to_sign' param"},
            status=status.HTTP_400_BAD_REQUEST
        )

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION
    )

    files_to_save = []
    for file_to_sign in files_to_sign:

        file_name = f"private/uploads/{randomlongstr()}.{file_to_sign['file_extension']}"

        try:
            presigned_post = s3_client.generate_presigned_post(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_name,
                Fields={"acl": "private", "Content-Type": file_to_sign['file_type']},
                Conditions=[
                    {"acl": "private"},
                    {"Content-Type": file_to_sign['file_type']}
                ],
                ExpiresIn=600
            )
            file_to_sign['presigned'] = presigned_post
            file_to_sign['url'] = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}'

        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            continue

        file_to_sign['file_original_name'] = file_to_sign['file_name']
        files_to_save.append(file_to_sign)

    return Response({'success': True, 'files': files_to_save})


