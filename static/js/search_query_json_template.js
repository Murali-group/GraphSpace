/**
 * Created by adb on 08/04/17.
 */

var nodeSubQueryTemplateJSON = {
    "nested": {
        "path": "object_elements.object_nodes.object_data",
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "query": "*"
                        }
                    }
                ]
            }
        }
    }
};

var networkSubQueryTemplateJSON = {
    "nested": {
        "path": "object_data",
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "query": "*"
                        }
                    }
                ]
            }
        }
    }
};

var searchQueryTemplateJSON = {
    "_source": false,
    "query": {
        "bool": {
            "must": [],
            "should": [],
            "must_not": [],
            "minimum_should_match": 0
        }
    }
}