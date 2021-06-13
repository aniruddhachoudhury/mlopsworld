from __future__ import absolute_import, division, print_function, unicode_literals
import os
import dill
import s3fs
import time
import json
import adlfs
import click
import gcsfs
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from feast.config import Config
from urllib.parse import urlparse
from pyarrow.parquet import ParquetDataset
import feast.staging.entities as entities
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from feast.data_source import FileSource, KafkaSource
from feast.data_format import ParquetFormat, AvroFormat
from feast import Client, Feature, Entity, ValueType, FeatureTable
from feast.pyspark.abc import RetrievalJobParameters, SparkJobStatus, SparkJob



        
def feature_store_settings(staging_bucket,project):
        # Using environmental variables
            environment = \
                        {'FEAST_CORE_URL': 'feast-release-feast-core.default:6565',
                         'FEAST_DATAPROC_CLUSTER_NAME': 'dataprocfeast',
                         'FEAST_DATAPROC_PROJECT': project,
                         'FEAST_DATAPROC_REGION': 'us-east1',
                         'FEAST_STAGING_LOCATION': staging_bucket,
                         'FEAST_HISTORICAL_FEATURE_OUTPUT_FORMAT': 'parquet',
                         'FEAST_HISTORICAL_FEATURE_OUTPUT_LOCATION': f"{staging_bucket}historical/",
                         'FEAST_HISTORICAL_SERVING_URL': 'feast-release-feast-online-serving.default:6566',
                         'FEAST_REDIS_HOST': '34.72.322.71',
                         'FEAST_REDIS_PORT': '6379',
                         'FEAST_SERVING_URL': 'feast-release-feast-online-serving.default:6566',
                         'FEAST_SPARK_HOME': '/usr/local/spark',
                         'FEAST_SPARK_LAUNCHER': 'dataproc',
                         'FEAST_SPARK_STANDALONE_MASTER': 'local[*]',
                         'FEAST_SPARK_STAGING_LOCATION':  f'{staging_bucket}/artifacts/',
                         'FEAST_SPARK_STAGING_LOCATION': 'gs://dataproc-staging-us-east1-996861042416-4w01soni/artifacts/',
                         'FEAST_SPARK_STANDALONE_MASTER': 'local[*]',
                         'DEMO_KAFKA_BROKERS': '36.194.132.2'
    
                          }               
     
            for key,value in environment.items():
                os.environ[key] = value                




def read_parquet(uri):
    parsed_uri = urlparse(uri)
    if parsed_uri.scheme == "file":
        return pd.read_parquet(parsed_uri.path)
    elif parsed_uri.scheme == "gs":
        fs = gcsfs.GCSFileSystem()
        files = ["gs://" + path for path in fs.glob(uri + '/part-*')]
        ds = ParquetDataset(files, filesystem=fs)
        return ds.read().to_pandas()
    elif parsed_uri.scheme == 's3':
        fs = s3fs.S3FileSystem()
        files = ["s3://" + path for path in fs.glob(uri + '/part-*')]
        ds = ParquetDataset(files, filesystem=fs)
        return ds.read().to_pandas()
    elif parsed_uri.scheme == 'wasbs':
        fs = adlfs.AzureBlobFileSystem(
            account_name=os.getenv('FEAST_AZURE_BLOB_ACCOUNT_NAME'), account_key=os.getenv('FEAST_AZURE_BLOB_ACCOUNT_ACCESS_KEY')
        )
        uripath = parsed_uri.username + parsed_uri.path
        files = fs.glob(uripath + '/part-*')
        ds = ParquetDataset(files, filesystem=fs)
        return ds.read().to_pandas()
    else:
        raise ValueError(f"Unsupported URL scheme {uri}")

def wait_for_job_status(
    job: SparkJob,
    expected_status: SparkJobStatus,
    max_retry: int = 4,
    retry_interval: int = 5,
):
    for i in range(max_retry):
        if job.get_status() == expected_status:
            print("The Spark Job is Completed")
            return
        time.sleep(retry_interval)
    raise ValueError(f"Timeout waiting for job status to become {expected_status.name}")

def change_datetime(df,col):
    df[col]=pd.to_datetime(df[col])
    return df


@click.command()
@click.option('--staging-bucket', default="gs://<BUCKET>/")
@click.option('--project', default="your-gcp-project")
@click.option('--target-name', default="fare_statistics__target")
@click.option('--data-id', default="gs://<BUCKET>/driver_id.csv")
@click.option('--data-source', default="batch")
@click.option('--data-features', default="gs://<BUCKET>/features.json")
def feature_store_service(staging_bucket,project,target_name,data_id,data_source,data_features):

    # Intiate the environment variables for the spark job
    if data_source.lower()=='batch':    
        feature_store_settings(staging_bucket,project)

    #Load Artifacts
    local_features="/mnt/features.json"
    os.system("gsutil cp {} {}".format(data_features,local_features))


    with open(local_features) as f:
        features = json.load(f)
    
    entities_with_timestamp=pd.read_csv(data_id)
    entities_with_timestamp=change_datetime(entities_with_timestamp,'event_timestamp')

    #Feature Store Spark Job for Historical Data
    client = Client()    
    job = client.get_historical_features(feature_refs=features,entity_source= entities.stage_entities_to_fs(entity_source=entities_with_timestamp, staging_location=staging_bucket,config= Config))    
    features_outcome=pd.DataFrame()
    if True:
        output_file_uri = job.get_output_file_uri()
        wait_for_job_status(job,SparkJobStatus.COMPLETED)
        features_outcome=read_parquet(output_file_uri)

    features_outcome.dropna(inplace=True)
    data_target = features_outcome[target_name]
    data = features_outcome.drop([target_name,'driver_id','event_timestamp'], axis=1)
    
    #Scale
    scaler = StandardScaler()
    data = scaler.fit_transform(data) 

     #%% split training set to validation set
    x_train, x_test, y_train, y_test = train_test_split(data, data_target, test_size=0.2, random_state=0)
    
    #print loga
    print(len(x_train), 'train examples')
    print(len(x_test), 'test examples')
    

    #Dump the data in PVC
    with open("/mnt/training.data","wb") as f:
        dill.dump(x_train,f) 
    
    with open("/mnt/validation.data","wb") as f:
        dill.dump(x_test,f) 
    
    with open("/mnt/trainingtarget.data","wb") as f:
        dill.dump(y_train,f) 
       
    with open("/mnt/validationtarget.data","wb") as f:
        dill.dump(y_test,f) 

    return


if __name__ == "__main__":
    feature_store_service()