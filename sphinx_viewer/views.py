from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


class EpubFileUploadView(View):
    def get(self, request):
        return render(request, template_name='index.html')


class ReturnHtmlView(View):
    def post(self, request):
        file = request.FILES.getlist('epub')
        if not file:
            return render(request, template_name='error.html')
        # conversion and HTML returning logic
        return HttpResponse("ok")
