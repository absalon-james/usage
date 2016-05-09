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

# Run setup.py develop

cd usage
python setup.py develop
```
