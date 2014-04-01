
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
    $.ajax({
        url: WEBDIR + 'newznab/search?q=' + query + '&cat=' + catid,
        type: 'get',
        dataType: 'text',
        beforeSend: function () {
            $('#results_table_body').empty();
            $('.spinner').show();
        },
        success: function (data) {
            $('.spinner').hide();
            if (data === null) return;
            $('#results_table_body').append(data);
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
});

