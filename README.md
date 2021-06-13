# 2nd Annual MLOps World: Machine Learning in Production Conference

![](image.png)


##
[![Linkedin Badge](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/aniruddha-choudhury-5a34b511b/)


## ⚡ Technologies

![Python](https://img.shields.io/badge/-Python-black?style=flat-square&logo=Python)
![Redis](https://img.shields.io/badge/-Redis-black?style=flat-square&logo=Redis)
![Docker](https://img.shields.io/badge/-Docker-black?style=flat-square&logo=docker)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-black?style=flat-square&logo=google-cloud)
![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github)
![Kubernetes](https://img.shields.io/badge/kubernetes-326ce5.svg?&style=for-the-badge&logo=kubernetes&logoColor=white)
<code><img height="20" src="https://github.com/aniruddhachoudhury/Credit-Risk-Model/blob/master/avatar?raw=true">Kubeflow</code>


## Feature Store with Kubeflow in Google Cloud Platform

---

##  Setting up Kubeflow with Feast on GCP

### Step 1 : Setup Environment

- Using Google cloud shell
    
    Log into the Google cloud console `https://console.cloud.google.com/` . Open `cloud shell`. Make sure you are connected to correct project envionrment. All of other dependencies such as `gcloud, kubectl, helm, make` is already available and configured.
    
    Currently default Helm version on Google cloud shell is `v3.x`. You can check using `helm version --client`.But if you not willing to use cloud shell please visit the [helm install link](https://helm.sh/docs/intro/install/)
    
    
 - gcloud components
 
```bash
sudo gcloud components install kubectl kpt anthoscli beta
gcloud components update
```
- Kustomize Installation

```bash
# Detect your OS and download corresponding latest Kustomize binary
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash
# Add the kustomize package to your $PATH env variable
sudo mv ./kustomize /usr/local/bin/kustomize
```
- yq v3 jq Installation

```bash
sudo wget https://github.com/mikefarah/yq/releases/download/3.4.1/yq_linux_amd64 -O /usr/bin/yq && sudo chmod +x /usr/bin/yq
yq --version
sudo apt install jq
```
    
### Step 2 : Kubeflow Setup
<img src="https://github.com/aniruddhachoudhury/Credit-Risk-Model/blob/master/avatar?raw=true" width="200"/>

Kubeflow is an end-to-end Machine Learning (ML) platform for Kubernetes, it provides components for each stage in the ML lifecycle, from exploration through to training and deployment. Operators can choose what is best for their users, there is no requirement to deploy every component. 
  
Please visit the following link to install kubeflow  for respective Cloud [Kubeflow Installation Link](https://www.kubeflow.org/docs/started/installing-kubeflow/)

Steps to install kubeflow `1.3` in Google Cloud Platform
   - **GCP API Enabled** : You can also enable these APIs by running the following command in Cloud Shell, [setup project link](https://www.kubeflow.org/docs/distributions/gke/deploy/project-setup/)
   
   ```bash
   gcloud services enable \
          compute.googleapis.com \
          container.googleapis.com \
          iam.googleapis.com \
          servicemanagement.googleapis.com \
          cloudresourcemanager.googleapis.com \
          ml.googleapis.com \
          iap.googleapis.com \
          sqladmin.googleapis.com \
          meshconfig.googleapis.com 
  ```
  - **Oauth Client** :  Cloud Identity-Aware Proxy (Cloud IAP) when deploying Kubeflow on Google Cloud, then you must follow these instructions to create an OAuth client for use with Kubeflow, [oauth setup link](https://www.kubeflow.org/docs/distributions/gke/deploy/oauth-setup/)
  Make note that you can find your `OAuth client credentials` in the credentials section of the Google Cloud Console. You need to retrieve the client ID and client secret later when you’re ready to enable Cloud IAP.

 - **Deploy Management cluster** : Management cluster which you will use to deploy one or more instances of Kubeflow.The management cluster is used to run Cloud Config Connector. Cloud Config Connector is a Kubernetes addon that allows you to manage Google Cloud resources through Kubernetes. [Link](https://www.kubeflow.org/docs/distributions/gke/deploy/management-setup/)
---
![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")

**Clone the GitHub repository and check out the v1.3.0 tag & go to directory for Management cluster configurations** 
 ```bash
 git clone https://github.com/kubeflow/gcp-blueprints.git 
 cd gcp-blueprints
 git checkout tags/v1.3.0 -b v1.3.0
 cd management
 ```
**Configure Environment Variables**
 ```bash
MGMT_PROJECT=<the project where you deploy your management cluster>
MGMT_DIR=<path to your management cluster configuration directory>
MGMT_NAME=<name of your management cluster>
LOCATION=<location of your management cluster>
```
**Configure kpt setter values & find out setters exist in a package**
```bash
kpt cfg set -R . name "${MGMT_NAME}"
kpt cfg set -R . gcloud.core.project "${MGMT_PROJECT}"
kpt cfg set -R . location "${LOCATION}"
kpt cfg list-setters .
```
**Deploy Management Cluster**
```bash
#Deploy the management cluster by applying cluster resources
make apply-cluster
#Create a kubectl context for the management cluster, it will be named ${MGMT_NAME}
make create-context
#Install the Cloud Config Connector
make apply-kcc
```
- **Deploy Kubeflow cluster** :Your management cluster will need a namespace setup to administer the Google Cloud project where Kubeflow will be deployed. [Link](https://www.kubeflow.org/docs/distributions/gke/deploy/deploy-cli/)

---

![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 2")

**Run the following command to pull upstream manifests from kubeflow/manifests repository**
```bash
cd..
cd kubeflow
bash ./pull-upstream.sh
```
**Set environment variables with OAuth Client ID and Secret for IAP**

```bash
export CLIENT_ID=<Your CLIENT_ID>
export CLIENT_SECRET=<Your CLIENT_SECRET>
```
**Configure Environment Variables**
```bash
export KF_PROJECT=<google-cloud-project-id>
# You can get your project number by running this command
# (replace ${KF_PROJECT} with the actual project ID):
# gcloud projects describe --format='value(projectNumber)' "${KF_PROJECT}"
export KF_PROJECT_NUMBER=<google-cloud-project-number>
# ADMIN_EMAIL env var is the Kubeflow admin's email address, it should be
# consistent with login email on Google Cloud.
# Example: admin@gmail.com
export ADMIN_EMAIL=<administrator-full-email-address>
# The MGMT_NAME env var contains the name of your management cluster created in management cluster setup:
export MGMT_NAME=<management-cluster-name>
# The MGMTCTXT env var contains a kubectl context that connects to the management cluster. By default, management cluster setup creates a context named ${MGMT_NAME} for you.
export MGMTCTXT="${MGMT_NAME}"

# KF_NAME env var is name of your new Kubeflow cluster.
export KF_NAME=kubeflow
# The CloudSQL instance and Cloud Storage bucket instance are created during deployment, so you should make sure their names are not used before.
export CLOUDSQL_NAME="${KF_NAME}-kfp"
# Note, Cloud Storage bucket name needs to be globally unique across projects.So we default to a name related to ${KF_PROJECT}.
export BUCKET_NAME="${KF_PROJECT}-kfp"
# LOCATION can either be a zone or a region, that determines whether the deployed,Specify LOCATION as a region like the following line to create a regional Kubeflow cluster.
export LOCATION=us-central1-c
# REGION should match the region part of LOCATION.
export REGION=us-central1
# Preferred zone of Cloud SQL. Note, ZONE should be in REGION.
export ZONE=us-central1-c
# Anthos Service Mesh version label
export ASM_LABEL=asm-193-2
```

**Configure kpt setters as environement variables in packages and finding out which setters exist in a package**

```bash
bash kpt-set.sh
kpt cfg list-setters .
kpt cfg list-setters common/managed-storage
kpt cfg list-setters apps/pipelines
```

**Management cluster config**

```bash
kubectl config use-context "${MGMTCTXT}"
kubectl create namespace "${KF_PROJECT}"
```
**Authorize Cloud Config Connector for each Kubeflow project**

```bash
MGMT_PROJECT=<the project where you deploy your management cluster>

#Redirect to managment directory and configure kpt setter:
pushd "../management"
kpt cfg set -R . name "${MGMT_NAME}"
kpt cfg set -R . gcloud.core.project "${MGMT_PROJECT}"
kpt cfg set -R . managed-project "${KF_PROJECT}"
#Update the policy
gcloud beta anthos apply ./managed-project/iam.yaml
#Return to gcp-blueprints/kubeflow directory:
popd

**Deploy Kubeflow**
```bash
make apply
```
**Access the Kubeflow user interface (UI)**
Enter the following URI into your browser address bar. It can take 20 minutes for the URI to become available: https://${KF_NAME}.endpoints.${KF_PROJECT}.cloud.goog/
You can run the following command to get the URI for your deployment:
`kubectl -n istio-system get ingress`
  
  
  

### Step 3 : Feast Installation



<img src="https://raw.githubusercontent.com/feast-dev/feast/v0.9-branch/docs/assets/feast_logo.png" width="425"/> 


Feast (Feature Store) is an operational data system for managing and serving machine learning features to models in production.[Install link](https://docs.feast.dev/v/v0.9-branch/getting-started/install-feast/kubernetes-with-helm)

Check your deployment Once the Kubeflow kubernetes cluster.

Follow these steps to verify the deployment:

When the deployment finishes, check the resources installed in the namespace kubeflow in your new cluster. To do this from the command line, first set your kubectl credentials to point to the new cluster:

```bash
gcloud container clusters get-credentials "${KF_NAME}" --zone "${ZONE}" --project "${KF_PROJECT}"
Then, check what’s installed in the kubeflow namespace of your GKE cluster:
kubectl -n kubeflow get all
```

**Install Feast via Helm3**
```bash
helm repo add feast-charts https://feast-helm-charts.storage.googleapis.com
helm repo update
kubectl create secret generic feast-postgresql --from-literal=postgresql-password=password
helm install feast-release feast-charts/feast
```

**Expose Redis to External LoadBalancer**
```bash
kubectl get svc |  grep redis-master
kubectl patch service -n default feast-release-redis-master -p '{"spec": {"type": "LoadBalancer"}}'  
kubectl get  svc |  grep redis-master
```

**Expose Kafka to External LoadBalancer**
```bash
kubectl patch service -n default feast-release-kafka -p '{"spec": {"type": "LoadBalancer"}}'  
```

**Install Dataproc**
```bash
gcloud dataproc clusters create dataprocfeast --image-version='2.0.0-RC11-debian10' --region us-east1
```

**Install Grafana Prometheus**
```bash
helm install prometheus stable/prometheus
helm install grafana stable/grafana
``` 



