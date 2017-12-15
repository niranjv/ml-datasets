# Purpose: Use Topic Modeling from AWS Comprehend to generate topics from tweets and Reddit submissions

# Get input files for AWS Comprehend
cut -f 1 -d, twitter_data.csv > twitter_data_textonly.csv
cut -f 1 -d, reddit_data.csv > reddit_data_textonly.csv

# Copy input files to S3; Comprehend will get files from here
aws s3 cp twitter_data_textonly.csv s3://nvtemp/comprehend/input/ --region us-east-1 --profile dev-admin
aws s3 cp reddit_data_textonly.csv s3://nvtemp/comprehend/input/ --region us-east-1 --profile dev-admin

# Get topics from AWS Comprehend
jobname=NVTestJob
timestamp=$(date "+%Y%m%d-%H%M%S")
aws comprehend --region us-east-1 --profile dev-admin start-topics-detection-job \
                --input-data-config S3Uri=s3://nvtemp/comprehend/input/,InputFormat=ONE_DOC_PER_LINE \
                --output-data-config S3Uri=s3://nvtemp/comprehend/output/ \
                --job-name $jobname-$timestamp \
                --number-of-topics 100 \
                --cli-input-json file://aws_comprehend_job_definition.json
                
# Format of aws_comprehend_job_definition.json
# {
#     "DataAccessRoleArn": "arn:aws:iam::account ID:role/data access role name"
# }
