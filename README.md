# usage
A simple approach on getting usage/billing information from ceilometer

### Overview
Ceilometer samples meters at specific events and over intervals of time.
This tool takes all samples for a meter during a time range and computes
a meter reading according to the type of meter(guage|cumulative|delta).

##### Guage Meter
Guage meters are just values at a point in time. This tool sorts guage meter
samples by time in ascending order and approximates the area under the line
that would be made if the sorted samples were assembled into a graph. This
works great for standard sizing meters like vcpus, memory, and storage
capacity. The approximation units would be then be vcpu hours, memory hours,
and storage capacity hours. It is possible to define a rate for a resource
hour and compute a cost for the hours of use of a quanitity of resource.

##### Cumulative Meter
Cumulative meters are counters. This tool subtracts the first sample of a
meter from the last sample of a meter in a given time range to get a reading
of a cumulative meter.

##### Delta meter
Delta meters just measure change from sample to the next. This tool sums all
of the samples in a time range.

### Requirements

- apt-get install python-dev
- pip install python-ceilometerclient
- pip install positional
- pip install babel

### Installation
```shell

# Clone this repo
git clone https://github.com/absalon-james/usage.git

# Setup the configuration file with credentials
mkdir -p /etc/usage
cp usage/sample-usage.yaml /etc/usage/usage.yaml

# Cp the sample report definition
cp usage/sample-report.yaml /etc/usage/report.yaml

# Run setup.py develop

cd usage
python setup.py develop
```

### Configuration
This tool requires access to ceilometer and uses the python-ceilometerclient
to interface with ceilometer. Auth is configured in a yaml file with a
default location of /etc/usage/usage.yaml

```yaml
auth_kwargs:
  auth_url: your_auth_url
  username: your_user_name
  password: your_password
  project_name: your_project_name
  user_domain_name: your_user_domain_name
  project_domain_name: your_project_domain_name
  # Optionally provide endpoint_type
  # endpoint_type: internalURL
```

## Console Scripts
This tool provides three console scripts: usage-report, usage-summary, and usage-licensing

### usage-report
This console script creates a report in csv format according to a definition
file. The definition file describes the columns of the report and how to get
information for each column in the report.

```shell
# Basic usage
usage-report

# Is the same as
usage-report --config-file /etc/usage/usage.yaml --definition-file /etc/usage/report.yaml --output-directory /etc/usage/reports --mtd

# --config-file - Location of yaml file with auth kwargs
# --definition-file - Location of yaml file describing the report
# --output-directory - Directory to save reports in

# Time ranges are specified 4 ways

# Month to date - Beginning of this month until now
# Csv will be written to <output_directory>/mtd/yyyy_mm.csv
usage-report --mtd

# Today - Beginning of today until now
# Csv will be written to <output_directory>/daily/yyyy_mm_dd.csv
usage-report --today

# The last hour - Only the last hour
# Csv will be written to <output_directory>/hourly/yyyy/mm/dd/<timerange>.csv
usage-report --last-hour

# Arbitrary time range
# Csv will be written to <output_directory>/other/2016-07-01T00:00:00_to_2016-07-20T16:47:20.233169.csv
usage-report --start 2016-07-01 00:00:00 --stop 2016-07-20 16:47:20.233169

# The csv can also be written to stdout for redirection to a file of the user's choice.
usage-report --use-stdout > somefile.csv
```

##### The report definition file.
This file is a yaml description of a report. It consists of columns and items.
Columns will have a name and a function. The name is for  output only, the
function determines what goes into a column. Items describe meters to be
included in the report. Items also include rates.

This tool provides a basic set of field functions. All field functions are
pluggable and installed via python entry points. It is easy to create and use
other field functions not provided by this tool.

There will be one row in the csv per meter per resource that has the meter.
Consider an environment where there are 10 VM resources. There will be 20 rows
in the csv. 10 rows are for vcpus meters and 10 rows are for memory meters.

```yaml
name: 'mtd'
currency_code: USD
billing_entity: OpenStack

# The columns definition
columns:
  # name: will be the name of the column in the csv report
  # func: Name of the field function to use.
  - name: Resource Id
    func: resource_id
  - name: Project Id
    func: project_id
  - name: Meter Name
    func: meter_name
  - name: user:appid
    func: metadata:appid
  - name: user:environment
    func: metadata:environment
  - name: Item Rate
    func: item_rate
  - name: Cost
    func: cost

# The items definition
items:
  # Meter name needs to be the same in ceilometer
  - meter_name: vcpus
    billing_entity: OpenStack
    line_item_type: Usage
    product_code: Compute
    usage_type: Vcpu Hours
    operation: Runinstances
    currency_code: USD
    # Cost per unit
    item_rate: 0.2
    description: cpu Hours
    product_name: Compute

  - meter_name: memory
    billing_entity: OpenStack
    line_item_type: Usage
    product_code: Compute
    usage_type: Memory GB Hours
    operation: Runinstances
    currency_code: USD
    item_rate: 0.5
    description: Memory GB Hours
    product_name: Compute
    conversion: megabytes_to_gigabytes
```

### usage-summary.

This is a tool that accepts a previously generated csv report and summarizes
cost by keystone domain and by a group by field.

```shell
# Basic usage
usage-summary somereport.csv

# Is the same as
usage-summary --config-file /etc/usage/usage.yaml --group-by user:appid --project-id-field 'Project Id' --cost-field Cost

# --config-file - Location of yaml file with auth kwargs
# --group-by - Name of column to group costs by under keystone domain
# --project-id-field - Name of column in report containing a resource's project id.
# --cost-field - Name of column in report containing a line item cost.
```

### usage-licensing
This is a tool that attempts to get some insight into licensing costs by
leveraging the image metadata that is captured by certain VM meters like
vcpus and memory.

This is only useful when software information such
as edition and version are tracked in image metadata. If a VM is created with
a base windows image and sqlserver is installed later, this tool will not
have any visibility.

It is often useful to have a separate licensing report definition
that requests image metadata information.

A sample licensing report definition file:
```yaml
name: 'mtd'
currency_code: USD
billing_entity: OpenStack
columns:
  - name: Resource Id
    func: resource_id
  - name: Project Id
    func: project_id
  - name: user:environment
    func: metadata:environment
  - name: image:OS Distro
    func: image_metadata:os_distro
  - name: image:OS Version
    func: image_metadata:os_version
  - name: image:Oracle Edition
    func: image_metadata:sw_database_oracle_edition
  - name: image:Oracle Version
    func: image_metadata:sw_database_oracle_version
  - name: image:SQLServer Edition
    func: image_metadata:sw_database_sqlserver_edition
  - name: image:SQLServer Version
    func: image_metadata:sw_database_sqlserver_version
  - name: Hours
    func: hours
items:
  - meter_name: vcpus
    billing_entity: OpenStack
    line_item_type: Usage
    product_code: Compute
    usage_type: Vcpu Hours
    operation: Runinstances
    currency_code: USD
    item_rate: 0.2
    description: cpu Hours
    product_name: Compute
```

A sample licensing definition that uses output from the report above:
```yaml
licensers:
  # Name of the licenser
  - type: OracleCount
    project_id_field: Project Id
    costs:
      enterprise:
        12.1.0.2: 0
      standard:
        12.1.0.2: 0

  - type: OracleHours
    project_id_field: Project Id
    hours_field: Hours
    costs:
      enterprise:
        12.1.0.2: 2
      standard:
        12.1.0.2: 1

  - type: SQLServerCount
    project_id_field: Project Id
    costs:
      enterprise:
        '2016': 0
      standard:
        '2016': 0

  - type: SQLServerHours
    project_id_field: Project Id
    hours_field: Hours
    costs:
      enterprise:
        '2016': 5
      standard:
        '2016': 10

  - type: WindowsCount
    project_id_field: Project Id
    costs:
      windows:
        'NT 10.0': 0
        'NT 6.3': 0

  - type: WindowsHours
    project_id_field: Project Id
    costs:
      windows:
        'NT 10.0': 30
        'NT 6.3': 20
```

A licenser is a python class installed via python entry points. The included
licensers can be used or custom licensers can be created and installed.

```shell
# Basic usage
usage-licensing somefile_licensing_report.csv

# Is the same as
usage-licensing --config-file /etc/usage/usage.yaml --definition-file /etc/usage/licensing.yaml somefile_licensing_report.csv

# --config-file - Location of yaml file with auth kwargs
# --definition-file - Location of yaml file listing the licensers.
```
