from log import logging

logger = logging.getLogger('usage.domain_cache')

_CACHE = {}
_DOMAIN_CLIENT = None


def set_domain_client(domain_client):
    global _DOMAIN_CLIENT
    _DOMAIN_CLIENT = domain_client


def get_domain_name(project_id):

    if _DOMAIN_CLIENT is None:
        raise Exception('Unable to retrieve domain for project {}. '
                        'Please set the domain client first.')

    if project_id not in _CACHE:
        try:
            domain = _DOMAIN_CLIENT.get_domain_for_project(project_id)
            _CACHE[project_id] = domain['name']
        except Exception:
            logger.exception('Unable to retrieve domain for project {}'
                             .format(project_id))
            _CACHE[project_id] = 'unknown'

    return _CACHE[project_id]
