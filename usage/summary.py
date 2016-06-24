import csv
import datetime

from log import logging

logger = logging.getLogger('usage.summary')


class Summary:
    """
    This class will group resources by keystone domains then by a group_by
    column. Values of the cost column are summed.
    """
    def __init__(self,
                 domain_client=None,
                 input_file=None,
                 project_id_column=None,
                 cost_column=None,
                 group_by=None):
        """Inits the summary.

        :param domain_client: DomainClient instance.
        :type domain_client: usage.clients.DomainClient
        :param input_file: Name of the input file
        :type input_file: String
        :param project_id_column: Name of the column containing the project id
        :type project_id_column: String
        :param cost_column: Name of the column containing the cost
        :type cost_column: String
        :param group_by: Name of the column to group by
        :type group_by: String
        """
        self.domain_client = domain_client
        self.input_file = input_file
        self.project_id_column = project_id_column
        self.cost_column = cost_column
        self.group_by = group_by

        # Init the data
        self.data = {}
        self.total = 0.0

        # This will store a dictionary of project-ids to domain names.
        self.project_domain_cache = {}

        self.read()

    def output(self):
        indent = ' ' * 4
        print 'Summarizing {} on {}'.format(
            self.input_file,
            datetime.datetime.utcnow().isoformat()
        )
        print 'Grouping on {}'.format(self.group_by)

        domains = self.data.keys()
        domains.sort()
        for domain in domains:
            domain_total = sum(self.data[domain].values())
            print '{}:'.format(domain)
            groups = self.data[domain].keys()
            groups.sort()
            for group in groups:
                print '{}{:<24}{:10.2f}'.format(
                    indent,
                    '{}:'.format(group),
                    self.data[domain][group]
                )
            print '{}{:<24}{:10.2f}'.format(indent, 'Total:', domain_total)
        print 'Total:\t{:10.2f}'.format(self.total)

    def _handle_row(self, row):
        """Handle a report row.

        :param row: Row in iteration of a csv.DictReader
        :type row: Dict
        """
        project_id = row[self.project_id_column]
        group_by = row[self.group_by] or 'Other'
        cost = float(row[self.cost_column])

        domain_data = self.data.setdefault(
            self.get_domain_name(project_id),
            {}
        )
        group_cost = domain_data.get(group_by) or 0
        group_cost += cost
        self.total += cost
        domain_data[group_by] = group_cost

    def read(self):
        with open(self.input_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self._handle_row(row)

    def get_domain_name(self, project_id):
        """Caches domain names for project ids in a dictionary.

        Gets the cached value for project_id if it is cached.
        Gets the domain name and caches it if it is not cached.

        :param project_id: Id of a project
        :type project_id: String
        :return: Human name of a domain
        :rtype: String
        """
        if project_id not in self.project_domain_cache:
            try:
                domain = self.domain_client.get_domain_for_project(project_id)
                self.project_domain_cache[project_id] = domain['name']
            except Exception:
                logger.exception('Unable to retrieve domain for project {}'
                                 .format(project_id))
                self.project_domain_cache[project_id] = 'unknown'
        return self.project_domain_cache[project_id]
