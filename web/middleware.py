from web.models import Visit


class VisitMiddleware(object):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        if 'admin' in request.path:
            return

        if 'visits' in request.path:
            return

        Visit.objects.create(user=request.user, path=request.path)
