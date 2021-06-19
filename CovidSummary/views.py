from django.http import HttpResponse
from .utils import GetCovidSummary
import json
from common.common import ResponseBaseClass
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class GetCountrySummaryView(ResponseBaseClass):

    def __init__(self,**kwargs):
        self.class_name = 'GetCountrySummaryView'

    def post(self, request):
        request_body = json.loads(request.body)
        #log the request body here
        backend_service = GetCovidSummary(request_body.get('country_name','India'))
        source, response = backend_service.get_response()
        payload = self.generate_response(response,request_body, source)
        #log response here
        return HttpResponse(json.dumps(payload), content_type='application/json')

