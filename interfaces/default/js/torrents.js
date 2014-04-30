
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
            $('a.ajax-link').click(function (e) {
                e.preventDefault();
                var link = $(this);
                 $.getJSON(link.attr('href'), function () {
                    notify('', 'Sent to qBittorrent', 'success', '');
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
    if ($('#query').val()) $('#searchform').submit();
});

