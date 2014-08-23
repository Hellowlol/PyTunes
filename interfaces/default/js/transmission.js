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

    // Torrent button ajax load
    //$(document.body).off('click', '#torrent-queue .torrent-action a');
    //$(document.body).on('click', '#torrent-queue .torrent-action a', function(event) {
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
        success: function (response) {
            if (response !== null && response.arguments && response.result === 'success') {
                //$('#torrent-queue').html('');
                $('#torrent-all').html('');
                //$('#torrent-paused').html('');

                // Empty queue
                if (response.arguments.torrents.length === 0) {
                    //$('#torrent-queue').html('<tr><td colspan="5">Queue is empty</td></tr>');
                    $('#torrent-all').html('<tr><td colspan="5">Queue is empty</td></tr>');
                    //$('#torrent-paused').html('<tr><td colspan="5">Queue is empty</td></tr>');
                }

                $.each(response.arguments.torrents, function (index, torrent) {
                    tr = $('<tr>');

                    var progressBar = $('<div>');
                    progressBar.addClass('bar');
                    progressBar.css('width', (torrent.percentDone * 100) + '%');

                    var progress = $('<div>');
                    progress.addClass('progress');
                    if (torrent.percentDone >= 1) {
                        progress.addClass('progress-success');
                    }
                    progress.append(progressBar);

                    // Round to 2 decimals
                    //ratio = Math.round(torrent.uploadRatio*100) / 100;
                    ratio = torrent.uploadRatio;
                    if (ratio == -1) {
                        ratio = 0.00;
                    }

                    // Button group
                    buttons = $('<div>').addClass('btn-group');

                    // Action button (pause or resume)
                    actionButton = generateTorrentActionButton(torrent);
                    buttons.append(actionButton);

                    // Remove torrent button
                    removeButton = $('<a>').
                    addClass('btn btn-mini').
                    html('<i class="icon-remove"></i>').
                    attr('href', WEBDIR + 'transmission/remove/' + torrent.id).
                    attr('title', 'Remove torrent');
                    buttons.append(removeButton);

                    var doneSize = torrent.totalSize - torrent.leftUntilDone;
                    // Remove torrent and files button
                    removeButtonAndFiles = $('<a>').
                    addClass('btn btn-mini').
                    html('<i class="icon-trash"></i>').
                    attr('href', WEBDIR + 'transmission/remove_with_files/' + torrent.id).
                    attr('title', 'Remove torrent and all files');
                    buttons.append(removeButtonAndFiles);

                    var doneSize = torrent.totalSize - torrent.leftUntilDone;
                    // View and edit files 
                    viewFilesButton = $('<a>').
                    addClass('btn btn-mini').
                    html('<i class="icon-copy"></i>').
                    attr('href', WEBDIR + 'transmission/ViewFiles/' + torrent.id).
                    attr('title', 'View and edit files');
                    buttons.append(viewFilesButton);

                    var doneSize = torrent.totalSize - torrent.leftUntilDone;

                    tr.append(
                    $('<td>').html(torrent.name + '<br><small><i class="icon-download"></i> ' + getReadableFileSizeString(torrent.rateDownload) + '/s' + '&nbsp;&nbsp;' + ' <i class="icon-upload"></i> ' + getReadableFileSizeString(torrent.rateUpload) + '/s</small>'),
                    $('<td>').text(torrent.downloadDir),
                    $('<td>').text(ratio),
                    $('<td>').text(torrent.priorities),
                    $('<td>').text(torrent.queuePosition),
                    $('<td>').text(getReadableFileSizeString(doneSize)),
                    $('<td>').text(getReadableFileSizeString(torrent.totalSize)),
                    $('<td>').text(getReadableTime(torrent.eta)),
                    $('<td>').text(torrentStatus(torrent.status)),
                    //$('<td>').addClass('span3').html(progress).text('<br><small>').text(getReadableFileSizeString(doneSize) + '/' + getReadableFileSizeString(torrent.totalSize)),
                    $('<td>').addClass('span3').html(progress),
                    $('<td>').addClass('torrent-action').append(buttons));
                $('#torrent-all').append(tr)
            });
            $('.spinner').hide();
            }
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
