 $('[data-player-control]').click(function () {
 		alert('click')
        var action = $(this).attr('data-player-control');
        $.get(WEBDIR + 'samsungtv/sendkey?action='+action);
        //alert('Done ', action)
    });