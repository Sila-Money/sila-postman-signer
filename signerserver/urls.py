""" signerserver URL Configuration

    The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/2.2/topics/http/urls/
"""

from django.urls import path
from signerserver import views


handler404 = views.handler404
handler500 = views.handler500

urlpatterns = [
    path('generate_private_key', views.generate_private_key_view),
    path('generate_signature', views.generate_signature_view),
    path('forward', views.forwarder_view),
]
