import boto3
import copy
import json
import logging
import os



def setup_logging()
    logger = logging.getLogger()
    
    h = logging.StreamHandler(sys.stdout)

    FORMAT = '%(asctime)s  %(message)s'
    h.setFormatter(logging.Formatter(format))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

    return logger


logger = setup_logging()



session = boto3.Session(profile_name="dev-admin", region_name="us-east-1")
ml = session.client("machinelearning")


# ----------
# Data files location
# ----------
S3_BUCKET = os.environ["S3_BUCKET"]
ds_s3_train = "s3://{}/bo1/train.csv".format(S3_BUCKET)
ds_s3_test = "s3://{}/bo1/test.csv".format(S3_BUCKET)


# ----------
# Data splitting
# ----------
ds_split_start = 0
ds_split_end = 70

ds_split_train = {
    "splitting": {
        "percentBegin": ds_split_start,
        "percentEnd": ds_split_end,
        "strategy": "random"
    }
}

# Complement training split in test split
ds_split_test = copy.deepcopy(ds_split_train)
ds_split_test["splitting"]["complement"] = True


# ----------
# Data schema
# ----------
ds_schema_test = {}
ds_schema_test["version"] = "1.0"
ds_schema_test["dataFormat"] = "CSV"
ds_schema_test["dataFileContainsHeader"] = True
ds_schema_test["attributes"] = [
    {
        "fieldName": "age",
        "fieldType": "NUMERIC"
    },
    {
        "fieldName": "cost_of_ad",
        "fieldType": "NUMERIC"
    },
    {
        "fieldName": "device_type",
        "fieldType": "CATEGORICAL"
    },
    {
        "fieldName": "gender",
        "fieldType": "CATEGORICAL"
    },
    {
        "fieldName": "in_initial_launch_location",
        "fieldType": "BINARY"
    },
    {
        "fieldName": "income",
        "fieldType": "NUMERIC"
    },
    {
        "fieldName": "n_drivers",
        "fieldType": "NUMERIC"
    },
    {
        "fieldName": "n_vehicles",
        "fieldType": "NUMERIC"
    },
    {
        "fieldName": "prior_ins_tenure",
        "fieldType": "NUMERIC"
    },

]

# Add outcome attribute for training data source
ds_schema_train = copy.deepcopy(ds_schema_test)
ds_schema_train["targetFieldName"] = "outcome"
ds_schema_train["attributes"].append(
    {
        "fieldName": "outcome",
        "fieldType": "BINARY"
    }
)


# ----------
# Create data source
# ----------

logger.info("Creating training data source")
response = ml.create_data_source_from_s3(
    DataSourceId='bo1-train',
    DataSourceName='BO1 training set',
    DataSpec={
        "DataLocationS3": ds_s3_train,
        "DataRearrangement": json.dumps(ds_split_train),
        "DataSchema": json.dumps(ds_schema_train)
    },
    ComputeStatistics=True
)
logger.info("RESPONSE: \n" + response)


logger.info("Creating test data source")
response = ml.create_data_source_from_s3(
    DataSourceId='bo1-test',
    DataSourceName='BO1 test set',
    DataSpec={
        "DataLocationS3": ds_s3_test,
        "DataRearrangement": json.dumps(ds_split_test),
        "DataSchema": json.dumps(ds_schema_test)
    },
    ComputeStatistics=True
)
logger.info("RESPONSE: \n" + response)


# ----------
# Create model based on training data
# ----------

logger.info("Creating model based on training data")
response = ml.create_ml_model(
        MLModelId="bo1-model",
        MLModelName="BO1 Outcome Model",
        MLModelType="BINARY",
        Parameters={
            "sgd.shuffleType": "auto",
            "sgd.l2RegularizationAmount": "1.0E-07"
        },
        TrainingDataSourceId="bo1-train"
    )


logger.info("RESPONSE: \n" + response)


# ----------
# Get batch predictions for test set
# ----------
response = ml.create_batch_prediction(
    BatchPredictionId="bo1-test-prediction",
    BatchPredictionName="Predictions for BO1-test",
    MLModelId="bo1-model",
    BatchPredictionDataSourceId="bo1-test-1",
    OutputUri="s3://com.lifetech.ampliseq.dev.transfer/bo1-test-prediction/"

)