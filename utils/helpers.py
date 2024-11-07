import json
import requests
from django.conf import settings
from rest_framework import serializers
# from billing_management_backend.settings.logging import logger
import logging
logger = logging.getLogger(__name__)


def get_user_from_token(uuid, request):
    #  data = {
    #         "type":"virtueleBilling",
    #         "userId":149,
    #         "token":"sdadas",
    #         "companyId":3
    #     }
    #  return data
    try:
        # server_url = settings.AUTH_SERVICE_DOMAIN
        headers = {
            'Authorization': 'Bearer ' + uuid,
            'Content-Type': 'application/json'
        }
        # print(headers, 'headers')

        response = requests.get(
            f"https://clbdev.virtuele.us/api/user/token-info", headers=headers)
        print(response.text, 'response')
        if response.status_code == 200:
            data = response.json()
            value = json.loads(data["company"])
            # print(request.GET, "request.GET.get('type', None)")
            value['type'] = request.GET.get('type', None)
            value['userId'] = request.GET.get('userId', None)
            value['token'] = uuid
            # print(value, 'value')
            return value
        # else:
            # logger.error(f"Authentication API : {response.text}")
    except Exception as error:
        logger.error(f"Authentication API : {error}")
        print(error, 'error')
        # data = {
        #     "type":"virtueleBilling",
        #     "userId":149,
        #     "token":"sdadas",
        #     "companyId":3
        # }
        return None


def get_user(request):
    user = {}
    if request.user.get("type") == "virtueleBilling":
        if request.data.get("company_id"):
            user["user_id"] = request.data.get("company_id")
            user['company_id'] = request.data.get("company_id")
        else:
            raise serializers.ValidationError("Company ID Not Found !!!")
    else:
        user["user_id"] = request.user.get("userId")
        user["company_id"] = request.user.get("companyId")
    print("*"*20)
    print("get user", user)
    print("*"*20)
    return user
