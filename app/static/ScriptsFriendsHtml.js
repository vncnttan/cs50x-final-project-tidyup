// friends.html

document.addEventListener('DOMContentLoaded', function(e) {
    // Prompt to ask are you sure
    // Handle the delete button in the long event
    $('.delfriend').each(function(){
        $(this).click(function(){
            // Get the Long event ID (from the button id "deleteFriend 2" to the friend id "del_long_name 2")
            id = $(this).attr('id').replace('delFriend ','');
            console.log(id);
        });
    });

    // Submit the form if people click submit on the modal
    $('#deleteFriend').click(function(){
        delfriend = "deleteFriend " + id
        console.log("submitting " + delfriend);
        delfriend = document.getElementById(delfriend);
        console.log(delfriend);
        $(delfriend).submit();
    });

    // Open specific offcanvas after clicking div friend
    let friend_list = document.querySelectorAll('.friends');
    console.log(friend_list);
    for (const friend of friend_list) {
      friend.addEventListener('click', function(e) {
        console.log(friend);

        // e.g friend 1
        var friend_id = $(friend).attr('id');
        console.log(friend_id);

        // e.g offcanvas friend 1
        var OffcanvasId = 'offcanvas '+friend_id;
        console.log(OffcanvasId);

        var myOffcanvas = document.getElementById(OffcanvasId)
        var bsOffcanvas = new bootstrap.Offcanvas(myOffcanvas);
        console.log(bsOffcanvas);
        bsOffcanvas.show();
      });
    };
});