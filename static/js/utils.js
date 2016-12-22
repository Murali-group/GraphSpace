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
        z_index: 100000,
        type: 'success'
    });

    $('.sidebar-nav-pills').click(function (e) {
        $('.gs-sidebar-nav').removeClass('active');
        $($(this).data('target')).addClass('active');
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

var UndoManager = function (onUndo, onRedo, onUpdate) {
    this.state = [];
    this.index = -1;

    this.onUndo = onUndo;
    this.onRedo = onRedo;
    this.onUpdate = onUpdate;
};

UndoManager.prototype = {
    constructor: UndoManager,
    undo: function () {
        if (this.index >= 0) {
            this.index = this.index - 1;
            this.onUndo(this.state[this.index]);
        } else {
            this.onUndo();
        }
    },
    redo: function () {
        if (this.index+1 < this.state.length) {
            this.index = this.index + 1;
            this.onRedo(this.state[this.index]);
        } else {
            this.onRedo();
        }
    },
    update: function (action) {
        this.index = this.index + 1
        this.state = this.state.slice(0, this.index);
        this.onUpdate(this.state.push(action));
    }
};
