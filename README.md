# usage
A simple approach on getting usage/billing information from ceilometer

### Still a work in progress and not meant to be used in production.
- Works for gauge meters where resource metadata includes created_at and deleted_at
- Works for cumulative meters
- Delta meters maybe added in the future
- A console script/cli tool is planned.
- Some work may have to be done to configure cinder notifications and audits.

### Sample configuration
```yaml
auth_kwargs:
  auth_url: your_auth_url
  username: your_user_name
  password: your_password
  project_name: your_project_name
  user_domain_name: your_user_domain_name
  project_domain_name: your_project_domain_name
```

### Requirements
- python-ceilometerclient

### Installation
```shell

# Clone this repo
git clone https://github.com/absalon-james/usage.git

# Setup the configuration file with credentials
mkdir -p /etc/usage
cp usage/sample-usage.yaml /etc/usage/usage.yaml

# Run setup.py develop

cd usage
python setup.py develop
```

### How to use:
```python
import datetime
from usage import config
from usage.clients import ClientManager
from usage.meter import Meter

conf = config.load('/etc/usage/usage.yaml')
manager = ClientManager(**conf.get('auth_kwargs',{}))
ceilometer = manager.get_ceilometer()

# Get vcpu hours for the last 5 hours

# Setup time frame
now = datetime.datetime.utcnow()
five_hours_ago = now - datetime.timedelta(hours=5)

# 'vcpus' is the name of a meter in ceilometer
m = Meter(ceilometer, 'vcpus')
reading = m.read(start=five_hours_ago, stop=now)
print "Vcpu hours for the last 5 hours: {}".format(reading)

# For a more detailed example look at main.py
```
