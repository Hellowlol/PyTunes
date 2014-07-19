function loadClients() {
    //alert('clients');
    $.ajax({
        url: WEBDIR + 'torrents/GetClients',
        type: 'get',
        dataType: 'text',
        success: function (data) {
            if (data === null) return errorHandler();
            $('#defclient').append(data);
        }
    });
}

function search(query, engineid, catid) {
    if (query === undefined) return;
    $.ajax({
        url: WEBDIR + 'torrents/search?q=' + query + '&engineid=' + engineid + '&cat=' + catid,
        type: 'get',
        dataType: 'html',
        timeout: 60000,
        beforeSend: function () {
            $('#results_table_body').empty();
            $('.spinner').show();
        },
        success: function (data) {
            if (data === null) return errorHandler();
            $('#results_table_body').append(data);
            $('table').trigger("update");
            $('table').trigger("sorton", [
                [
                    [3, 1],
                    [4, 1]
                ]
            ]);
            $('.download').click(function () {
                var link = $(this).attr('torr_link');
                var sendData = {
                    'link': link
                };
                $.ajax({
                    url: WEBDIR + "torrents/getdefclient",
                    type: 'get',
                    data: sendData,
                    dataType: 'json',
                    success: function () {
                        $.ajax({
                            url: WEBDIR + data.path,
                            type: 'get',
                            dataType: 'text',
                            success: function () {
                                notify('Torrent Download', 'Sent to ' + data.client, 'success', '');
                            }
                        });
                    }

                });
            });
        },
        complete: function () {
            $('.spinner').hide();
        },
        error: function () {
            //add error block
        }
    });
}

$(document).ready(function () {
    $('#torrent_search_table').tablesorter();
    $('#searchform').submit(function () {
        //alert('search');
        //e.preventDefault();
        search($('#query').val(), $('#engineid').val(), $('#catid').val());
        return false;
    });
    loadClients();
    // Client change. send command, reload options.
    $('#defclient').change(function () {
        $.ajax({
            sendData = {client: $(this).val()}
            url: WEBDIR + 'settings/SetTorrClient',
            type: 'get',
            dataType: 'text',
            success: function (data) {
                $.ajax({
                    url: WEBDIR + 'torrents/GetClients',
                    type: 'get',
                    dataType: 'text',
                    success: function (data) {
                        if (data === null) return errorHandler();
                        $('#defclient').empty();//combine these two
                        $('#defclient').append(data);
            notify('XBMC', 'Server change ' + data, 'info');
                    }
                });
            }
        });
    });
});
