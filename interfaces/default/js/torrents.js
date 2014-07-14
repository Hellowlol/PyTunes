
function search(query, engineid, catid) {
    if (query === undefined) return;
    alert(engineid);
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
            $('table').trigger("sorton", [[[3,1], [4,1]]]);
            $('.download').click(function (e) {
                var sendData = {
                    link: $(this).attr('torr_link'),
                    client: $(this).attr('torr_client')
                };
                $.ajax({
                    url: WEBDIR + "torrents/download",
                    type: 'get',
                    data: sendData,
                    dataType: 'text',
                    success: function (data) {
                        notify(data, 'Sent to ' + $(this).attr('torr_client'), 'success', '');
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
        search($('#query').val(), $('#engineid').val(), $('#catid').val());
        return false;
    });
});

