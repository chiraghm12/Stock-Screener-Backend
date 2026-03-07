import json
import logging
from urllib.parse import parse_qs

# from rest_framework_simplejwt.backends import TokenBackend
# from rest_framework_simplejwt.exceptions import TokenBackendError

# from user.models import MoneyTrackerUser

stock_screener_logger = logging.getLogger("stock_screener_logger")


# def get_user(request):
#     """
#     Method for get user from Authentication Token
#     """
#     try:
#         # get access token
#         header = request.META.get("HTTP_AUTHORIZATION", "")
#         parts = header.split()

#         if len(parts) == 2 and parts[0].lower() == "bearer":
#             token = parts[1]
#         else:
#             return None

#         if token:
#             # decode the token aget user data
#             user_data = TokenBackend(algorithm="HS256").decode(token, verify=False)
#             # get user
#             user = MoneyTrackerUser.objects.get(id=user_data["user_id"])
#             return user
#         else:
#             # condition for login log
#             if "login" in request.path:
#                 # condition for login in admin portal
#                 if "admin" in request.path:
#                     # parse the body data and get the email
#                     body_data = request.body.decode("utf-8")
#                     parsed_data = parse_qs(body_data)
#                     email = parsed_data.get("email", [""])[0]
#                 else:
#                     # get the email
#                     payload = json.loads(request.body.decode("utf-8"))
#                     email = payload.get("email", "")
#                 user = MoneyTrackerUser.objects.get(email=email)
#                 return user
#             return None
#     except TokenBackendError:
#         return None
#     except MoneyTrackerUser.DoesNotExist:  # pylint: disable=no-member
#         return None


class RequestLoggingMiddleware:
    """
    Middleware for logging incoming HTTP requests and responses.

    This middleware captures and logs detailed information about each
    incoming HTTP request and the corresponding response. It logs details
    such as the request method, user information, request path, origin, remote address,
    and any associated form data, payload, or query parameters.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        parsed_data = None
        payload = None
        request_body = None
        try:
            # get user and email
            # user = get_user(request)
            # request.user = user if user else request.user
            if not request.user.is_anonymous:
                email = request.user.email
            else:
                email = "No Authentication"

            # handle POST, PATCH, PUT methods
            if request.method in ["POST", "PATCH", "PUT"]:
                # for log multipart/form-data request
                if request.content_type.startswith("multipart/form-data"):
                    form_data = request.POST.dict()
                    file_data = request.FILES
                    form_data["uploaded_files"] = list(file_data.items())

                    stock_screener_logger.info(  # pylint: disable=W1203
                        f"Incoming request({id(request)}): {request.method} - "
                        f"User: {email} - Origin: {request.META.get('HTTP_ORIGIN')} - "
                        f"{request.path} - {request.META['REMOTE_ADDR']} - "
                        f"Form Data: {form_data}"
                    )
                else:
                    # for json body request
                    request_body = (
                        request.body.decode("utf-8") if request.body else None
                    )
                    # handle request which is not of admin portal.
                    if "/admin/" not in str(request.get_full_path()):
                        payload = json.loads(request_body) if request_body else None
                        stock_screener_logger.info(  # pylint: disable=W1203
                            f"Incoming request({id(request)}): {request.method} - "
                            f"User: {email} - Origin: {request.META.get('HTTP_ORIGIN')} - "
                            f"{request.path} - {request.META['REMOTE_ADDR']} - "
                            f"Payload:{payload}"
                        )
                    else:
                        # handle requests of admin portal
                        parsed_data = parse_qs(request_body)
                        stock_screener_logger.info(  # pylint: disable=W1203
                            f"Incoming request({id(request)}): {request.method} - "
                            f"User: {email} - "
                            f"{request.path} - {request.META['REMOTE_ADDR']} - "
                            f"Payload: {parsed_data if parsed_data else ' '}"
                        )
            elif request.method == "GET":
                # handle GET requests
                # get query params if exists.
                query_params = request.GET.dict()
                if query_params:
                    stock_screener_logger.info(  # pylint: disable=W1203
                        f"Incoming request({id(request)}): {request.method} - "
                        f"User: {email} - Origin: {request.META.get('HTTP_ORIGIN')} - "
                        f"{request.path} - {request.META['REMOTE_ADDR']} "
                        f"query_params:{query_params}"
                    )
                else:
                    stock_screener_logger.info(  # pylint: disable=W1203
                        f"Incoming request({id(request)}): {request.method} - "
                        f"User: {email} - Origin: {request.META.get('HTTP_ORIGIN')} - "
                        f"{request.path} - {request.META['REMOTE_ADDR']}"
                    )
            elif request.method == "DELETE":
                # handle DELETE requests.
                stock_screener_logger.info(  # pylint: disable=W1203
                    f"Incoming request({id(request)}): {request.method} - "
                    f"User: {email} - Origin: {request.META.get('HTTP_ORIGIN')} - "
                    f"{request.path} - {request.META['REMOTE_ADDR']}"
                )

            # get response
            response = self.get_response(request)

            # log the response which is not for admin portal requests
            if "/admin/" not in str(request.get_full_path()):
                # get the text from response and log
                text = response.get("status_text", response.reason_phrase)
                # log the response for different status code
                if response.status_code == 500:
                    stock_screener_logger.info(  # pylint: disable=W1203
                        f"Response for ({id(request)}): {response.status_code} - {text}"
                    )
                elif response.status_code in [400, 401, 403]:
                    stock_screener_logger.info(  # pylint: disable=W1203
                        f"Response for ({id(request)}): {response.status_code} - {text} - "
                        f"response:{response.data}"
                    )
                else:
                    stock_screener_logger.info(  # pylint: disable=W1203
                        f"Response for ({id(request)}): {response.status_code} - {text}"
                    )
            # return response
            return response
        except Exception as error:  # pylint: disable=W0718
            stock_screener_logger.error(
                f"{error}", exc_info=True
            )  # pylint: disable=W1203
