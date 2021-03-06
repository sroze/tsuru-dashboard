from django.template.response import TemplateResponse
from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from auth.views import LoginRequiredView

import requests
import json


class ListService(LoginRequiredView):
    def get(self, request):
        url = "{0}/services/instances".format(settings.TSURU_HOST)
        authorization = {'authorization': request.session.get('tsuru_token')}
        services = requests.get(url, headers=authorization).json()
        return TemplateResponse(request, "services/list.html", {'services': services})


class ServiceInstanceDetail(LoginRequiredView):
    def apps(self, instance):
        url = "{0}/apps".format(settings.TSURU_HOST)
        response = requests.get(url, headers=self.authorization)
        app_list = []
        for app in response.json():
            if app['name'] not in instance['Apps']:
                app_list.append(app['name'])
        return app_list

    @property
    def authorization(self):
        return {'authorization': self.request.session.get('tsuru_token')}

    def get_instance(self, instance_name):
        url = "{0}/services/instances/{1}".format(settings.TSURU_HOST,
                                                  instance_name)
        response = requests.get(url, headers=self.authorization)
        return response.json()

    def get(self, request, *args, **kwargs):
        instance_name = kwargs["instance"]
        instance = self.get_instance(instance_name)
        apps = self.apps(instance)
        return TemplateResponse(request, "services/detail.html",
                                {'instance': instance, 'apps': apps})


class ServiceAdd(LoginRequiredView):
    def post(self, request, *args, **kwargs):
        service_name = kwargs["service_name"]
        authorization = {'authorization': request.session.get('tsuru_token')}
        tsuru_url = '{0}/services/instances'.format(settings.TSURU_HOST)
        data = {"name": request.POST["name"],
                "service_name": service_name}
        requests.post(tsuru_url,
                      data=json.dumps(data),
                      headers=authorization)
        return redirect(reverse('service-list'))

    def get(self, request, *args, **kwargs):
        service_name = kwargs["service_name"]
        return TemplateResponse(request, "services/add.html",
                                {'service': {"name": service_name}})


class Bind(LoginRequiredView):
    def post(self, request, *args, **kwargs):
        app = request.POST["app"]
        instance = kwargs["instance"]
        authorization = {'authorization': request.session.get('tsuru_token')}
        tsuru_url = '{0}/services/instances/{1}/{2}'.format(
            settings.TSURU_HOST, instance, app)
        requests.put(tsuru_url, headers=authorization)
        return redirect(reverse('service-detail', args=[instance]))


class Unbind(LoginRequiredView):
    def get(self, request, *args, **kwargs):
        app = kwargs["app"]
        instance = kwargs["instance"]
        authorization = {'authorization': request.session.get('tsuru_token')}
        tsuru_url = '{0}/services/instances/{1}/{2}'.format(
            settings.TSURU_HOST, instance, app)
        requests.delete(tsuru_url, headers=authorization)
        return redirect(reverse('service-detail', args=[instance]))


class ServiceRemove(LoginRequiredView):
    def get(self, request, *args, **kwargs):
        instance = kwargs["instance"]
        authorization = {'authorization': request.session.get('tsuru_token')}
        tsuru_url = '{0}/services/instances/{1}'.format(
            settings.TSURU_HOST, instance)
        requests.delete(tsuru_url,
                        headers=authorization)
        return redirect(reverse('service-list'))
