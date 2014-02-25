$(document).ready(function () {
    $('.spinner').show();
    var artistid = $('div.page-title').attr('data-artist-id');
    loadArtist(artistid);
    loadAlbums(artistid);
    //$('#banner').css('background-image', 'url(' + WEBDIR + 'xbmc/GetImage/' + showid + ')');
});

function loadArtist(artistid) {
    $.ajax({
        url: WEBDIR + 'xbmc/GetArtist?artist_id=' + artistid,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            //if (data.result != 'success') {
            //    notify('Error', 'Artist not found: ' + artistid, 'error');
            //    return;
            //}
//elem.html('<li>loadArtist</li>');
            artistdata = data.artistdetails;
            //$('.xbmc_albums').append(xbmcStatusLabel(artistdata.status));
            if (artistdata.formed) {
                $('.xbmc_formed').html(artistdata.formed);
            }
            else {
                $('.xbmc_formed').html('N/A');
            }
            if (artistdata.musicbrainzid) {
                $('.xbmc_mbid').html(artistdata.musicbrainzid);
            }
            else {
                $('.xbmc_mbid').html('N/A');
            }
            if (artistdata.description) {
                $('.description').html(shortenText(artistdata.description, 1000));
            }
            else {
                $('.description').html('No Description');
            }
            if (artistdata.born) {
                $('.xbmc_born').html(artistdata.born);
            }
            else {
                $('.xbmc_born').html('N/A');
            }
            if (artistdata.died) {
                $('.xbmc_died').html(artistdata.died);
            }
            else {
                $('.xbmc_died').html('N/A');
            }
            if (artistdata.disbanded) {
                $('.xbmc_disbanded').html(artistdata.disbanded);
            }
            else {
                $('.xbmc_disbanded').html('N/A');
            }
            if (artistdata.yearsactive) {
                $('.xbmc_yearsactive').html(artistdata.yearsactive);
            }
            else {
                $('.xbmc_yearsactive').html('N/A');
            }
            //$('.xbmc_yearsactive').text(artistdata.yearsactive);
            //$('.xbmc_mbid').text(artistdata.musicbrainzid);
            if (artistdata.thumbnail !== '') {
                thumbsrc = WEBDIR + 'xbmc/GetThumb?w=256&h=256&thumb=' + encodeURIComponent(artistdata.thumbnail);
            }
            if (artistdata.fanart !== '') {
                fansrc = WEBDIR + 'xbmc/GetThumb?w=1000&h=500&o=20&thumb=' + encodeURIComponent(artistdata.fanart);
            }
            document.images["thumb"].src = thumbsrc;
            //$('.thumb').html($('<img>').attr('src', thumbsrc).addClass('thumbnail'));
            $('.thumb').html($('<img>').attr('src', thumbsrc).addClass('thumbnail'));
            //movieAnchor.append($('<h6>').addClass('title').html(shortenText(movie.title, 12)));
            $('#fanart').css('background-image', 'url(' + fansrc + ')');

            if (artistdata.mood) {
                $('.xbmc_mood').html(shortenText(artistdata.mood.join(', '), 80));
            }
            else {
                $('.xbmc_mood').html('N/A');
            }
            if (artistdata.style) {
                $('.xbmc_style').html(shortenText(artistdata.style.join(', '), 80));
            }
            else {
                $('.xbmc_style').html('N/A');
            }
            if (artistdata.instrument) {
                $('.xbmc_instrument').html(artistdata.instrument.join(', '));
            }
            else {
                $('.xbmc_instrument').html('N/A');
            }
        },
        error: function () {
            notify('Error', 'Error while loading artist.', 'error');
        }
    });
}

function loadAlbums(artistid) {
    $('.spinner').show();
    var elem = $('#album-grid');
    //var albums = '';
    $.ajax({
        url: WEBDIR + 'xbmc/GetAlbums?artistid=' + artistid,
        type: 'get',
        //data: sendData,
        dataType: 'json',
        success: function (data) {
            //$('.artist-albums').html('TEST');
            //if (data === null) return errorHandler();
            //if (data.albums !== undefined) {
                $.each(data.albums, function (i, album) {
                    var albumItem = $('<li>').hover(function () {
                        $(this).children('div').fadeToggle();
                    });

                    var src = 'holder.js/150x150/text:No artwork';
                    if (album.thumbnail !== '') {
                        src = WEBDIR + 'xbmc/GetThumb?w=150&h=150&thumb=' + encodeURIComponent(album.thumbnail);
                    }
                    albumItem.append($('<img>').attr('src', src).addClass('thumbnail'));

                    var albumCaption = $('<div>').addClass('grid-caption hide').append(
                    $('<a>').attr('href', '#').append(
                    $('<h6>').html(album.title),
                    $('<h6>').html(album.artist).addClass('artist')).click(function (e) {
                        e.preventDefault();
                        loadAlbum({
                            'albumid': album.albumid,
                            'search': album.title
                        });
                    }),
                    $('<div>').addClass('grid-control').append(
                    $('<a>').attr('href', '#').append(
                    $('<img>').attr('src', WEBDIR + '../../img/play.png').attr('title', 'Play')).click(function (e) {
                        e.preventDefault();
                        playItem(album.albumid, 'album');
                    }),
                    $('<a>').attr('href', '#').append(
                    $('<img>').attr('src', WEBDIR + '../../img/add.png').attr('title', 'Queue')).click(function (e) {
                        e.preventDefault();
                        xbmc/queueItem(album.albumid, 'album');
                        notify('Added', 'Album has been added to the playlist.', 'info');
                    })));
                    albumItem.append(albumCaption);
                    elem.append(albumItem);
                    //albums = albums + albumItem;
                });
            //}
            Holder.run();
        },
        complete: function () {
            //$('.artist-albums').append(albums);
            $('.spinner').hide();
        }
    });
    return elem;
}

