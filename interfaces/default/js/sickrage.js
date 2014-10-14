$(document).ready(function () {
    $(window).trigger('hashchange');
    loadTab();

    // Load data on tab display
    $('a[data-toggle="tab"]').click(function (e) {
        $('#search').val('');
        searchString = '';
    }).on('shown', loadTab);

    $(window).trigger('hashchange');


    $('#restart').click(function () {
        restartSB();
    });

    $('#shutdown').click(function () {
        shutdownSB();
    });

    $('#add_show_button').click(function () {
        $(this).attr('disabled', true);
        searchTvDb($('#add_show_name').val());
    });

    $('#add_indexerid_button').click(function () {
        addShow($('#add_show_select').val());
    });

    $('#cancel_show_button').click(function () {
        cancelAddShow();
    });

});

function loadTab() {
    if ($('#tvshows').is(':visible')) {
        loadShows();
    } 
    else if ($('#nextaired').is(':visible')) {
        loadNextAired();
    } 
    else if ($('#history').is(':visible')) {
        loadSickrageHistory(25);
    } 
    else if ($('#logs').is(':visible')) {
        loadLogs();
    } 
    $('.spinner').hide();
}

function loadShows() {
    $('.spinner').show();
    $.ajax({
        url: WEBDIR + 'sickrage/GetShowList',
        type: 'get',
        dataType: 'text',
        success: function (result) {
            $('#tvshows_table_body').append(result);
            $('.spinner').hide();
        }
    });
}

function loadShow(indexerid) {
    $.ajax({
        url: WEBDIR + 'sickrage/GetShow?indexerid=' + indexerid,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            data = data.data;

            var table = $('<table>');
            table.addClass('table table-bordered table-striped table-condensed');

            row = $('<tr>');
            row.append('<th>Status</th><td>' + data.status + '</td>');
            table.append(row);

            row = $('<tr>');
            row.append('<th>Airs</th><td>' + data.airs + '</td>');
            table.append(row);

            row = $('<tr>');
            row.append('<th>Language</th><td>' + data.language + '</td>');
            table.append(row);

            row = $('<tr>');
            row.append('<th>Location</th><td>' + data.location + '</td>');
            table.append(row);

            row = $('<tr>');
            row.append('<th>Quality</th><td>' + data.quality + '</td>');
            table.append(row);

            row = $('<tr>');
            row.append('<th>Network</th><td>' + data.network + '</td>');
            table.append(row);

            modalContent = $('<div>');
            modalContent.append(
            $('<img>').attr('src', WEBDIR + 'sickrage/GetBanner/' + indexerid).addClass('img-rounded'),
            $('<hr>'),
            table);

            var modalButtons = {
                'Show': function () {
                    window.location = WEBDIR + 'sickrage/view/' + indexerid;
                }
            };

            showModal(data.show_name, modalContent, modalButtons);
        }
    });
}

function loadNextAired(options) {
    $('.spinner').show();
    var defaults = {
        limit: 0
    };
    $.extend(defaults, options);

    $.ajax({
        url: WEBDIR + 'sickrage/GetNextAired',
        type: 'get',
        dataType: 'json',
        success: function (result) {
            // If sickrage not configured, return false (Dashboard)
            if (result === null) return false;

            if (result.data.soon.length === 0) {
                var row = $('<tr>');
                row.append($('<td>').html('No future episodes found'));
                $('#nextaired_table_body').append(row);
                return false;
            }

            var soonaired = result.data.soon;
            var todayaired = result.data.today;
            var nextaired = todayaired.concat(soonaired);
            var lateraired = result.data.later;

            // Loop next airing episodes
            $.each(nextaired, function (i, tvshow) {
                if (defaults.limit !== 0 && i === defaults.limit) {
                    return false;
                }
                var row = $('<tr>');
                var name = $('<a>').attr('href', '#').html(tvshow.show_name).click(function (e) {
                    loadShow(tvshow.indexerid);
                });

                row.append(
                $('<td>').append(name),
                $('<td>').html(tvshow.ep_name),
                $('<td>').html(tvshow.airdate));

                $('#nextaired_table_body').append(row);
            });

            // Loop later airing episodes
            $.each(lateraired, function (i, tvshow) {
                if (defaults.limit !== 0 && i === defaults.limit) {
                    return false;
                }
                var row = $('<tr>');
                var name = $('<a>').attr('href', '#').html(tvshow.show_name).click(function (e) {
                    loadShow(tvshow.indexerid);
                });

                row.append(
                $('<td>').append(name),
                $('<td>').html(tvshow.ep_name),
                $('<td>').html(tvshow.airdate));

                $('#nextaired_table_body').append(row);
            });

            $('#nextaired_table_body').parent().trigger('update');
        }
    });
}

function loadSickrageHistory(limit) {
    $('.spinner').show();
    $.ajax({
        url: WEBDIR + 'sickrage/GetHistory?limit=' + limit,
        type: 'get',
        dataType: 'json',
        success: function (result) {
            if (result.data.legth === 0) {
                var row = $('<tr>');
                row.append($('<td>').html('History is empty'));
                $('#history_table_body').append(row);
            }

            $.each(result.data, function (indexerid, tvshow) {
                var row = $('<tr>');
                row.append(
                $('<td>').html(tvshow.date),
                $('<td>').append($('<a>').text(tvshow.show_name).attr('href', WEBDIR + 'sickrage/view/' + tvshow.indexerid)),
                $('<td>').html(tvshow.season + 'x' + tvshow.episode),
                $('<td>').append(sickrageStatusLabel(tvshow.status)),
                $('<td>').html(tvshow.quality));

                $('#history_table_body').append(row);
            });
            $('#history_table_body').parent().trigger('update');
        }
    });
}

function loadLogs() {
    $('.spinner').show();
    $.ajax({
        url: WEBDIR + 'sickrage/GetLogs',
        type: 'get',
        dataType: 'json',
        success: function (result) {
            if (result.data.legth === 0) {
                var row = $('<tr>');
                row.append($('<td>').html('Log is empty'));
                $('#log_table_body').append(row);
            }
            $.each(result.data, function (i, logitem) {
                var row = $('<tr>');
                row.append($('<td>').html(logitem));
                $('#log_table_body').append(row);
            });
        }
    });
}

function shutdownSB() {
    if (confirm('Are you sure? Shutdown. ')) {
        $.ajax({
            url: WEBDIR + 'sickrage/Shutdown',
            type: 'get',
            dataType: 'json',
            timeout: 15000,
            success: function (data) {
                if (data.result == 'success') {
                    notify('OK', data.message, 'success');
                    return;
                } else {
                    notify('Error', data.message, 'error');
                    return;
                }
            },
            error: function (data) {
                notify('Error', 'Unable to shutdown.', 'error', 1);
            }
        });
    }
}

function restartSB() {
    if (confirm('Are you sure? Restart.')) {
        $.ajax({
            url: WEBDIR + 'sickrage/Restart',
            type: 'get',
            dataType: 'json',
            timeout: 15000,
            success: function (data) {
                if (data.result == 'success') {
                    notify('OK', data.message, 'success');
                    return;
                } else {
                    notify('Error', data.message, 'error');
                    return;
                }
            },
            error: function (data) {
                notify('Error', 'Unable to restart.', 'error', 1);
            }
        });
    }
}


function searchTvDb(query) {
    $.ajax({
        url: WEBDIR + 'sickrage/SearchShow?query=' + query,
        type: 'get',
        dataType: 'xml',
        success: function (result) {
            series = $(result).find('Series');
            if (series.length === 0) {
                $('#add_show_button').attr('disabled', false);
                notify('No Series Found', query, 'error');
                return;
            }
            $('#add_show_select').html('');
            series.each(function () {
                var indexerid = $(this).find('seriesid').text();
                var showname = $(this).find('SeriesName').text();
                var language = $(this).find('language').text();
                var option = $('<option>');
                option.attr('value', indexerid);
                option.html(showname + ' (' + language + ')');
                $('#add_show_select').append(option);
            });
            $('#add_show_name').hide();
            $('#cancel_show_button').show();
            $('#add_show_select').fadeIn();
            $('#add_show_button').attr('disabled', false).hide();
            $('#add_indexerid_button').show();
        }
    });
}

function addShow(indexerid) {
    $.ajax({
        url: WEBDIR + 'sickrage/AddShow?indexerid=' + indexerid,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            notify('Add TV show', data.message, 'success');
            cancelAddShow();
        }
    });
}

function cancelAddShow() {
    $('#add_show_name').val('');
    $('#add_show_select').hide();
    $('#cancel_show_button').hide();
    $('#add_show_name').fadeIn();
    $('#add_indexerid_button').hide();
    $('#add_show_button').show();
}

function sickrageStatusLabel(text) {
    var statusOK = ['Continuing', 'Downloaded', 'HD'];
    var statusInfo = ['Snatched', 'Unaired'];
    var statusError = ['Ended'];
    var statusWarning = ['Skipped'];

    var label = $('<span>').addClass('label').text(text);

    if (statusOK.indexOf(text) != -1) {
        label.addClass('label-success');
    } else if (statusInfo.indexOf(text) != -1) {
        label.addClass('label-info');
    } else if (statusError.indexOf(text) != -1) {
        label.addClass('label-important');
    } else if (statusWarning.indexOf(text) != -1) {
        label.addClass('label-warning');
    }

    var icon = sickrageStatusIcon(text, true);
    if (icon !== '') {
        label.prepend(' ').prepend(icon);
    }
    return label;
}

function sickrageStatusIcon(iconText, white) {
    var text = [
        'Downloaded',
        'Continuing',
        'Snatched',
        'Unaired',
        'Archived',
        'Skipped'];
    var icons = [
        'icon-download-alt',
        'icon-repeat',
        'icon-share-alt',
        'icon-time',
        'icon-lock',
        'icon-fast-forward'];

    if (text.indexOf(iconText) != -1) {
        var icon = $('<i>').addClass(icons[text.indexOf(iconText)]);
        if (white === true) {
            icon.addClass('icon-white');
        }
        return icon;
    }
    return '';
}
