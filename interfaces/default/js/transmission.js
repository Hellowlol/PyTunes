// Last time we checked, was there a problem connecting to transmission?
var transmissionConnectionError = false;

$(document).ready(function () {
    $('.spinner').show();
    getTorrents();
    getStatus();
    setInterval(function () {
        getTorrents();
        getStatus();
    }, 4000);

	$(':button').click(function(){
		var formData = new FormData($('form')[0]);
		$.ajax({
			url: 'transmission/to_client2',  //Server script to process data
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
	$(document.body).off('click', '#torrent-all .torrent-action a');
    $(document.body).on('click', '#torrent-all .torrent-action a', function (event) {
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
    $.ajax({
        url: WEBDIR + 'transmission/queue',
        type: 'get',
        dataType: 'html',
        success: function (response) {
                $('#torrent-all').html('');
               $('#torrent-all').append(response);
            $('.spinner').hide();
         }
    });
}

/**
 * Generate a start or stop button based on the torrent status
 */
function generateTorrentActionButton(torrent) {
    button = $('<a>').addClass('btn btn-mini');
    // Resume button if torrent is paused
    if (torrent.status === 0) {
        button.html('<i class="icon-play"></i>');
        button.attr('href', WEBDIR + 'transmission/start/' + torrent.id);
        button.attr('title', 'Resume torrent');
    } else { // Pause button
        button.html('<i class="icon-pause"></i>');
        button.attr('href', WEBDIR + 'transmission/stop/' + torrent.id);
        button.attr('title', 'Pause torrent');
    }

    return button;
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

/**
 * Converts seconds to readable time.
 */
function getReadableTime(timeInSeconds) {
    if (timeInSeconds < 1) {
        return '0:00:00';
    }

    var days = parseInt(timeInSeconds / 86400, 10) % 7;
    var hours = parseInt(timeInSeconds / 3600, 10) % 24;
    var minutes = parseInt(timeInSeconds / 60, 10) % 60;
    var seconds = parseInt(timeInSeconds % 60, 10);

    // Add leading 0 and : to seconds
    seconds = ':' + (seconds < 10 ? "0" + seconds : seconds);

    if (days < 1) {
        days = '';
    } else {
        days = days + 'd ';
        // remove seconds if the eta is 1 day or more
        seconds = '';
    }
    return days + hours + ":" + (minutes < 10 ? "0" + minutes : minutes) + seconds;
}

/**
 * Get textual representation of torrent status
 *
 * Since torrent status is retured as integer by the Transmission API the number must be mapped to a string
 */
function torrentStatus(statusNr) {
    states = ['Paused', 'unkown 1', 'unknown 2', 'Queued', 'Downloading', 'unknown 5', 'Seeding'];
    return states[statusNr];
}
