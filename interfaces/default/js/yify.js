function loadNewest() {
    //alert("In Newest" + page);
    $.ajax({
        url: WEBDIR + "yify/newest",
        type: 'get',
        dataType: 'text',
        success: function (data) {
            //alert("Newest: " page_counts.popular);
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
                //'background-image': 'url(' + WEBDIR + 'manager/GetThumb?w=950&h=450&o=10&thumb=' + encodeURIComponent(data.fanart) + ')'
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
                //e.preventDefault();
                var src = 'http://www.youtube.com/embed/' + $(this).attr('ytid') + '?rel=0&autoplay=1';
                var youtube = $('<iframe allowfullscreen>').attr('src', src).addClass('modal-youtube');
                //alert($(this).prop('ytid'));
                $('#modal_dialog .modal-body').html(youtube);
            });
        }
    });
}
 

$(document).ready(function () {
    $('.spinner').show();
    loadNewest();
    $('.spinner').hide();
});

