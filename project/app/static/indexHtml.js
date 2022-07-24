// index.html

// Prompt to ask are you sure
document.addEventListener('DOMContentLoaded', function(e) {
    // Handle the delete button in the long event
    $('.dellongevbtn').each(function(){
        $(this).click(function(){
            // Get the Long event ID (from the button id "delLongEvBtn 2" to the event name id "del_long_name 2")
            id = $(this).attr('id').replace('delLongEvBtn ','');
            console.log(id);
            event_name = "del_long_name " + id;
            console.log(event_name);
            event_name = document.getElementById(event_name);
            console.log(event_name);

            // Change the value of the h5 with id eventname to show the event that was selected
            event_name = $(event_name).val();
            $('#eventname').text(event_name);
        });
    });
    $('.delshortevbtn').each(function() {
        $(this).click(function(){
            console.log("clicked");
            // Get the Short event ID (from the button id "delShortEvBtn 2" to the event name id "del_short_name 2")
            id = $(this).attr('id').replace('delShortEvBtn ','');
            console.log(id);
            event_name = "del_short_name " + id;
            console.log(event_name);
            event_name = document.getElementById(event_name);
            console.log(event_name);

            // Change the value of the h5 with id eventname to show the event that was selected
            event_name = $(event_name).val();
            console.log(event_name);
            $('#eventname').text(event_name);
        });
    });

    $('#submit').click(function(){
        delform = "deleteForm " + id
        console.log("submitting " + delform);
        delform = document.getElementById(delform);
        console.log(delform);
        $(delform).submit();
    });
});



// Handle opening offcanvas
document.addEventListener('DOMContentLoaded', function(e) {
    // Short Event
    let short_event_list = document.querySelectorAll('.short_events');
    for (const event of short_event_list) {
        event.addEventListener('click', function(e) {
        console.log(event);

        // e.g short event 1
        var short_event_id = $(event).attr('id');
        console.log(short_event_id);

        // e.g offcanvas short event 1
        var OffcanvasId = 'offcanvas '+short_event_id;
        console.log(OffcanvasId);

        var myOffcanvas = document.getElementById(OffcanvasId)
        var bsOffcanvas = new bootstrap.Offcanvas(myOffcanvas);
        console.log(bsOffcanvas);
        bsOffcanvas.show();
        });
    };

    // Long Events
    let long_event_list = document.querySelectorAll('.long_events');
    for (const event of long_event_list) {
        event.addEventListener('click', function(e) {
        console.log(event);

        // e.g long event 1
        var long_event_id = $(event).attr('id');
        console.log(long_event_id);

        // e.g offcanvas longevent 1
        var OffcanvasId = 'offcanvas '+long_event_id;
        console.log(OffcanvasId);

        var myOffcanvas = document.getElementById(OffcanvasId)
        var bsOffcanvas = new bootstrap.Offcanvas(myOffcanvas);
        console.log(bsOffcanvas);
        bsOffcanvas.show();
        });
    };
});