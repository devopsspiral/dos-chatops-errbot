from errbot import BotPlugin, botcmd, arg_botcmd, webhook
import docker

client = docker.from_env()


class Dos(BotPlugin):
    """
    dos
    """
    _services = {
        'web': {'image': 'nginx:latest',
                'ports': {'80/tcp': '8090'},
                'info': 'Web created at http://localhost:8090'
                },
        'jenkins': {'image': 'jenkins:latest',
                    'ports': {'8080/tcp': '8080', '5000/tcp': '5000'},
                    'info': 'Jenkins created at http://localhost:8080'
                    },
    }

    def activate(self):
        """
        Triggers on plugin activation
        """
        super(Dos, self).activate()
        self['services'] = []

    @arg_botcmd('service', type=str)
    def docker_start(self, message, service=None):
        """Spawns new service using docker"""

        container_id = self.get_container_id(service)
        if container_id:
            return f'Service {service} already running'
        container = client.containers.run(Dos._services[service]['image'],
                                          detach=True,
                                          remove=True,
                                          ports=Dos._services[service]['ports'])
        services = list(self['services'])
        services.append({'id': container.id, 'name': service})
        self['services'] = services
        return Dos._services[service]['info']

    @arg_botcmd('service', type=str)
    def docker_kill(self, message, service=None):
        """Kills service using docker"""

        container_id = self.get_container_id(service)
        if not container_id:
            return f'No service {service} currently running'
        client.containers.get(container_id).kill()
        services = [item for item in self['services'] if not (service == item.get('name'))]
        self['services'] = services
        return f'{service} killed!'

    @arg_botcmd('service', type=str)
    @arg_botcmd('-t', dest='timestamps', action='store_true')
    def docker_logs(self, message, service=None, timestamps=None):
        """Returns docker logs of a service"""

        container_id = self.get_container_id(service)
        if not container_id:
            return f'No service {service} currently running'
        return client.containers.get(container_id).logs(timestamps=timestamps).decode('UTF-8')

    @botcmd
    def docker_list(self, message, args):
        """Returns list of running services"""

        return [item['name'] for item in self['services']]

    def get_container_id(self, service):
        for item in self['services']:
            if item['name'] == service:
                return item['id']
        return None
