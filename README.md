# dotenvyaml

Load environment variables from `.env.yaml` files. Like [python-dotenv](https://github.com/theskumar/python-dotenv), but for YAML.

## Install

```bash
pip install dotenvyaml
```

## Usage

```python
from dotenvyaml import load_dotenvyaml

# Auto-discovers .env.yaml in current directory
load_dotenvyaml()

# Or specify a path
load_dotenvyaml("config/.env.yaml")

# Override existing env vars
load_dotenvyaml(override=True)

# Silent mode (no print output)
load_dotenvyaml(verbose=False)
```

## .env.yaml format

```yaml
PROJECT_ID: "my-project"
REGION: "us-central1"
SERVICE_ACCOUNT: "sa@my-project.iam.gserviceaccount.com"
```
