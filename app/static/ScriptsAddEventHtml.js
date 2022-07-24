// add-event.html
// Clearing date and time if the user switched tabs
document.addEventListener('DOMContentLoaded', function(e) {
    let tabs = document.querySelectorAll('.tab-switch');
    // Assign variable to all datepicker input
    var dates = $("input[class$='.datepicker']");
    console.log(tabs)
    for (const tab of tabs) {
        tab.addEventListener('click', function(e)
            {
            // Set the datepicker value t0 0
            $(".datepicker").val("");

            dates.attr('value', '');
            dates.each(function(){
                $.datepicker._clearDate(this);
            });

            console.log("tab clicked");
            }
        );
    }
});

