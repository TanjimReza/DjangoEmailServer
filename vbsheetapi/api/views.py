from django.shortcuts import render
from rest_framework import response
from rest_framework.decorators import api_view


@api_view(['GET'])
def getData(request):
    data = {
        'data': 'data'
    }
    return response.Response(data)
