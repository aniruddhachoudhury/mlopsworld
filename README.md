# 2nd Annual MLOps World: Machine Learning in Production Conference

![](image.png)


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
**Run the following command to pull upstream manifests from kubeflow/manifests repository**
```bash
cd..
cd kubeflow
bash ./pull-upstream.sh
```
<div class="animate__slideInDown animate__bounce animate__repeat-2">Example</div>



  
  
  

### Step 3 : Feast Installation

Once the Kubeflow kubernetes cluster

