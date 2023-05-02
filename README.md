# Azure Data Factory custom logging solution

Here is the solution for delivering custom metadata from Azure Data Factory (ADF) to Azure Log Analytics through Databricks.


### How it works?
1) ADF Logging pipeline is being invoked from the pipeline, where logging is needed. 2 parameters are being transmitted: parent pipeline name and JSON output with metadata itself, in form of {name: value}.
2) Logging pipeline transfers the request to the Databricks.
3) Databricks receives the parameters, transforms it to API-call suitable form and finally transfers metadata to to Azure Log Analytics.

### Reason of using Databricks:
Azure Monitor Rest API requires the request being encoded by the Base64 format of HMAC-SHA256 algorithm on the UTF-8-encoded string. At the moment of publishing this solution there is no way for doing such encoding by the ADF itself.
