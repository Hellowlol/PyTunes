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
            byteSizeOrdering()
            $('#results_table_body').append(data);
            $('table').trigger("update");
            $('table').trigger("sorton", [
                [
                    [3, 1],
                    [4, 1]
                ]
            ]);
            $('.download').click(function () {
                var sendData = {
                    link: $(this).attr('torr_link')
                };
                $.ajax({
                    url: WEBDIR + $('#defclient').val(),
                    type: 'get',
                    data: sendData,
                    dataType: 'text',
                    success: function () {
                        notify('Torrent Download', 'Sent to ' + $("#defclient option:selected").text(), 'success', '');
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
    $('#searchform').submit(function (e) {
        e.preventDefault();
        search($('#query').val(), $('#engineid').val(),         $('#catid').val());
        return false;
    });
    loadClients();
    // Client change. send command, reload options.
    $('#defclient').change(function () {
        sendData = {client: $("#defclient option:selected").text()};
        $.ajax({
            url: WEBDIR + 'settings/SetTorrClient',
            type: 'get',
            data: sendData,
            dataType: 'text',
            success: function (data) {
                notify('Torrents', 'Client change ' + $("#defclient option:selected").text() + data, 'info');
            }
        });
    });
});
