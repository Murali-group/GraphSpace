/**
 * Created by adb on 25/11/16.
 */


$(document).ready(function () {
    $.notifyDefaults({
        placement: {
            from: "top",
            align: "center"
        },
        delay: 15000,
        offset: 100,
        type: 'success'
    });

});

var utils = {
    initializeTabs: function () {
        utils.selectTab(document.location.toString());

        $('.nav-pills a').on('shown.bs.tab', function (e) {
            // Change hash for page-reload. It will add the appropriate hash tag in the url for current tab.
            window.location.hash = e.target.hash;
        });
    },
    selectTab: function (url) {
        // Go to Specific Tab on Page Reload or Hyperlink
        if (url.match('#')) {
            $('.nav-pills a[href="#' + url.split('#')[1] + '"]').tab('show');
        }
    },
    dateFormatter: function (value, row, index) {
        return moment(value).fromNow();
    }
};