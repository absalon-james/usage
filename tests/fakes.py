class FakeArgs:
    """Fake arguments object."""
    def __init__(self,
                 mtd=False,
                 today=False,
                 last_hour=False,
                 start=None,
                 stop=None,
                 config_file='config_file',
                 definition_filename='definition_filename',
                 output_directory='/basedir',
                 log_level='log_level',
                 show_tags=False,
                 use_stdout=False):
        """Set up the fake argument object.

        :param mtd: Month to date
        :type mtd: Bool
        :param today: Today
        :type today: Bool
        :param last_hour: Last hour
        :type last_hour: Bool
        :param start: Start
        :type start: String
        :param stop: Stop
        :type stop: String
        :param config_file: Config File
        :type config_file: String
        :param definition_filename: Definition filename
        :type definition_filename: String
        :param output_directory: Output directory
        :type output_directory: String
        :param log_level: Log Level
        :type log_level: String
        :param show_tags: Show Tags
        :type show_tags: Bool
        :param use_stdout: Use Stdout
        :type use_stdout: Bool
        """
        self.mtd = mtd
        self.today = today
        self.last_hour = last_hour
        self.start = start
        self.stop = stop
        self.config_file = config_file
        self.definition_filename = definition_filename
        self.output_directory = output_directory
        self.log_level = log_level
        self.show_tags = show_tags
        self.use_stdout = use_stdout


class FakeSample:
    """Fake sample class for testing."""
    def __init__(self,
                 message_id=None,
                 resource_id=None,
                 project_id=None,
                 meter=None,
                 timestamp=None,
                 counter_volume=None,
                 resource_metadata=None,
                 counter_name=None,
                 counter_type=None):
        """Set up the fake sample

        :param message_id: Test message_id. Defaults to 'message_id'
        :type message_id: String
        :param resource_id: Test resource id. Defaults to 'resource_id'
        :type resource_id: String
        :param project_id: Test project id. Defaults to 'project_id'
        :type project_id: String
        :param timestamp: Test timestamp. Defaults to 0
        :type timestamp: Datetime|Float|Integer
        :param counter_volume: Value of the sample. Defaults to 0
        :type counter_volume: Numeric
        :param resource_metadata: Resource metadata. Defaults to {}.
        :type resource_metadata: Dict
        :param counter_name: Name of the counter. Defaults to 'counter_name'
        :type counter_name: String
        :param counter_type: Type of the counter. Defaults to 'counter_type'
        :type counter_type: String
        """
        self.message_id = message_id or 'message_id'
        self.resource_id = resource_id or 'resource_id'
        self.project_id = project_id or 'project_id'
        self.meter = meter or 'meter'
        self.timestamp = timestamp or 0
        self.counter_volume = counter_volume or 0
        self.resource_metadata = resource_metadata or {}
        self.counter_name = counter_name or 'counter_name'
        self.counter_type = counter_type or 'gauge'


class FakeReading:
    """Fake reading object."""
    def __init__(self,
                 start='start',
                 stop='stop',
                 resource_id='resource_id',
                 project_id='project_id',
                 metadata=None,
                 value='value'):
        """Set up fake reading.

        :param start: Reading start. Defaults to 'start'
        :type start: String|Datetime
        :param stop: Reading stop. Defaults to 'stop'
        :type stop: String|Datetime
        :param resource_id: Test resource id. Defaults to 'resource_id'
        :type resource_id: String
        :param project_id: Test project id. Defaults to 'project_id'
        :type project_id: String
        :param metadata: Test metadata. Defaults to {}
        :type metadata: Dict
        :param value: Test value. Defaults to 'value'
        :type value': Any
        """
        self.start = start
        self.usage_start = start
        self.stop = stop
        self.usage_stop = stop
        self.resource_id = resource_id
        self.project_id = project_id
        self.metadata = metadata or {}
        self.value = value
