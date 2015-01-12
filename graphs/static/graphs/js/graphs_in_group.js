$(document).ready(function() {

    //these accordions make up the side menu
    //and set it to the minimum value when page is viewed
   $('#accordion_description').accordion({
      collapsible: true
    });

   $('#accordion_owner').accordion({
      collapsible: true,
   });

   $('#accordion_members').accordion({
      collapsible: true,
   });

   $('#accordion_tags').accordion({
      collapsible: true,
   });
});