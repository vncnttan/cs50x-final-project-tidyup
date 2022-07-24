export var events = function () {
    var tmp = null;
    $.ajax({
        'async': false,
        'type': "POST",
        'url': "/events",
        'contentType': "application/json",
        'traditional': "true",
        'success': function (data) {
            tmp = data
        },
    });
    return tmp;
}();
