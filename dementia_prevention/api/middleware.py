class LogBlockedRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/login/' and request.method == 'GET':
            print(
                f"Blocked GET request from: {request.META.get('HTTP_REFERER')}\n"
                f"User-Agent: {request.META.get('HTTP_USER_AGENT')}\n"
                f"IP: {request.META.get('REMOTE_ADDR')}"
            )
        return self.get_response(request)
    