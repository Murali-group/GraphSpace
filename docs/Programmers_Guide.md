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

## HTTP Status Codes
The [GraphSpace](https://graphspace.org) API attempts to return appropriate HTTP status codes for every request.</p>

### Success Codes
* ***200:*** Your request has succeeded.

* ***201:*** Your request has been fulfilled and resulted in a new resource being created.

### Error Codes
* ***400:*** Bad Request! The server cannot or will not process your request due to an apparent client error (e.g., malformed request syntax, too large size, invalid request message framing, or deceptive request routing).

* ***401:*** Unauthenticated! Either your authentication token is missing or invalid, or you are not allowed to access the content provided by the requested URL.

* ***403:*** Unauthorized! You are not authorized to access this resource, create an account and contact resource's owner for permission to access this resource.

* ***405:*** Method Not Allowed! Your request method is not supported by the resource. For example, using GET on a form which requires data to be presented via POST, or using PUT on a read-only resource.

* ***1000:*** User with the provided email id already exists!

* ***1003:*** Your Username or Password is not recognized.

* ***1006:*** `is_public` is required to be set to True when `owner_email` and `member_email` are not provided.

* ***1007:*** You are not authorized to access private graphs created by other users.

* ***1008:*** You are not allowed to create a graph for other users.

* ***1009:*** Your graph ID is missing.

* ***1010:*** You are not authorized to access groups you aren't part of. Set `owner_email` or `member_email` to your email.

* ***1011:*** You are not allowed to create a group for other users.

* ***1012:*** You are not authorized to access layouts which are not shared. Set `owner_email` to your email or `is_shared` to 1.

* ***1013:*** Cannot create the layout with your provided owner email.

* ***1014:*** Layout with the provided name already exists.

## graphspace-python

The GraphSpace software also includes a simple yet powerful Python library called ``graphspace python`` that allows a user to rapidly construct a network, add nodes and edges, modify their visual styles, and then upload the network, all within tens of lines of code. Moreover, the user need not know the details of the REST API to use this module. It is very easy to integrate this library into a user's software pipeline.

### Installation

Install graphspace_python from PyPI using:

```
    pip install graphspace_python
```

### Usage

Please refer to ``graphspace_python`` package's [documentation](http://manual.graphspace.org/projects/graphspace-python/) to learn how to use it. 
