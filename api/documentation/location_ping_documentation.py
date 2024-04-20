from drf_yasg import openapi
from api.documentation.common_elements import date_time_properties


# Base Customer Schema
def base_location_ping_schema(required_fields=[], include_fields=None):
    all_properties = {
        'location_ping_id': openapi.Schema(type=openapi.TYPE_STRING),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        # Add other fields here
    }
    properties = {k: v for k, v in all_properties.items() if include_fields is None or k in include_fields}
    
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=properties,
        required=required_fields
    )

# Function to create a request body schema
def create_request_body_schema(base_schema, description=""):
    return openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=base_schema,
        description=description
    )

# Customer list response object
location_ping_list_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'location_pings': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_location_ping_schema(), description='List of location_pings'),
        'page': openapi.Schema(type=openapi.TYPE_INTEGER, description='Current page number'),
        'pages': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of pages'),
        'records_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of records')
    },
    description='Customer list response object with pages and record count'
)

# Customer response object
location_ping_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'location_ping': base_location_ping_schema()
    },
    description='Customer object'
)

# Adding response object
location_ping_not_added_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_location_ping_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a location_ping that could not be added'
)
add_location_pings_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'location_pings_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_location_ping_schema(), description='List of successfully added location_pings'),
        'location_pings_not_added': openapi.Schema(type=openapi.TYPE_ARRAY, items=location_ping_not_added_entry_schema, description='Details of location_pings that could not be added')
    },
    description='Response for the add location_pings operation'
)

# Updating response object
location_ping_not_updated_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_location_ping_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a location_ping that could not be updated'
)
update_location_pings_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'location_pings_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_location_ping_schema(), description='List of successfully updated location_pings'),
        'location_pings_not_updated': openapi.Schema(type=openapi.TYPE_ARRAY, items=location_ping_not_updated_entry_schema, description='Details of location_pings that could not be updated')
    },
    description='Response for the add location_pings operation'
)

# Archiving response object
location_ping_not_archived_entry_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position in the original submitted list'),
        'submitted_object': base_location_ping_schema(),
        'errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='List of error messages')
    },
    description='Details of a location_ping that could not be archived'
)
archive_location_pings_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'location_pings_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_location_ping_schema(), description='List of successfully archived location_pings'),
        'location_pings_not_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=location_ping_not_archived_entry_schema, description='Details of location_pings that could not be archived')
    },
    description='Response for the add location_pings operation'
)
destroy_location_pings_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'location_pings_archived': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_location_ping_schema(), description='List of successfully archived location_pings'),
    },
    description='Response for the add location_pings operation'
)

# Generate schemas for add and update operations
location_ping_add_schema = base_location_ping_schema(required_fields=['name'])
location_ping_update_schema = base_location_ping_schema(required_fields=['location_ping_id'])
location_ping_archive_schema = base_location_ping_schema(required_fields=['location_ping_id'], include_fields=['location_ping_id'])

# Function to create a request body schema that includes 'location_pings' key
def create_location_pings_key_request_body_schema(base_schema, description=""):
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'location_pings': openapi.Schema(type=openapi.TYPE_ARRAY, items=base_schema, description=description)
        },
        required=['location_pings']
    )

# Generate request body schemas with 'location_pings' key
location_ping_add_request_body = create_location_pings_key_request_body_schema(location_ping_add_schema, "List of location_pings to add")
location_ping_update_request_body = create_location_pings_key_request_body_schema(location_ping_update_schema, "List of location_pings to update")
location_ping_archive_request_body = create_location_pings_key_request_body_schema(location_ping_archive_schema, "List of location_pings to archive")

# Customer response schema
location_ping_schema = base_location_ping_schema()