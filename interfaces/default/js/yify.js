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

function loadMovie(id) {
    var sendData = {
        yifyid: id
    };
    $.ajax({
        url: WEBDIR + "yify/GetMovie",
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            $('#modal_dialog .modal-h3').html(data.head);
            $('#modal_dialog .modal-body').html(data.body);
            $('#modal_dialog .modal-footer').html(data.foot);

            $('#modal_dialog').modal({
                show: true,
                backdrop: false
            });

            $('.modal-fanart').css({
                'background-image': 'url(' + WEBDIR + 'manager/GetThumb?w=950&h=450&o=10&thumb=' + data.fanart + ')'
            });

            $('#download').click(function () {
                var sendData = {
                    link: $(this).attr('yify_link')
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

            $('#youtube').click(function (e) {
                var src = 'http://www.youtube.com/embed/' + $(this).attr('ytid') + '?rel=0&autoplay=1';
                var youtube = $('<iframe allowfullscreen>').attr('src', src).addClass('modal-youtube');
                $('#modal_dialog .modal-body').html(youtube);
            });
        }
    });
}

function search(set, keywords, quality, genre, rating, sort, order, append) {
    $('.spinner').show();
    var sendData = {
        set: set,
        keywords: keywords,
        quality: quality,
        genre: genre,
        rating: rating,
        sort: sort,
        order: order
    };
    $.ajax({
        url: WEBDIR + 'yify/search',
        type: 'get',
        data: sendData,
        dataType: 'text',
        timeout: 60000,
        success: function (data) {
            if (!append) {
                document.getElementById("yify-grid").innerHTML = "";
            }
            if (data === null) return errorHandler();
            $('#yify-grid').append(data);
            $('.spinner').hide();
        },
        complete: function () {
            $('.yify').click(function (e) {
                e.preventDefault();
                loadMovie($(this).prop('id'));
            });
        }
    });
}

var set = 1;

$(document).ready(function () {
    //$('.spinner').show();
    search(set, $('#keywords').val(), $('#quality').val(), $('#genre').val(), $('#rating').val(), $('#sort').val(), $('#order').val(), 0);
    //$('.spinner').hide();
    $('#searchform').submit(function () {
        //e.preventDefault();
        set = 1;
        search(set, $('#keywords').val(), $('#quality').val(), $('#genre').val(), $('#rating').val(), $('#sort').val(), $('#order').val(), 0);
        return false;
    });
    // Load more titles on scroll
    $(window).scroll(function () {
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 10) {
            set += 1;
            $('.spinner').show();
            search(set, $('#keywords').val(), $('#quality').val(), $('#genre').val(), $('#rating').val(), $('#sort').val(), $('#order').val(), 1);
        }
            $('.spinner').hide();
    });
    loadClients();
    // Client change. send command, reload options.
    $('#defclient').change(function () {
        sendData = {
            client: $("#defclient option:selected").text()
        };
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
