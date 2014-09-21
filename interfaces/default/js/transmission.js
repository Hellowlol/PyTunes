// Last time we checked, was there a problem connecting to transmission?
var transmissionConnectionError = false;

$(document).ready(function () {
    $('.spinner').show();
    getTorrents();
    getStatus();
    setInterval(function () {
        getTorrents();
        getStatus();
    }, 10000);

	$('#all', '#queued', '#downloading', '#seeding', '#paused', '#finished', '#error').click(function(){
        $('.spinner').show();
        getTorrents();
    });
	$(':button').click(function(){
		var formData = new FormData($('form')[0]);
		$.ajax({
			url: '/transmission/to_client2',  //Server script to process data
			type: 'POST',
			xhr: function() {  // Custom XMLHttpRequest
				var myXhr = $.ajaxSettings.xhr();
				if(myXhr.upload){ // Check if upload property exists
					myXhr.upload.addEventListener('progress',progressHandlingFunction, false); // For handling the progress of the upload
				}
				return myXhr;
			},
			//Ajax events
			//beforeSend: beforeSendHandler,
			//success: completeHandler,
			//error: errorHandler,
			// Form data
			data: formData,
			//Options to tell jQuery not to process data or worry about content-type.
			cache: false,
			contentType: false,
			processData: false
		});
	});
});

/**
 * Start or stop all torrents
 */
$('#transmission-stop-all , #transmission-resume-all').click(function () {
    action = $(this).data('action');
    $.ajax({
        url: WEBDIR + 'transmission/' + action,
        success: function (response) {
            // Refresh torrent list after successfull request with a tiny delay
            if (response.result == 'success') {
                window.setTimeout(getTorrents, 500);
            }
        }
    });
});



function getTorrents() {

    var filter = '';

    if ($('#all').is(':visible')) {
        filter = 'All';
    } 
    else if ($('#queued').is(':visible')) {
        filter = 'Queued';
    } 
    else if ($('#downloading').is(':visible')) {
        filter = 'Downloading';
    } 
    else if ($('#seeding').is(':visible')) {
        filter = 'Seeding';
    } 
    else if ($('#paused').is(':visible')) {
        filter = 'Paused';
    } 
    else if ($('#stalled').is(':visible')) {
        filter = 'Stalled';
    } 
    else if ($('#finished').is(':visible')) {
        filter = 'Finished';
    } 
    else if ($('#error').is(':visible')) {
        filter = 'Error';
    } 

    $.ajax({
        url: WEBDIR + 'transmission/queue/' + filter,
        type: 'get',
        dataType: 'html',
        success: function (response) {
            if (filter === 'All') {
                $('#torrent-all').html('');
                $('#torrent-all').append(response);
            }
            else if (filter === 'Queued') {
                $('#torrent-queued').html('');
                $('#torrent-queued').append(response);
            }
            else if (filter === 'Downloading') {
                $('#torrent-downloading').html('');
                $('#torrent-downloading').append(response);
            }
            else if (filter === 'Seeding') {
                $('#torrent-seeding').html('');
                $('#torrent-seeding').append(response);
            }
            else if (filter === 'Paused') {
                $('#torrent-paused').html('');
                $('#torrent-paused').append(response);
            }
            else if (filter === 'Stalled') {
                $('#torrent-stalled').html('');
                $('#torrent-stalled').append(response);
            }
            else if (filter === 'Finished') {
                $('#torrent-finished').html('');
                $('#torrent-finished').append(response);
            }
            else if (filter === 'Error') {
                $('#torrent-error').html('');
                $('#torrent-error').append(response);
            }
            $('.spinner').hide();
            $(".torrent-error").click(function (event) {
                alert($(this).attr('message'));
            });
            $('select.select_cat').change(function(){
                $.ajax({
                    type: 'POST',
                    url: '/transmission/ChangeCat',
                    data: {
                        dir: $(this).val(), 
                        id: $(this).attr('torrid')
                        },
                    dataType: 'text',
                    success: function (response) {
                        //alert(response);
                        //if (response.result == 'success') {
                        //    window.setTimeout(getTorrents, 500);
                        //}
                    }
                });
            });
            $('.torrent-action').click(function (event) {
                event.preventDefault();
                // set spinner inside button
                $(this).html('<i class="icon-spinner icon-spin"></i>');

                // do ajax request
                $.ajax({
                    url: $(this).attr('href'),
                    success: function (response) {
                        // Refresh torrent list after successfull request with a tiny delay
                        if (response.result == 'success') {
                            window.setTimeout(getTorrents, 500);
                        }
                    }
                });
            });
            $('.torrent-files').click(function (event) {
                event.preventDefault();

                // do ajax request
                $.ajax({
                    url: $(this).attr('href'),
                    type: 'get',
                    dataType: 'text',
                    success: function (response) {
                        alert(response);
                        //if (response.result == 'success') {
                        //    window.setTimeout(getTorrents, 500);
                        //}
                    }
                });
            });
         }
    });
}


/**
 * Get General transmission stats
 */
function getStatus() {
    $.ajax({
        url: WEBDIR + 'transmission/stats',
        success: function (response) {
            if (response !== null && response.arguments && response.result === 'success') {
                uploadSpeed = getReadableFileSizeString(response.arguments.uploadSpeed);
                downloadSpeed = getReadableFileSizeString(response.arguments.downloadSpeed);

                $('#queue_upload').text(uploadSpeed + '/s');
                $('#queue_download').text(downloadSpeed + '/s');
            }

            // Transmission api not responding, show message if the last know state was OK
            if (response === null && transmissionConnectionError === false) {
                transmissionConnectionError = true;
                notify('Error', 'Could not connect to Transmission', 'error');
            }
        }
    });
}

/**
 * Converts bytes to readable filesize in kb, MB, GB etc.
 */
function getReadableFileSizeString(fileSizeInBytes) {
    var i = -1;
    var byteUnits = [' KB', ' MB', ' GB', ' TB', 'PB'];
    do {
        fileSizeInBytes = fileSizeInBytes / 1024;
        i++;
    } while (fileSizeInBytes > 1024);
    return Math.round(fileSizeInBytes, 0.1).toFixed(1) + byteUnits[i];
}



