
function search(query, catid) {
    if (query === undefined) return;
    $.ajax({
        url: WEBDIR + 'torrents/search?q=' + query + '&cat=' + catid,
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
            $('.download').click(function (e) {
                var sendData = {
                    hash: $(this).attr('torr_link'),
                    cmd: 'download'
                };
                $.ajax({
                    //alert('load movie ' + id);
                    url: WEBDIR + "qbittorrent/command",
                    type: 'get',
                    data: sendData,
                    dataType: 'text',
                    success: function (data) {
                        notify(data, 'Sent to qBittorrent', 'success', '');
                    }

                });
            });
        },
        complete: function () {
            $('.spinner').hide();
        }
    });
}

$(document).ready(function () {
    $('#searchform').submit(function () {
        search($('#query').val(), $('#catid').val());
        return false;
    });
});

