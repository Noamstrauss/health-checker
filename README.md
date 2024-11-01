## HTTP Health Checker
A simple Python application that monitors HTTP endpoints and tracks their availability percentage.

---

### Prerequisites

* Python 3.7 or higher
* pip

### Installation

Clone this repository:

```bash
git clone https://github.com/Noamstrauss/health-checker.git
cd health-checker
```
Create a virtual environment (optional but recommended):

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

### Configuration
Create a YAML file (e.g., endpoints_config.yaml) with your endpoints:
```yaml
- name: fetch rewards index page
  url: https://www.fetchrewards.com/

- name: Google
  headers:
    user-agent: fetch-synthetic-monitor
  method: GET
  url: https://google.com

- name: Twitter
  headers:
    user-agent: fetch-synthetic-monitor
  method: GET
  url: https://twitter.com
```
### Usage
  Run the application with:
  ```bash
  python health_checker.py -c endpoints_config.yaml
  ```

Additional options:
```bash 
# Run with debug logging
python health_checker.py -c endpoints_config.yaml --log-level DEBUG
```

Show help:
```bash
python health_checker.py --help
```