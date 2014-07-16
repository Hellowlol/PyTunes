function loadClients() {
    $.ajax({
        url: WEBDIR + 'newznab/GetClients',
        type: 'get',
        dataType: 'text',
        success: function (data) {
            if (data === null) return errorHandler();
            $('#default_nzb_id').append(data);
        }
    });
}


function getCategories() {
    $.ajax({
        url: WEBDIR + 'newznab/getcategories',
        type: 'get',
        dataType: 'text',
        beforeSend: function () {
            $('.spinner').show();
        },
        success: function (data) {
            $('.spinner').hide();
            if (data === null) return false;
            var select = $('#catid').html('');
            select.append($('<option>').html('Everything').attr('value', '-1'));
            select.append(data);
        }
    });
}


function search(query, catid) {
    if (query === undefined) return;
    var sendData = {
        q: query,
        cat: catid
    };
    $.ajax({
        url: WEBDIR + 'newznab/search',
        type: 'get',
        dataType: 'text',
        data: sendData,
        beforeSend: function () {
            $('#results_table_body').empty();
            $('.spinner').show();
        },
        success: function (data) {
            $('.spinner').hide();
            if (data === null) return;
            $('#results_table_body').append(data);
            $('a.ajax-link').click(function (e) {
                e.preventDefault();
                var link = $(this);
                 $.getJSON(link.attr('href'), function () {
                    notify('', 'Sent to Sabnzbd+  Category: ' + link.attr('cat'), 'success');
                });
            });
        }
    });
}


$(document).ready(function () {
    $('#searchform').submit(function () {
        search($('#query').val(), $('#catid').val());
        return false;
    });

    if ($('#query').val()) $('#searchform').submit();
    getCategories();
    // Load serverlist and send command on change.

    var servers = $('#servers').change(function () {
        $.get(WEBDIR + 'settings/changenewzserver?id=' + $(this).val(), function (data) {
            notify('XBMC', 'Server change ' + data, 'info');
        });
    });

    $.get(WEBDIR + 'settings/getnewzserver', function (data) {
        if (data === null) return;
        $.each(data.servers, function (i, item) {
            server = $('<option>').text(item.name).val(item.id);
            if (item.name == data.current) server.attr('selected', 'selected');
            servers.append(server);
        });
    }, 'json');
});

