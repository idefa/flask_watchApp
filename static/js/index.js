$(function () {

    //BEGIN TO-DO-LIST
    $('.todo-list').slimScroll({
        "width": '100%',
        "height": '250px',
        "wheelStep": 30
    });
    $( ".sortable" ).sortable();
    $( ".sortable" ).disableSelection();
    //END TO-DO-LIST
    function counterNum(obj, start, end, step, duration) {
        $(obj).html(start);
        setInterval(function(){
            var val = Number($(obj).html());
            if (val < end) {
                $(obj).html(val+step);
            } else {
                clearInterval();
            }
        },duration);
    }
    //END COUNTER FOR SUMMARY BOX
});

