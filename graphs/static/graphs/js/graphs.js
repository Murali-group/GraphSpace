/* Front end code for graphs/ endpoint.  Provides all front-end functionalities that occur when 
 * user interacts with HTML elements 
 */
$(document).ready(function() {

    //these accordions make up the side menu
   $('#accordion_tags').accordion({
      collapsible: true,
   });

   //When search button on the side gets clicked
   $("#search_button").click(function (e) {
   	e.preventDefault();
      urlAppender($("#searching").val(), 'search=', 'tags=');
   });

   //When tag button on the side gets clicked
   $("#tags_button").click(function (e) {
   	e.preventDefault();
      urlAppender($("#tags_searching").val(), "tags=", "search=");
   });

   $(".search").click(function (e) {
      e.preventDefault();
      modifyQueryTerms('search', $(this).attr('id'));
   });

   $(".tags").click(function (e) {
      e.preventDefault();
      modifyQueryTerms('tags', $(this).attr('id'));
   });

   /**
   * For each tag, if it is clicked, extract the id (tag name)
   * from button and append it to the URL, making sure that URL syntax 
   * is still followed.
   */
   $(".tag_links").click(function (e) {
      var url = document.URL;
      //If there is no tag query in URL
      if (url.indexOf('tags') == -1) {
         //Insert tags at the end with '?' character if no query string present
         if (url.indexOf('?') == -1) {
            url += '?tags=' + $(this).attr('id');
         } else {
            //If there is another query, neeed '&' to join queries
            url += '&tags=' + $(this).attr('id');
         }
      } else {
         //Insert tag query at the end of the URL
         var tagIndex = url.indexOf('tags=');
         var sepIndex = url.indexOf('&');
         //If tags is after the '&' character, simply append to query string
         if (tagIndex > sepIndex) {
            url += ',' + $(this).attr('id');
         } else {
            //Otherwise, need to get index of '&' and pad all tags before this character so that tags query is properly formatted
            var url = url.substring(0, tagIndex) + url.substring(sepIndex, tagIndex) + ',' + $(this).attr('id') + url.substring(sepIndex);
         }
      }
      //Change the URL to modified location
      window.location.href = url;
   });   

   /**
   * Appends appropriate terms to the url depending on what is being searched for
   * For example, it appends ?queryTerm if there are no query terms, or it appends &queryTerm=
   * to the end of the current url if a queryterm already exists.
   * 
   * @param searchVal Value to be searched for
   * @param element1 First element to be searched for in the query string
   * @param element2 Second element to be searched for in the query string
   */
   function urlAppender(searchVal, element1, element2) {
      var url = document.URL;
      if (searchVal.length > 0) {
         //If user is viewing a certain page and there are multiple query terms
         if (url.indexOf('page=') > -1) {
            if (url.indexOf('&') > -1) {
               if (url.indexOf('page=') < url.indexOf('&')) {
                  //Get all of the URL except the pagination number user is currently at
                  url = url.slice(0, url.indexOf('page')) + url.slice(url.indexOf('&'));
                  return;
               } else {
                  //Otherwise if pagination is at the end of URL, get everything before pagination
                  url = url.slice(0, url.indexOf('page=') -1);
               }
            } else {
               //Otherwise, just get everything before pagination
               url = url.slice(0, url.indexOf('page') - 1);
            }
         }
         //If we are searching for a specific element in the query term
         if (url.indexOf(element2) == -1) {
            //If there is already a query term, append '&' to it
            if (url.indexOf(element1) == -1 && url.indexOf('?') > -1) {
               window.location.href = url + '&' + element1 + searchVal;
            } else if (url.indexOf(element1) == -1) {
               //Otherwise, append ? to it 
               window.location.href = url + '?' + element1 + searchVal;
            } else {
               //If it is part of the same query, append it with ',' character
               window.location.href = url + ',' + searchVal;
            }
         } else {
            //Find out which query element comes first.
            //Then, created new url with old query terms,
            //in addition to the new query terms to append
            element2Index = url.indexOf(element2);
            element1Index = url.indexOf(element1);
            if (element1Index > element2Index) {
               oldSearchTerms = url.substring(element1Index);
               searchVal += ',' + oldSearchTerms.substring(element1.length);
               window.location.href = url.substring(0, element1Index-1) + '&' + element1 + searchVal;
            } else {
               window.location.href = url.substring(0, element1Index-1) + '?' + url.substring(element2Index, url.length) + '&' + element1 + searchVal;
            }
         }
      } else {
         return alert("Please enter a term to search for!");
      }
   }

   /**
   * Modifies query terms that are part of the URL already
   * @param termType Query type to change value of ex: search= or tags=
   * @param queryTerm term(s) to change to in the termType
   */
   function modifyQueryTerms(termType, queryTerm) {
      var url = document.URL;

      var searchIndex = url.indexOf(termType);
      var endSearchIndex = url.substring(searchIndex).indexOf('&');

      if (endSearchIndex == -1) {
         searchString = url.substring(searchIndex).replace(termType + '=', '').replace(/%20/g, '').split(',');
         searchURL = url.substring(0, searchIndex) + termType + '=';
         var indexToRemove = searchString.indexOf(queryTerm);
         if (indexToRemove > -1 ) {
            searchString.splice(indexToRemove, 1);
         }
         for (var i = 0; i < searchString.length; i++) {
            if (searchString[i].length > 0 && searchString[i] != queryTerm) {
               if (i == 0) {
                  searchURL += searchString[i];
               } else {
                  searchURL += ',' + searchString[i];
               }
            }
         } 
         if (searchString.length == 0) {
            window.location.href = url.substring(0, searchIndex - 1);
         } else {
            window.location.href = searchURL;  
         } 
      } else {
         searchString = url.substring(searchIndex, url.indexOf('&')).replace(termType + '=', '').replace(/%20/g, '').split(',');
         searchURL = url.substring(0, searchIndex) + termType + '=';
         var indexToRemove = searchString.indexOf(queryTerm);
         if (indexToRemove > -1 ) {
            searchString.splice(indexToRemove, 1);
         }
         for (var i = 0; i < searchString.length; i++) {
            if (searchString[i].length > 0 && searchString[i] != queryTerm) {
               if (i == 0) {
                  searchURL += searchString[i];
               } else {
                  searchURL += ',' + searchString[i];
               }
            }
         }
         searchURL += url.substring(url.indexOf('&'));
         if (searchString.length == 0) {
            window.location.href = url.substring(0, searchIndex) + url.substring(url.indexOf('&') + 1);
         } else {
            window.location.href = searchURL;
         }
      }
   }
});