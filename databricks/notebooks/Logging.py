# Databricks notebook source
# MAGIC %md
# MAGIC ### Widgets
# MAGIC These are created to accept parameters from ADF

# COMMAND ----------

parent_pipeline = dbutils.widgets.get("parent_pipeline")
json_input = dbutils.widgets.get("json_input")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Send data to Log Analytics
# MAGIC Data packing in form needed for sending API-request to Azure Log Analytics

# COMMAND ----------

import json
import requests
import datetime
import hashlib
import hmac
import base64
import ast

# Update the customer ID to your Log Analytics workspace ID
customer_id = dbutils.secrets.get(scope = "storage-scope", key = "log-analytics-customer-id-databricks")
# For the shared key, use either the primary or the secondary Connected Sources client authentication key   
shared_key = dbutils.secrets.get(scope = "storage-scope", key = "log-analytics-shared-key-databricks")
# The log type is the name of the event that is being submitted
log_type = parent_pipeline

# An example of JSON web monitor object
json_data = ast.literal_eval(json_input)
print(json_data)


#####################
######Functions######  
#####################

# Build an request body
body = json.dumps(json_data)

# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Build and send a request to the POST API
def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    api_version = '2016-04-01'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=' + api_version

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print('Accepted')
    else:
        print("Response code: {}".format(response.status_code))
        print(response.text)

post_data(customer_id, shared_key, body, log_type)
