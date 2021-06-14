### Feature Store Kubeflow Taxi Classification Use-Case : End to End Pipeline

### Pre-Requisite
- Follow the **setup-guides/steps-gcp.md** to setup kubeflow and required components. 

### Steps for End-To-End Pipeline


1. set working directory 

Connect to GCP via Local
```bash
gcloud init
gcloud auth application-default login
```

3. Build the container for Data preprocessing

```bash
cd $WORKDIR/1_feature_store_ingestion/
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=mlops_world/featureingestion
IMAGE_VERSION=latest 
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
```

Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .
```
Push training image to GCR
```
docker push $IMAGE_NAME:$IMAGE_VERSION
```

4. Build the container for Training Model

```bash
cd $WORKDIR/2_HPO_train/
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=mlops_world/feastrainingjob
IMAGE_VERSION=latest 
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
```

Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .
```
Push training image to GCR
```
docker push $IMAGE_NAME:$IMAGE_VERSION
```

5. Build the container for Evaluation Model

```bash
cd $WORKDIR/pipeline/evaluation 
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=mlops_world/modelevaluation
IMAGE_VERSION=latest 
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME

```

Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .
```
Push training image to GCR
```
docker push $IMAGE_NAME:$IMAGE_VERSION
```

5. Build the container for Serving Model

```bash
cd $WORKDIR/pipeline/evaluation 
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=mlops_world/kfservingcustom
IMAGE_VERSION=latest 
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME

```

Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .
```
Push training image to GCR
```
docker push $IMAGE_NAME:$IMAGE_VERSION
```
