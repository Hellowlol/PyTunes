function loadServers() {
    $.ajax({
        url: WEBDIR + 'settings/GetNewzServers',
        type: 'get',
        dataType: 'text',
        success: function (data) {
            if (data === null) return errorHandler();
            $('#default_newznab_server').append(data);
        }
    });
}

//Future Use
function loadClients() {
    $.ajax({
        url: WEBDIR + 'newznab/GetNewzClients',
        type: 'get',
        dataType: 'text',
        success: function (data) {
            if (data === null) return errorHandler();
            $('#default_nzb_client').append(data);
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
            select.empty();
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
    //loadClients();
    loadServers();
    getCategories();
    $('#searchform').submit(function () {
        search($('#query').val(), $('#catid').val());
        return false;
    });

    //if ($('#query').val()) $('#searchform').submit();

    // send command on server change.
    var servers = $('#default_newznab_server').change(function () {
        $.get(WEBDIR + 'settings/changenewzserver?id=' + $(this).val(), function (data) {
            getCategories();
            notify('Newznab', 'Server change ' + data, 'info');
        });
    });


    //Future Use
    var clients = $('#default_newznab_client').change(function () {
        $.get(WEBDIR + 'settings/changenewzclient?id=' + $(this).val(), function (data) {
            notify('Newznab', 'Client change ' + data, 'info');
        });
    });

});

