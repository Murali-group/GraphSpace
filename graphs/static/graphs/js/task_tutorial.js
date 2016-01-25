$(document).ready(function() {
    $('#joyRideTipContent').joyride({
      autoStart : true,
      postStepCallback : function (index, tip) {
      if (index == 2) {
        $(this).joyride('set_li', false, 1);
      }
    },
    modal:true,
    expose: true
    });
});