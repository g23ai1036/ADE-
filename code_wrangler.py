import awswrangler as wr
import pandas as pd
import urllib.parse
import os


## Environment Variables
os_input_s3_cleansed_layer = os.environ['s3_cleansed_layer'] ##  s3_cleansed_layer: S3 path where the cleaned data will be stored.
os_input_glue_catalog_db_name = os.environ['glue_catalog_db_name ## glue_catalog_db_name: AWS Glue Catalog database name
os_input_glue_catalog_table_name = os.environ['glue_catalog_table_name'] ## glue_catalog_table_name : AWS Glue Catalog table name.
os_input_write_data_operation = os.environ['write_data_operation'] ## write_data_operation : Write operation mode (e.g., 'overwrite' or 'append').

## Lambda Handler
## The lambda_handler function is the entry point for the Lambda function and processes the S3 event

def lambda_handler(event, context):
    # Get the object from the event and show its content type
    # Extract Bucket and Key:
    
    bucket = event['Records'][0]['s3']['bucket']['name'] ## Extracts the bucket name and object key from the event data
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        # Read JSON Data from S3:
        # Creating DF from content
        df_raw = wr.s3.read_json('s3://{}/{}'.format(bucket, key)) ## Uses awswrangler to read JSON data from the specified S3 bucket and object key

        # Extract required columns:
        df_step_1 = pd.json_normalize(df_raw['items']) ## Normalizes the JSON data to create a flattened DataFrame

        # Write to S3  in Parquet Format:
        wr_response = wr.s3.to_parquet(
            df=df_step_1,
            path=os_input_s3_cleansed_layer,
            dataset=True,
            database=os_input_glue_catalog_db_name,
            table=os_input_glue_catalog_table_name,
            mode=os_input_write_data_operation
        )
        ## Writes the processed DataFrame to the cleansed S3 layer in Parquet format
        ## The awswrangler library also updates the AWS Glue Catalog with the new data

        return wr_response
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
