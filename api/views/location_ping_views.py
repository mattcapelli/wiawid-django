from django.shortcuts import render
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.utils import *

from rest_framework import status
from django.db.models import Q

from core.utils import randomstr

from api.views.utils import *

from backend.models import *

import json
from django.utils import timezone
import datetime

import logging
logger = logging.getLogger('WiaWid')

# Custom decorators
from backend.decorators import *

# Serializers
from api.serializers.location_ping_serializers import *

from api.views.utils import *

# API documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.documentation.location_ping_documentation import *
from api.documentation.common_elements import error_response, success_response

# Auth
from api.views.utils import IsAuthenticatedOrHasAPIKey


#-----------------------------------------------------------------------------------------------------------------------------
# Getting location_pings
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='get',
    tags=['LocationPings'],
    operation_id="Get LocationPing List",
    operation_description="Retrieve a list of location_pings",
    responses={
        200: location_ping_list_response_schema,
        400: error_response,
        403: error_response
    },
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Search term", type=openapi.TYPE_STRING),
        openapi.Parameter('sort', openapi.IN_QUERY, description="Sort option", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrHasAPIKey]) # Auth only, no API key
def get_location_pings(request):
    
    user = request.user

    # Filter location_pings based on user and status, using select_related for optimization
    query = LocationPing.objects.select_related('user').filter(user=user, status='active').order_by('-created_at')

    # LocationPingly search filtering if applicable
    search_query = request.query_params.get('search', '').strip()
    if search_query:
        query = query.filter(Q(geocoordinate__icontains=search_query))

    # LocationPingly sorting
    sort_option = request.query_params.get('sort', '').strip()
    sort_fields = {
        'created_at_asc': 'created_at',
        'created_at_desc': '-created_at',
        'geocoordinate_asc': 'geocoordinate',
        'geocoordinate_desc': '-geocoordinate'
    }
    query = query.order_by(sort_fields.get(sort_option, '-created_at'))  # Default sort by name

    # Pagination
    try:
        page_number = int(request.query_params.get('page', 1))
    except ValueError:
        return Response({'errors': ['Page number must be an integer.']}, status=status.HTTP_400_BAD_REQUEST)
    try:
        page_size = int(request.query_params.get('page_size', 5))
        if page_size > 100:  # Check if page size is above 100
            return Response({'errors': ['Page size cannot exceed 100.']}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'errors': ['Page size must be an integer.']}, status=status.HTTP_400_BAD_REQUEST)
    paginator = Paginator(query, page_size)
    
    try:
        location_pings = paginator.page(page_number)
    except PageNotAnInteger:
        location_pings = paginator.page(1)
    except EmptyPage:
        location_pings = paginator.page(paginator.num_pages)

    serializer = LocationPingSerializer(location_pings, many=True)
    response_data = {
        'location_pings': serializer.data,
        'page': location_pings.number,
        'pages': paginator.num_pages,
        'records_count': paginator.count
    }

    return Response(response_data)


@swagger_auto_schema(
    method='get',
    tags=['LocationPings'],
    operation_id="Get LocationPing",
    operation_description="Retrieve a location ping",
    responses={
        200: location_ping_response_schema,
        400: error_response,
        403: error_response
    },
    manual_parameters=[]
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def get_location_ping(request, location_ping_id):

    user = request.user
    location_ping = LocationPing.objects.select_related('user').filter(location_ping_id=location_ping_id, status='active').first()
    if location_ping:
        serializer = LocationPingSerializer(location_ping, many=False)
        return Response({'location_ping': serializer.data})
    else:
        return Response({'errors': ['Location ping does not exist.']}, status=status.HTTP_400_BAD_REQUEST)


#-----------------------------------------------------------------------------------------------------------------------------
# Adding location_pings
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='post',
    tags=['LocationPings'],
    operation_id="Add LocationPing",
    operation_description="Add a location ping",
    request_body=location_ping_add_schema,
    responses={
        201: location_ping_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrHasAPIKey]) # Auth only, no API key
def add_location_ping(request):
    
    user = request.user
    location_ping_object = request.data
    
    valid_params = check_params(location_ping_object, [
        {'param': 'location_ping_id', 'type': 'string', 'required': False, 'length': 32},
        {'param': 'lat', 'type': 'float', 'required': True},
        {'param': 'lng', 'type': 'float', 'required': True},
        {'param': 'geocoordinate', 'type': 'string', 'required': True},
        {'param': 'accuracy', 'type': 'float', 'required': True},
        {'param': 'altitude', 'type': 'float', 'required': True},
        {'param': 'heading', 'type': 'float', 'required': True},
        {'param': 'speed', 'type': 'float', 'required': True},
        {'param': 'timestamp', 'type': 'datetime', 'required': True},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])
    
    if valid_params['valid']:
        try:
            with transaction.atomic():
                result = create_location_ping_record(location_ping_object, request.user)
            serializer = LocationPingSerializer(result['location_ping'])
            return Response({'location_ping': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating location ping: {e}')
            return Response({'errors': ['Failed to create location ping.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    tags=['LocationPings'],
    operation_id="Add LocationPings",
    operation_description="Add a list of location pings",
    request_body=location_ping_add_request_body,
    responses={
        200: add_location_pings_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def add_location_pings(request):
    data = request.data
    
    location_pings_data = data.get('location_pings')
    if not isinstance(location_pings_data, list) or not location_pings_data:
        return Response({'errors': ['LocationPings list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(location_pings_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'location_pings_added': [], 'location_pings_not_added': []}

    try:
        with transaction.atomic():
            for index, location_ping_object in enumerate(location_pings_data):

                valid_params = check_params(location_ping_object, [
                    {'param': 'location_ping_id', 'type': 'string', 'required': False, 'length': 32},
                    {'param': 'lat', 'type': 'float', 'required': True},
                    {'param': 'lng', 'type': 'float', 'required': True},
                    {'param': 'geocoordinate', 'type': 'string', 'required': True},
                    {'param': 'accuracy', 'type': 'float', 'required': True},
                    {'param': 'altitude', 'type': 'float', 'required': True},
                    {'param': 'heading', 'type': 'float', 'required': True},
                    {'param': 'speed', 'type': 'float', 'required': True},
                    {'param': 'timestamp', 'type': 'datetime', 'required': True},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    result = create_location_ping_record(location_ping_object, request.user)
                    serializer = LocationPingSerializer(result['location_ping'])
                    response_data['location_pings_added'].append(serializer.data)
                else:
                    response_data['location_pings_not_added'].append({
                        'index': index,
                        'submitted_object': location_ping_object,
                        'errors': valid_params['errors']
                    })
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error adding location_pings: {e}')
        return Response({'errors': ['Failed to add location_pings.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Updating location_pings
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['LocationPings'],
    operation_id="Update LocationPing",
    operation_description="Update a location ping",
    request_body=location_ping_update_schema,
    responses={
        201: location_ping_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def update_location_ping(request, location_ping_id):
    location_ping_object = request.data
    user = request.user
    
    valid_params = check_params(location_ping_object, [
        {'param': 'location_ping_id', 'type': 'string', 'required': True, 'length': 32},
        {'param': 'lat', 'type': 'float', 'required': True},
        {'param': 'lng', 'type': 'float', 'required': True},
        {'param': 'geocoordinate', 'type': 'string', 'required': True},
        {'param': 'accuracy', 'type': 'float', 'required': True},
        {'param': 'altitude', 'type': 'float', 'required': True},
        {'param': 'heading', 'type': 'float', 'required': True},
        {'param': 'speed', 'type': 'float', 'required': True},
        {'param': 'timestamp', 'type': 'datetime', 'required': True},
        {'param': 'data', 'type': 'object', 'required': False},
        {'param': 'config', 'type': 'object', 'required': False},
    ])

    if valid_params['valid']:
        try:
            with transaction.atomic():
                location_ping_id = location_ping_object['location_ping_id']
                location_ping = LocationPing.objects.filter(location_ping_id=location_ping_id, status='active').first()
                if location_ping:
                    result = update_location_ping_record(location_ping, location_ping_object)
                    serializer = LocationPingSerializer(result['location_ping'])
                    return Response({'location_ping': serializer.data}, status=status.HTTP_200_OK)
                else:
                    logger.error(f'Error updating location_ping: Location_ping does not exist.')
                    return Response({'errors': ['Location_ping does not exist.']}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f'Error updating location_ping: {e}')
            return Response({'errors': ['Failed to update location_ping.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'errors': valid_params['errors']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    tags=['LocationPings'],
    operation_id="Update LocationPings",
    operation_description="Update a list of location_pings",
    request_body=location_ping_update_request_body,
    responses={
        200: update_location_pings_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def update_location_pings(request):
    data = request.data

    location_pings_data = data.get('location_pings')
    if not isinstance(location_pings_data, list) or not location_pings_data:
        return Response({'errors': ['Location pings list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(location_pings_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'location_pings_updated': [], 'location_pings_not_updated': []}

    try:
        with transaction.atomic():
            for index, location_ping_object in enumerate(location_pings_data):
                valid_params = check_params(location_ping_object, [
                    {'param': 'location_ping_id', 'type': 'string', 'required': True, 'length': 32},
                    {'param': 'lat', 'type': 'float', 'required': True},
                    {'param': 'lng', 'type': 'float', 'required': True},
                    {'param': 'geocoordinate', 'type': 'string', 'required': True},
                    {'param': 'accuracy', 'type': 'float', 'required': True},
                    {'param': 'altitude', 'type': 'float', 'required': True},
                    {'param': 'heading', 'type': 'float', 'required': True},
                    {'param': 'speed', 'type': 'float', 'required': True},
                    {'param': 'timestamp', 'type': 'datetime', 'required': True},
                    {'param': 'data', 'type': 'object', 'required': False},
                    {'param': 'config', 'type': 'object', 'required': False},
                ])

                if valid_params['valid']:
                    location_ping_id = location_ping_object['location_ping_id']
                    location_ping = LocationPing.objects.filter(location_ping_id=location_ping_id, status='active').first()
                    if location_ping:
                        try:
                            result = update_location_ping_record(location_ping, location_ping_object)
                            serializer = LocationPingSerializer(result['location_ping'])
                            response_data['location_pings_updated'].append(serializer.data)
                        except LocationPing.DoesNotExist:
                            response_data['location_pings_not_updated'].append({
                                'index': index,
                                'submitted_object': location_ping_object,
                                'errors': ['LocationPing could not be updated']
                            })
                    else:
                        response_data['location_pings_not_updated'].append({
                            'index': index,
                            'submitted_object': location_ping_object,
                            'errors': ['LocationPing not found']
                        })
                else:
                    response_data['location_pings_not_updated'].append({
                        'index': index,
                        'submitted_object': location_ping_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error updating location_pings: {e}')
        return Response({'errors': ['Failed to update location_pings.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#-----------------------------------------------------------------------------------------------------------------------------
# Archiving location_pings
#-----------------------------------------------------------------------------------------------------------------------------

@swagger_auto_schema(
    method='put',
    tags=['LocationPings'],
    operation_id="Archive LocationPing",
    operation_description="Archive a location_ping",
    responses={
        201: location_ping_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def archive_location_ping(request, location_ping_id):
    
    location_ping = LocationPing.objects.select_related('user').filter(location_ping_id=location_ping_id, status='active').first()
    if location_ping:
        try:
            with transaction.atomic():
                location_ping.status = "archived"
                location_ping.save()
            serializer = LocationPingSerializer(location_ping)
            return Response({'location_ping': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error archiving location_ping: {e}')
            return Response({'errors': ['Failed to archive location_ping.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = LocationPingSerializer(location_ping, many=False)
        return Response({'location_ping': serializer.data})
    else:
        return Response({'errors': ['Location ping does not exist.']}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    tags=['LocationPings'],
    operation_id="Archive LocationPings",
    operation_description="Archive a list of location_pings",
    request_body=location_ping_archive_request_body,
    responses={
        200: archive_location_pings_response_schema,
        400: error_response,
        403: error_response,
        500: error_response
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def archive_location_pings(request):
    data = request.data

    location_pings_data = data.get('location_pings')
    if not isinstance(location_pings_data, list) or not location_pings_data:
        return Response({'errors': ['LocationPings list is required and should not be empty.']}, status=status.HTTP_400_BAD_REQUEST)
    if len(location_pings_data) > 100: # Check if there are more than 100 objects
        return Response({'errors': ['Cannot perform bulk operations on more than 100 objects.']}, status=status.HTTP_400_BAD_REQUEST)
    
    response_data = {'location_pings_archived': [], 'location_pings_not_archived': []}

    try:
        with transaction.atomic():
            for index, location_ping_object in enumerate(location_pings_data):
                valid_params = check_params(location_ping_object, [
                    {'param': 'location_ping_id', 'type': 'string', 'required': True, 'length': 32},
                ])

                if valid_params['valid']:
                    location_ping_id = location_ping_object['location_ping_id']
                    try:
                        location_ping = LocationPing.objects.get(location_ping_id=location_ping_id, status="active")
                        location_ping.status = "archived"
                        location_ping.save()
                        serializer = LocationPingSerializer(location_ping)
                        response_data['location_pings_archived'].append(serializer.data)
                    except LocationPing.DoesNotExist:
                        response_data['location_pings_not_archived'].append({
                            'index': index,
                            'submitted_object': location_ping_object,
                            'errors': ['LocationPing not found']
                        })
                else:
                    response_data['location_pings_not_archived'].append({
                        'index': index,
                        'submitted_object': location_ping_object,
                        'errors': valid_params['errors']
                    })

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error archiving location_pings: {e}')
        return Response({'errors': ['Failed to archive location_pings.']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#-----------------------------------------------------------------------------------------------------------------------------
# Utils location_pings
#-----------------------------------------------------------------------------------------------------------------------------

def create_location_ping_record(data, user):
    try:

        location_ping_id = data.get('location_ping_id', randomstr())

        location_ping_data = {
            'location_ping_id': location_ping_id,
            'user': user,
            'lat': data['lat'],
            'lng': data['lng'],
            'geocoordinate': data['geocoordinate'],
            'altitude': data['altitude'],
            'accuracy': data['accuracy'],
            'heading': data['heading'],
            'speed': data['speed'],
            'data': data.get('data'),
            'config': data.get('config'),
        }

        # Remove None values from dictionary
        location_ping_data = {k: v for k, v in location_ping_data.items() if v is not None}

        location_ping = LocationPing.objects.create(**location_ping_data)

        # Compile the timestamp
        if 'timestamp' in data:
            timestamp_data = data['timestamp']
            timestamp = datetime.datetime(timestamp_data['year'], timestamp_data['month'], timestamp_data['day'], timestamp_data['hour'], timestamp_data['minute'], timestamp_data['second'])
            location_ping.timestamp = timestamp
            location_ping.save()

        return {
            'success': True,
            'location_ping': location_ping,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error creating the location_ping record'],
        }


def update_location_ping_record(location_ping, data):
    try:
        updated_fields = []

        for field in [
                'lat',
                'lng',
                'geocoordinate',
                'altitude',
                'accuracy',
                'heading',
                'speed',
                'data', 
                'config',

            ]:
            if field in data:
                setattr(location_ping, field, data[field])
                updated_fields.append(field)

        if updated_fields:
            location_ping.save(update_fields=updated_fields)


        # Compile the timestamp
        if 'timestamp' in data:
            timestamp_data = data['timestamp']
            timestamp = datetime.datetime(timestamp_data['year'], timestamp_data['month'], timestamp_data['day'], timestamp_data['hour'], timestamp_data['minute'], timestamp_data['second'])
            location_ping.timestamp = timestamp
            location_ping.save()

        return {
            'success': True,
            'location_ping': location_ping,
        }

    except Exception as e:
        return {
            'success': False,
            'errors': ['Error updating the location_ping record'],
        }