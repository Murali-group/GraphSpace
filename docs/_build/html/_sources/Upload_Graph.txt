# Upload Graph


GraphSpace provides two methods to upload graphs: through the REST API or through the web interface.

## Via the REST API
This approach allows one to be more flexible and utilize all of the CSS features by specifically referencing them in the JSON for the graph. Please refer to the Programmer's Guide for more information.

## Via the Web Interface
As an alternative to the REST API for uploading a graph, we provide a simple web interface for uploading individual graphs. We support the following types of files:

- Graphs that a user of Cytoscape (v3.1 or later) can export in a JSON format, which we call "cyjs" format. Please follow [these instructions](https://github.com/idekerlab/cy-net-share/wiki) to export your Cytoscape graph to this format. These files must use the .cyjs extension.


If a user has an account and is logged in, this interface will upload the graph directly into the user's account, much like using the REST API. If a user does not have an account or is not logged in, this upload functionality will provide a unique URL through which the user may interact with the graph represented by the uploaded file. **Note: After 30 days, we will delete all graphs that are uploaded for unregistered users of GraphSpace.**

