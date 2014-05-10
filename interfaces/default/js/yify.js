
function loadMovie(id) {
    //alert('load movie ' + id);
    var sendData = {
        yifyid: id
    };
    $.ajax({
        url: WEBDIR + "yify/GetMovie",
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            //alert('webdir' + WEBDIR);
            //alert(data);
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
            $('#download').click(function (e) {
                var sendData = {
                    hash: $(this).attr('yify_link'),
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

            $('#youtube').click(function (e) {
                var src = 'http://www.youtube.com/embed/' + $(this).attr('ytid') + '?rel=0&autoplay=1';
                var youtube = $('<iframe allowfullscreen>').attr('src', src).addClass('modal-youtube');
                //alert($(this).prop('ytid'));
                $('#modal_dialog .modal-body').html(youtube);
            });
        }
    });
}

function search(set, keywords, quality, genre, rating, sort, append) {
    //alert('search ' + keywords);
    var sendData = {
        set: set,
        keywords: keywords,
        quality: quality,
        genre: genre,
        rating: rating,
        sort: sort
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
            //for some reason the .empty method didn't work
            //$('#yify-grid').empty;
            $('.spinner').show();
            //alert('search ' + data);
            if (data === null) return errorHandler();
            $('#yify-grid').append(data);
        },
        complete: function () {
            $('.yify').click(function(e){
                e.preventDefault();
                //alert('click');
                loadMovie($(this).prop('id'));
            });
            $('.spinner').hide();
        }
    });
} 

var set = 1;

$(document).ready(function () {
    $('.spinner').show();
    search(set, $('#keywords').val(), $('#quality').val(), $('#genre').val(), $('#rating').val(), $('#sort').val(), 0);
    $('.spinner').hide();
    $('#searchform').submit(function (e) {
        //e.preventDefault();
        //alert('search  submit' );
        search(set, $('#keywords').val(), $('#quality').val(), $('#genre').val(), $('#rating').val(), $('#sort').val(), 0);
        return false;
    });
    // Load more titles on scroll
    $(window).scroll(function () {
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 10) {
            set += 1;
            search(set, $('#keywords').val(), $('#quality').val(), $('#genre').val(), $('#rating').val(), $('#sort').val(), 1);
        }
    });

});

