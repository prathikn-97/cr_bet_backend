from rest_framework import status
from rest_framework.response import Response


# custom responses
def get_error_response(message):
    return Response({
        "message": message,
        "error": True
    }, status=status.HTTP_400_BAD_REQUEST)


def get_create_success_response(model, data):
    return Response({
        "message": "{} created successfully".format(model),
        "data": data,
        "error": False
    }, status=status.HTTP_201_CREATED)


def get_update_success_response(model, data):
    return Response({
        "message": "{} updated successfully".format(model),
        "data": data,
        "error": False
    }, status=status.HTTP_201_CREATED)


def get_success_ok_response(message, data):
    return Response({
        "message": message,
        "data": data,
        "error": False
    }, status=status.HTTP_200_OK)

def get_success_response(message):
    return Response({
        "message": message,
        "error": False
    })

def get_list_success_response(model, data):
    return Response({
        "message": "{} fetched successfully".format(model),
        "data": data,
        "error": False
    }, status=status.HTTP_200_OK)


def get_delete_success_response(model):
    return Response({
        "message": "{} deleted successfully".format(model),
        "error": False
    }, status=status.HTTP_200_OK)


def get_no_permission_response(message="You do not have permission to perform this action."):
    return Response({
        "message": message,
        "error": True
    }, status=status.HTTP_403_FORBIDDEN)


def get_list_count_success_response(model, data, count):
    return Response({
        "message": "{} fetched successfully".format(model),
        "count": count,
        "data": data,
        "error": False
    }, status=status.HTTP_200_OK)
