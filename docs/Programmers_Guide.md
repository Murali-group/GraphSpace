# Programmers Guide

## GraphSpace REST API

The GraphSpace REST API provides endpoints for entities such as graphs, layouts, and groups that allow developers to interact with the GraphSpace website remotely by sending and receiving JSON objects. This API enables developers to create, read, and
update GraphSpace content from client-side JavaScript or from applications written in any language. After a network is uploaded, the API allows the network owner to modify, delete, and share it. The API also allows a user to access several group management features available through the web interface. For example, a user can create or remove a group, add or remove members, obtain a list of groups he or she belongs to, and get information such as the membership on a group.

```
Note: In order to fully utilize the features of GraphSpace REST API, you must have an account on GraphSpace.
```

### Why use GraphSpace REST API ?

The GraphSpace REST API makes it easier than ever to use GraphSpace in new and exciting ways, such as creating external applications on top of GraphSpace. For example, 

- Create a Cytoscape plugin which will allow users to transfer networks between GraphSpace and Cytoscape. 
- Users can also automate the way they upload graphs to GraphSpace.

The scope of what can be done with the GraphSpace REST API is only limited by our imagination. Overall, if a user want a structured, extensible, and simple way to get data in and out of GraphSpace over HTTP, they should probably use the GraphSpace REST API.

### Base URL

All URLs referenced in the documentation have the following base:

> http://www.graphspace.org/api/v1/

<!---
The GraphSpace REST API is served over HTTP. In case you are 
-->



### API Reference

<iframe src="http://35.163.136.54/static/api.html" style="height: 100vh;width: 100%;"></iframe>


## graphspace-python

The GraphSpace software also includes a simple yet powerful Python library called ``graphspace python`` that allows a user to rapidly construct a network, add nodes and edges, modify their visual styles, and then upload the network, all within tens of lines of code. Moreover, the user need not know the details of the REST API to use this module. It is very easy to integrate this library into a user's software pipeline.

### Installation

Install graphspace_python from PyPI using:

```
    pip install graphspace_python
```

### Usage

Please refer to ``graphspace_python`` package's [documentation](http://manual.graphspace.org/projects/graphspace-python/) to learn how to use it. 


## GraphSpace REST APIs using the Postman app

```
    Note: In order to fully utilize the features of GraphSpace REST API, you must have an account on GraphSpace.
```

Postman is a Google Chrome app for interacting with HTTP APIs. It provides a friendly GUI for constructing requests and reading responses. Postman makes it easy to test, develop and document APIs by allowing users to quickly put together both simple and complex HTTP requests.

### Postman Installation

Postman is available as a [native app](https://www.getpostman.com/docs/install_native) (recommended) for Mac / Windows / Linux, and as a Chrome App. The Postman Chrome app can only run on the Chrome browser. To use the Postman Chrome app, you need to:
- Install Google Chrome: [Install Chrome](https://www.google.com/chrome/).
- If you already have Chrome installed, head over to Postman’s page on the [Chrome Webstore](https://chrome.google.com/webstore/detail/postman-rest-client-packa/fhbjgbiflinjbdggehcddcbncdddomop?hl=en), and click ‘Add to Chrome’.
- After the download is complete, launch the app.

### Using Postman for GraphSpace REST API

The GraphSpace REST APIs have the base URL http://www.graphspace.org/api/v1/. There are many endpoints defined under this base URL (the documentation of which can be found here), but to learn and understand the usage of GraphSpace REST APIs through Postman, we would be considering only the /graphs endpoint for GET and POST request.
- The GET /graphs request fetches a list of graphs from GraphSpace matching the query parameters.
- The POST /graphs request creates a graph in GraphSpace.

### GET /graphs
- The URL is the first thing that we would be setting for a request. We will set the URL to http://www.graphspace.org/api/v1/graphs.
!(_static/image/rest-api/gs_rest_get1.jpg)
