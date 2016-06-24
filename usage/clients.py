"""
Provides a cross project client manager.
"""
import keystoneclient

from keystoneauth1 import loading
from keystoneauth1 import session
from ceilometerclient import client as ceilometerclient


class DomainClient(object):
    """The openstackclient is lame."""
    def __init__(self, **kwargs):
        """Create the adapter."""
        kwargs.setdefault('user_agent', 'python-myclient')
        kwargs.setdefault('service_type', 'identity')
        kwargs.setdefault('version', '3')
        self.http = keystoneclient.adapter.Adapter(**kwargs)

    def get_project(self, project_id):
        """Get project data.

        :param project_id: Id of the project.
        :type project_id: String
        :return: Project data
        :rtype: Dict
        """
        data = self.http.get('/projects/{}'.format(project_id)).json()
        data = data['project']
        return data

    def get_domain(self, domain_id):
        """Get domain data.

        :param domain_id: Id of the domain
        :type domain_id: String
        :return: Domain data
        :rtype: Dict
        """
        data = self.http.get('/domains/{}'.format(domain_id)).json()
        data = data['domain']
        return data

    def get_domain_for_project(self, project_id):
        """Get domain data for a project.

        :param project_id: Id of the project
        :type project_id: String
        :return: Domain data
        :rtype: Dict
        """
        domain_id = self.get_project(project_id)['domain_id']
        return self.get_domain(domain_id)


class ClientManager(object):
    """Object that manages multiple openstack clients.

    Operates with the intention of sharing one keystone auth session.
    """
    def __init__(self, **kwargs):
        """Inits the client manager.

        :param auth_url: String keystone auth url
        :param username: String openstack username
        :param password: String openstack password
        :param project_id: String project_id - Tenant uuid
        """
        self.session = None
        self.ceilometer = None
        self.domain = None
        self.auth_kwargs = kwargs

    def get_session(self):
        """Get a keystone auth session.

        :returns: keystoneauth1.session.Session
        """
        if self.session is None:
            loader = loading.get_plugin_loader('password')
            auth = loader.load_from_options(**self.auth_kwargs)
            self.session = session.Session(auth=auth)
        return self.session

    def get_ceilometer(self, version='2'):
        """Get a ceilometer client instance.

        :param version: String api version
        :return: cinderclient.client
        """
        if self.ceilometer is None:
            self.ceilometer = ceilometerclient.get_client(
                version,
                **self.auth_kwargs
            )
        return self.ceilometer

    def get_domain(self):
        """Get an domain client instance.

        :return: Domain client instance.
        :rtype: DomainClient
        """
        if self.domain is None:
            self.domain = DomainClient(session=self.get_session())
        return self.domain
