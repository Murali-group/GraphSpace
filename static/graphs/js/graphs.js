/* Front end code for graphs/ endpoint.  Provides all front-end functionalities that occur when 
 * user interacts with HTML elements 
 */

/**
* Switches the search page.
* @param searchPage type of search page. (my_graphs/shared_graphs/public_graphs)
* */
var switchSearch = function(searchPage) {
    if (searchPage == 'public_graphs') {
        pathname = '/graphs/public/';
    } else if (searchPage == 'shared_graphs') {
        pathname = '/graphs/shared/';
    } else {
        pathname = '/graphs/';
    }

    window.location.href = pathname + window.location.search;
};

$(document).ready(function() {

  if (getQueryVariable('full_search')) {
    // Initially set search to full matching
    $("#full_search").attr('checked', true);
  } else {
    // Initially set search to full matching
    $("#partial_search").attr('checked', true);
  }

  //these accordions make up the side menu
  $('#accordion_tags').accordion({
    collapsible: true,
  });

  //When search button on the side gets clicked
  $("#search_button").click(function(e) {
    e.preventDefault();
    //Get URL removing any previous search query terms
    var newURL = removeURLParameter(document.URL, $('input[name=match]:not(:checked)').val());
    //Remove the trailing ? character
    if (newURL.charAt(newURL.length - 1) == '?') {
      newURL = newURL.substring(0, newURL.length - 1);
    }
    //Append new search type (partial or exact)
    urlAppender(newURL, $('input[name=match]:checked').val(), $("#searching").val());
  });

  //When tag button on the side gets clicked
  $("#tags_button").click(function(e) {
    e.preventDefault();
    urlAppender(document.URL, 'tags', $("#tags_searching").val());
  });

  //Clears all seach terms
  $("#clear_search").click(function(e) {
    e.preventDefault();
    clearSearchTerms();
  });

  //Clears all tag terms
  $("#clear_tags").click(function(e) {
    e.preventDefault();
    clearTagTerms();
  });

  //Based on the search term query, it fill in the search input with the searched tersm
  if (getQueryVariable($('input[name=match]:checked').val())) {
    $("#searching").val(decodeURIComponent(getQueryVariable($('input[name=match]:checked').val())));
  }

    //Based on the tag term query, it fill in the tag input with the tag terms
  if (getQueryVariable('tags')) {
    $("#tags_searching").val(decodeURIComponent(getQueryVariable('tags')));
  }

  //Places the clickable icons (sorting) in the table
  //The icons change depending on the type of sorting
  setIcons();

  /**
   * For each tag, if it is clicked, extract the id (tag name)
   * from button and append it to the URL, making sure that URL syntax 
   * is still followed.
   */
  $(".tag_links").click(function(e) {
    urlAppender(document.URL, 'tags', $(this).attr('id'));
  });

  /**
   * Appends appropriate terms to the url depending on what is being searched for
   * For example, it appends ?queryTerm if there are no query terms, or it appends &queryTerm=
   * to the end of the current url if a queryterm already exists.
   * 
   * @param url URL to append queryterm to
   * @param queryTerm Value to be searched for
   * @param queryValue Element to insert as the query value
   */
  function urlAppender(url, queryTerm, queryValue) {
    if (queryValue.length > 0) {
      var tempUrl = updateQueryStringParameter(url, queryTerm, queryValue);
      window.location.href = removeURLParameter(tempUrl, 'page');
    } else {
      window.location.href = window.location.href.split('?')[0];
    }
  }

  /**
   * Modifies query terms that are part of the URL already
   * @param termType Query type to change value of ex: search or tags
   * @param queryTerm term(s) to change to in the termType
   */
  function modifyQueryTerms(termType, queryTerm) {
    var url = document.URL;

    //Get index of where search terms start and end
    var searchIndex = url.indexOf(termType);
    var endSearchIndex = url.substring(searchIndex).indexOf('&');

    //If there are no more than one search term
    if (endSearchIndex == -1) {
      //Remove search term from URL
      searchString = url.substring(searchIndex).replace(termType + '=', '').replace(/%20/g, '').split(',');
      //Add new search term to URL
      searchURL = url.substring(0, searchIndex) + termType + '=';
      
      //Get where query term starts
      var indexToRemove = searchString.indexOf(queryTerm);
      if (indexToRemove > -1) {
        searchString.splice(indexToRemove, 1);
      }

      //For all search terms, append with a ",""
      for (var i = 0; i < searchString.length; i++) {
        if (searchString[i].length > 0 && searchString[i] != queryTerm) {
          if (i == 0) {
            searchURL += searchString[i];
          } else {
            searchURL += ',' + searchString[i];
          }
        }
      }
      //If there are no search terms, reload page without search term
      if (searchString.length == 0) {
        window.location.href = url.substring(0, searchIndex - 1);
      } else {
        window.location.href = searchURL;
      }
    } else {
      searchString = url.substring(searchIndex, url.indexOf('&')).replace(termType + '=', '').replace(/%20/g, '').split(',');
      searchURL = url.substring(0, searchIndex) + termType + '=';
      var indexToRemove = searchString.indexOf(queryTerm);
      if (indexToRemove > -1) {
        searchString.splice(indexToRemove, 1);
      }

      //For all search terms, append with a ",""
      for (var i = 0; i < searchString.length; i++) {
        if (searchString[i].length > 0 && searchString[i] != queryTerm) {
          if (i == 0) {
            searchURL += searchString[i];
          } else {
            searchURL += ',' + searchString[i];
          }
        }
      }

      //Add multiple search terms with '&'
      searchURL += url.substring(url.indexOf('&'));
      if (searchString.length == 0) {
        window.location.href = url.substring(0, searchIndex) + url.substring(url.indexOf('&') + 1);
      } else {
        window.location.href = searchURL;
      }
    }
  }

  /**
   * Sorts all graphs that are returned.
   */
  $(".order").click(function(e) {
    setIcon($(this).children().attr('id'));
  });

  /**
   * Deletes a graph through the UI.
   */
  $(".delete_graph").click(function(e) {
    e.preventDefault();
    var gid = $(this).attr('id');

    $("#deleteModal").modal('toggle');

    $("#delete_confirm").on('click', function(e) {
      $.post('/deleteGraph/', {
        'gid': gid
      }, function(data) {
        if (data.Error) {
          return alert(data.Error);
        }
        window.location.reload();
      });
    });
    
  });

  /**
   * Sets the specific icon for property. For example, clicking icon 
   * in front of graph id will change the icon to something else.
   * @param iconId ID of icon to change
   */
  function setIcon(iconId) {
    //Modified button is different because of different icons to display
    if (iconId == 'order_modified_icon') {
      if ($("#" + iconId).attr('class') == 'glyphicon glyphicon-sort' || $("#" + iconId).attr('class') == 'glyphicon glyphicon-sort-by-attributes-alt') {
        setOrderQuery(iconId, 'ascending');
      } else if ($("#" + iconId).attr('class') == 'glyphicon glyphicon-sort-by-attributes') {
        setOrderQuery(iconId, 'descending');
      }
    } else {
      if ($("#" + iconId).attr('class') == 'glyphicon glyphicon-sort' || $("#" + iconId).attr('class') == 'glyphicon glyphicon-sort-by-alphabet-alt') {
        setOrderQuery(iconId, 'ascending');
      } else if ($("#" + iconId).attr('class') == 'glyphicon glyphicon-sort-by-alphabet') {
        setOrderQuery(iconId, 'descending');
      }
    }
  }

  /*
   * Modifies the order query term in the URL to sort the 
   * specified attribute.
   * @param iconID ID of icon to sort attribute
   * @param sortValue value specified which way to sort attribute (ascending, descending, none)
   */
  function setOrderQuery(iconId, sortValue) {
    if (iconId == 'order_graphs_icon') {
      window.location.href = updateQueryStringParameter(window.location.href, "order", "graph_" + sortValue);
    } else if (iconId == 'order_owner_icon') {
      window.location.href = updateQueryStringParameter(window.location.href, "order", "owner_" + sortValue);
    } else if (iconId == 'order_modified_icon') {
      window.location.href = updateQueryStringParameter(window.location.href, "order", "modified_" + sortValue);
    }
  }

  /*
   * Removes the parameter from url that I don't want.
   * @param url URL to parse
   * @param parameter variable to delete from querystring
   */
  function removeURLParameter(url, parameter) {
    //prefer to use l.search if you have a location/link object
    var urlparts = url.split('?');
    if (urlparts.length >= 2) {

      var prefix = encodeURIComponent(parameter) + '=';
      var pars = urlparts[1].split(/[&;]/g);

      //reverse iteration as may be destructive
      for (var i = pars.length; i-- > 0;) {
        //idiom for string.startsWith
        if (pars[i].lastIndexOf(prefix, 0) !== -1) {
          pars.splice(i, 1);
        }
      }

      url = urlparts[0] + '?' + pars.join('&');
      return url;
    } else {
      return url;
    }
  }

  /**
   * Updates specified value in the query.
   */
  function updateQueryStringParameter(uri, key, value) {
    var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
    var separator = uri.indexOf('?') !== -1 ? "&" : "?";
    if (uri.match(re)) {
      return uri.replace(re, '$1' + key + "=" + value + '$2');
    } else {
      return uri + separator + key + "=" + value;
    }
  }

  /**
   * Gets query variables from the url.
   * @param variable variable to find in the URL
   */
  function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
      var pair = vars[i].split("=");
      if (pair[0] == variable) {
        return pair[1];
      }
    }
    return (false);
  }

  /**
   * Sets the icons at the loading of the page.
   * Changes the icons depending on the type of sorting the user wants.
   */
  function setIcons() {
    var orderVariable = getQueryVariable("order");

    if (orderVariable) {
      if (orderVariable == 'graph_ascending') {
        $("#order_graphs_icon").attr('class', 'glyphicon glyphicon-sort-by-alphabet');
        $("#order_graphs_btn").tooltip({
          "content": "Order by Graph ID descending"
        });
      } else if (orderVariable == 'graph_descending') {
        $("#order_graphs_icon").attr('class', 'glyphicon glyphicon-sort-by-alphabet-alt');
      } else if (orderVariable == 'modified_ascending') {
        $("#order_modified_icon").attr('class', 'glyphicon glyphicon-sort-by-attributes');
        $("#order_modified_btn").tooltip({
          "content": "Order by Modified descending"
        });
      } else if (orderVariable == 'modified_descending') {
        $("#order_modified_icon").attr('class', 'glyphicon glyphicon-sort-by-attributes-alt');
      } else if (orderVariable == 'owner_ascending') {
        $("#order_owner_icon").attr('class', 'glyphicon glyphicon-sort-by-alphabet');
        $("#order_owner_btn").tooltip({
          "content": "Order by Owner descending"
        });
      } else if (orderVariable == 'owner_descending') {
        $("#order_owner_icon").attr('class', 'glyphicon glyphicon-sort-by-alphabet-alt');
      }
    }
  }

  /**
  * Clears all tag terms and reloads page without the tag terms.
  */
  function clearTagTerms() {
    if (document.URL.indexOf('?') > -1 && document.URL.indexOf('tags') > -1) {
      var linkToGraph = removeURLParameter(document.URL, "tags");
    } else {
      var linkToGraph = document.URL;
    }

    window.location.href = linkToGraph;
  }

  /**
  * Clears all search terms and get rid of 
  * current search terms from the URL.
  */
  function clearSearchTerms() {
    //If there is a query term
    if (document.URL.indexOf('?') > -1) {
      //Remove the partial_search query from the URL
      if (getQueryVariable("partial_search")) {
        var linkToGraph = removeURLParameter(document.URL, "partial_search");
      } else if (getQueryVariable("full_search")) {
        //Remove the full_search query from the URL
        var linkToGraph = removeURLParameter(document.URL, "full_search");
        // linkToGraph = linkToGraph.substring(0, linkToGraph.length - 1);
      } else {
        var linkToGraph = document.URL;
      }
    } else {
      var linkToGraph = document.URL;
    }
    //Reload page without the search terms
    window.location.href = linkToGraph;
  }

});

