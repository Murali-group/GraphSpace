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

   //Appends appropriate terms to the url depending on what is being searched for
   //For example, it appends ?queryTerm if there are no query terms, or it appends &queryTerm=
   //to the end of the current url if a queryterm already exists
   function urlAppender(searchVal, element1, element2) {
      if (searchVal.length > 0) {
         if (document.URL.indexOf(element2) == -1) {
            if (document.URL.indexOf(element1) == -1) {
               window.location.href = document.URL + '?' + element1 + searchVal;
            } else {
               window.location.href = document.URL.substring(0, document.URL.indexOf('?' + element1) - 1) + '?' + element1 + searchVal;
            }
         } else {
            element2Index = document.URL.indexOf(element2);
            element1Index = document.URL.indexOf(element1);
            if (element1Index > element2Index) {
               window.location.href = document.URL.substring(0, element1Index-1) + '&' + element1 + searchVal;
            } else {
               window.location.href = document.URL.substring(0, element1Index-1) + '?' + document.URL.substring(element2Index, document.URL.length) + '&' + element1 + searchVal;
            }
         }
      } else {
         return alert("Please enter a term to search for!");
      }
   }
});