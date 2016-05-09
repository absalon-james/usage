"""
Provides a cross project client manager.
"""
from keystoneauth1 import loading
from keystoneauth1 import session
from ceilometerclient import client as ceilometerclient


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
        self.nova = None
        self.glance = None
        self.cinder = None
        self.ceilometer = None
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
