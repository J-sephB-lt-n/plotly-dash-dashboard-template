# Plotly Dash Data Dashboard Template

An example of a data dashboard built using Plotly Dash in python.

How it looks on a laptop (macbook air):

![](./screenshots/macbook-air.png)

How it looks on a mobile phone (iPhone XR):

<img src="./screenshots/iphone-xr.png" width="250"/>

Deploy locally:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python dash_app.py
```

Deploy on a Google Cloud Run service:

```bash
GCP_PROJ_ID="your_google_cloud_project_id_here"
GCP_REGION_NAME="region_in_which_to_deploy_service" # e.g. "africa-south1"
GCP_ARTIFACT_REG_REPO_NAME="your-artifact-registry-repo-name"
API_NAME="joes-example-dashboard"
source build_deploy_cloud_run.sh
```

Known issues:

- Plots on small screens are being cropped on Firefox browser (this is to do with the Firefox implementation of the `zoom` CSS property)

- The dashboard does not look good yet on very large screens
