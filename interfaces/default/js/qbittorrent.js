$("#qbt_rp_all_button").click(function () {
    if ($("#qbt_rp_all_icon").hasClass("icon-pause")) {
        $('#qbt_rp_all_icon').html(' Resume');
        $('#qbt_rp_all_icon').removeClass("icon-pause").addClass("icon-play");
        $.get(WEBDIR + 'qbittorrent/command/pauseall');
    } else {
        $('#qbt_rp_all_icon').html(' Pause');
        $('#qbt_rp_all_icon').removeClass("icon-play").addClass("icon-pause");
        $.get(WEBDIR + 'qbittorrent/command/resumeall');
    }
});

function get_torrents() {
    $.ajax({
        'url': WEBDIR + 'qbittorrent/fetch',
            'dataType': 'json',
            'success': function (response) {
            $('#torrents-queue').html("");
            $('#error_message').text("");
            var pausestatus = ["error", "pausedUP", "pausedDL", "checkingUP"];
            var numberofloop = 0;
            var times_in = 0;

            $.each(response, function (index, torrent) {
                tr = $('<tr>');
                numberofloop += 1;

                if (jQuery.inArray(torrent.state, pausestatus) !== -1) {
                    times_in += 1;
                }


                var progressBar = $('<div>');
                progressBar.addClass('bar');
                progressBar.css('width', (torrent.progress * 100) + '%');
                var progress = $('<div>');
                progress.addClass('progress');
                if (torrent.state === "uploading") {
                    progress.addClass('progress');
                }
                if (torrent.state === "downloading") {
                    progress.addClass('progress-success');
                }
                if (torrent.state === "stalledUP" || torrent.state === "stalledDL") {
                    progress.addClass('progress-danger');
                }
               if (torrent.state === "pausedDL" || torrent.state === "pausedUP") {
                    progress.addClass('progress-warning');
                }
                if (torrent.state === "checkingUP") {
                    progress.addClass('progress-warning');
                }
                if (torrent.state === "error") {
                    progress.addClass('progress-danger progress-striped active');
                }
                progress.append(progressBar);
                progress.append("&nbsp;" + Math.round(torrent.progress * 100) + "%");

                // Button group
                buttons = $('<div>').addClass('btn-group');


                // Action button (pause or resume)
                actionButton = generateTorrentActionButton(torrent);
                buttons.append(actionButton);

                // Remove button
                removeButton = $('<a class="qbt_removetorrent" data-action="delete" data-hash="" data-name="">').
                addClass('btn btn-mini').
                html('<i class="icon-remove"></i>').
                attr('data-hash', torrent.hash).
                attr('data-name', torrent.name).
                attr('title', 'Remove torrent');
                deleteButton = $('<a class="qbt_deletetorrent" data-action="deletePerm" data-hash="" data-name="">').
                addClass('btn btn-mini').
                html('<i class="icon-trash"></i>').
                attr('data-hash', torrent.hash).
                attr('data-name', torrent.name).
                attr('title', 'Delete torrent');
                buttons.append(removeButton).append(deleteButton);

                tr.append(

                $('<td>').addClass('qbt_name').html(torrent.name),
                $('<td>').addClass('qbt_size').text(torrent.size),
                $('<td>').addClass('qbt_seeds').text(torrent.num_seeds),
                $('<td>').addClass('qbt_peers').text(torrent.num_leechs),
                $('<td>').addClass('qbt_down_speed').text(torrent.dlspeed),
                $('<td>').addClass('qbt_up_speed').text(torrent.upspeed),
                $('<td>').addClass('qbt_ratio').text(torrent.ratio),
                $('<td>').addClass('qbit_eta').text(torrent.eta),
                $('<td>').addClass('qbt_state').text(torrent.state),
                $('<td>').addClass('span3 qbit_progress').html(progress),
                $('<td>').addClass('torrent-action').append(buttons));
                $('#torrents-queue').append(tr);
            });
            if (times_in === numberofloop) {
                $("#qbt_rp_icon").removeClass("icon-pause").addClass("icon-play");
            } else {
                $("#qbt_rp_icon").removeClass("icon-play").addClass("icon-pause");
            }
            $('.spinner').hide();

        }


    });
}

function get_speed() {
    $.ajax({
        'url': WEBDIR + 'qbittorrent/get_speed',
            'dataType': 'json',
            'success': function (response) {
            $.each(response, function (index, torrent) {
                $('#qbittorrent_speed_down').text(torrent.qbittorrent_speed_down);
                $('#qbittorrent_speed_up').text(torrent.qbittorrent_speed_up);
            });
        }
    });
}

function get_limits() {
    $.ajax({
        'url': WEBDIR + 'qbittorrent/get_limits',
        'dataType': 'json',
        'success': function (response) {
            $('#qbittorrent_limit_down').text(response.qbittorrent_limit_down);
            $('#qbittorrent_limit_up').text(response.qbittorrent_limit_up);
        }
    });
}

function generateTorrentActionButton(torrent) {
    button = $('<a>').addClass('btn btn-mini qbt_rp');
    // Resume button if torrent is paused
    var status = torrent.state;
    var icon = "";
    var cmd = "";
    var title = "";

    if (status == "pausedUP" || status == "pausedDL" || status == "error" || status == "checkingUP") {
        icon = "icon-play";
        title = "Resume torrent";
        cmd = "resume";
    } else {
        icon = "icon-pause";
        title = "Pause torrent";
        cmd = "pause";
    }

    // Set icon, command and title to button
    button.html('<i class="' + icon + '"></i>');
    button.attr('title', title);
    button.attr('data-hash', torrent.hash);
    button.attr('data-name', torrent.name);
    button.attr('data-action', cmd);
    return button;
}


// remove torrent
$(document).on('click', '.qbt_removetorrent', function () {
      var r = $(this);
    if (confirm('Are you sure you want to delete torrent' + r.attr('data-name'))) {
            $.get(WEBDIR + 'qbittorrent/command/' + r.attr('data-action') + '/' + r.attr('data-hash') + '/' + r.attr('data-name') + '/', function () {});
            get_torrents();
        }
});

// remove torrent and all files
$(document).on('click', '.qbt_deletetorrent', function () {
    var r = $(this);
    if (confirm('Are you sure you want to delete the file and torrent ' + r.attr('data-name'))) {
            $.get(WEBDIR + 'qbittorrent/command/' + r.attr('data-action') + '/' + r.attr('data-hash') + '/' + r.attr('data-name') + '/', function () {});
            get_torrents();
    }

});

// resume/pause all torrents
$(document).on('click', '.qbt_rp', function () {
    if ($(this).children("i").hasClass("icon-play")) {
        ($(this).children("i").removeClass("icon-play").addClass("icon-pause"));
    } else {
        ($(this).children("i").removeClass("icon-pause").addClass("icon-play"));
    }
    $.get(WEBDIR + 'qbittorrent/command/' + $(this).attr('data-action') + '/' + $(this).attr('data-hash') + '/' + $(this).attr('data-name') + '/', function () {

    });

});

//sets speed up and down
$(document).on('focusout', '.container-fluid .content #ss input', function () {
    $.get(WEBDIR + 'qbittorrent/set_speedlimit/' + $(this).data('action') + '/' + $(this).val() + '/', function () {

    });

});


// Loads the moduleinfo
$(document).ready(function () {
    $('.spinner').show();
    get_torrents();
    get_speed();
    get_limits();
    setInterval(function () {
        get_speed();
    }, 1000);
    setInterval(function () {
        get_torrents();
    }, 15000);
    setInterval(function () {
        get_limits();
    }, 60000);
});
