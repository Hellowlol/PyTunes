
function getCategories() {
    $.ajax({
        url: WEBDIR + 'torrents/getcategories',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            if (data === null) return false;

            var select = $('#catid').html('');
            select.append($('<option>').html('Everything').attr('value', '-1'));
            $.each(data.category, function (c, cat) {
                var option = $('<option>').html(cat["@attributes.name"]);
                option.attr('value', cat["@attributes.id"]);
                select.append(option);
                $.each(cat.subcat, function (s, sub) {
                    if (sub["@attributes"] === undefined) sub = cat.subcat;
                    var name = cat["@attributes.name"] + '-' + sub["@attributes.name"];
                    var option = $('<option>').html('&nbsp;&nbsp;' + name);
                    option.attr('value', sub["@attributes.id"]);
                    select.append(option);
                });
            });
        }
    });
}

function search(query, catid) {
    if (query === undefined) return;
    $.ajax({
        url: WEBDIR + 'torrents/search?q=' + query + '&cat=' + catid,
        type: 'get',
        dataType: 'text',
        beforeSend: function () {
            $('#results_table_body').empty();
            $('.spinner').show();
        },
        success: function (data) {
            if (data === null) return errorHandler();
            $('#results_table_body').append(data);
        },
        //timeout:120000
        complete: function () {
            $('.spinner').hide();
        }
    });
}

function showDetails(data) {
    var modalTitle = data.description;
    if (data.attr.imdbtitle) {
        modalTitle = data.attr.imdbtitle;
        if (data.attr.imdbyear) modalTitle += ' (' + data.attr.imdbyear + ')';
    } else if (data.attr.artist && data.attr.album) {
        modalTitle = data.attr.artist + ' - ' + data.attr.album;
    }

    var url = '';
    var link = '';
    var modalImage = '';
    if (data.attr.coverurl) {
        url = WEBDIR + 'newznab/thumb?url=' + data.attr.coverurl + '&w=200&h=300';
        modalImage = $('<div>').addClass('thumbnail pull-left');
        modalImage.append($('<img>').attr('src', url));
    } else if (data.attr.rageid) {
        url = WEBDIR + 'newznab/thumb?url=rageid' + data.attr.rageid + '&w=200&h=300';
        modalImage = $('<div>').addClass('thumbnail pull-left');
        modalImage.append($('<img>').attr('src', url));
    }

    var modalInfo = $('<div>').addClass('modal-movieinfo');
    if (data.attr.imdbtagline) {
        modalInfo.append($('<p>').html(data.attr.imdbtagline));
    }
    if (data.attr.genre) {
        modalInfo.append($('<p>').html('<b>Genre:</b> ' + data.attr.genre));
    }
    /*
    if(data.attr['imdbdirector']) {
        modalInfo.append($('<p>').html('<b>Director:</b> ' + data.attr['imdbdirector']));
    }
    if(data.attr['imdbactors']) {
        modalInfo.append($('<p>').html('<b>Actors:</b> ' + data.attr['imdbactors']));
    }
    */
    modalInfo.append($('<p>').html('<b>Size:</b> ' + bytesToSize(data.attr.size)));
    modalInfo.append($('<p>').html('<b>Grabs:</b> ' + data.attr.grabs));
    modalInfo.append($('<p>').html('<b>Files:</b> ' + data.attr.files));
    var password = data.attr.password;
    if (password === 0) password = 'None';
    modalInfo.append($('<p>').html('<b>Password:</b> ' + password));
    if (data.attr.imdbscore) {
        var rating = $('<span>').raty({
            readOnly: true,
            score: (data.attr.imdbscore / 2)
        });
        modalInfo.append(rating);
    }
    if (data.attr.label) {
        modalInfo.append($('<p>').html('<b>Label:</b> ' + data.attr.label));
    }
    if (data.attr.tracks) {
        modalInfo.append($('<p>').html('<b>Tracks:</b> ' + data.attr.tracks));
    }

    var modalBody = $('<div>');
    modalBody.append(modalImage);
    modalBody.append(modalInfo);

    var modalButtons = {
        'Download': function () {
            sendToSab(data.link);
            hideModal();
        }
    };
    if (data.attr.imdb) {
        link = 'http://www.imdb.com/title/tt' + data.attr.imdb + '/';
        $.extend(modalButtons, {
            'IMDb': function () {
                window.open(link, 'IMDb');
            }
        });
    }
    if (data.attr.rageid) {
        link = 'http://www.tvrage.com/shows/id-' + data.attr.rageid;
        $.extend(modalButtons, {
            'TVRage': function () {
                window.open(link, 'TVRage');
            }
        });
    }

    if (data.attr.backdropurl) {
        url = WEBDIR + 'torrents/thumb?url=' + data.attr.backdropurl + '&w=675&h=400&o=20';
        $('.modal-fanart').css({
            'background': '#ffffff url(' + url + ') top center no-repeat',
                'background-size': '100%'
        });
    }
    showModal(modalTitle, modalBody, modalButtons);
}

function sendToSab(url) {
    return $.ajax({
        url: WEBDIR + 'sabnzbd/AddNzbFromUrl',
        type: 'post',
        dataType: 'json',
        data: {
            nzb_url: url
        },
        success: function (result) {
            notify('', 'Sent to SabNZBd', 'info');
        }
    });
}

$(document).ready(function () {
    $('#searchform').submit(function () {
        search($('#query').val(), $('#catid').val());
        return false;
    });
    if ($('#query').val()) $('#searchform').submit();

    //getCategories();
});

