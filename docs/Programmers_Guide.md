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

## API Authentication Token
### Obtain Authentication Token
To get your API authentication token, log into your GraphSpace account and navigate to your account page. Once you are there click on the **Authentication Token** tab on the top. Then you can see your authentication token value. 

![Get Auth Token](_static/gifs/gs-screenshot-get-auth-token.gif)

### Use Authentication Token to Access GraphSpace API
cURL is the most used command line tool for making API calls. Here we use cURL command as an example.

**GET**
```
curl -X GET \
  '**YOUR GRAPHSPACE API URL**' \
  -H 'accept: application/json' \
  -H 'authorization: Basic **YOUR API AUTH TOKEN**' \
  -H 'content-type: application/json' \
```
**POST**
```
curl -X POST \
  **YOUR GRAPHSPACE API URL** \
  -H 'accept: application/json' \
  -H 'authorization: Basic **YOUR API AUTH TOKEN**' \
  -H 'content-type: application/json' \
  -d '**YOUR JSON DATA**'
```



## graphspace-python

The GraphSpace software also includes a simple yet powerful Python library called ``graphspace python`` that allows a user to rapidly construct a network, add nodes and edges, modify their visual styles, and then upload the network, all within tens of lines of code. Moreover, the user need not know the details of the REST API to use this module. It is very easy to integrate this library into a user's software pipeline.

### Installation

Install graphspace_python from PyPI using:

```
    pip install graphspace_python
```

### Usage

Please refer to ``graphspace_python`` package's [documentation](http://manual.graphspace.org/projects/graphspace-python/) to learn how to use it. 
