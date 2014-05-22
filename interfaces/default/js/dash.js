$(document).ready(function () {
    loadRecentMovies();
    loadRecentTVshows();
    loadRecentAlbums();
    loadDownloadHistory();
    loadNZBGetDownloadHistory();
    loadWantedMovies();
    loadNextAired();
    loadPopular();
    loadPopularTV();
    loadYify();
    loadStats();
    loadTopRatedTV();
    loadTopRated();
    loadInTheaters();
    loadUpcomingMovies();
});

function loadStats() {
    if (!$('#stats-table').length) return;
    $.ajax({
        'url': WEBDIR + 'stats/Dash',
        type: 'get',
            'dataType': 'json',
            'success': function (data) {
            //alert("Stats: " + data['bar']);
            if (data === null) return;
            $('#stats-table').append(data['bar']);
            $('#stats-table').show();
        }
    });
}

function loadYify() {
    if (!$('#yify-carousel').length) return;
    $.ajax({
        'url': WEBDIR + 'yify/Carousel',
        type: 'get',
            'dataType': 'html',
            'success': function (data) {
            //alert("Yify: " + data);
            if (data === null) return;
            $('#yify-carousel-inner').append(data);
            $('#yify-carousel').show();
        }
    });
}

function loadTopRated() {
    if (!$('#toprated-carousel').length) return;
    $.ajax({
        'url': WEBDIR + 'manager/Carousel?carousel=toprated&page=1',
        type: 'get',
            'dataType': 'html',
            'success': function (data) {
            //alert("Toprated: " + data);
            if (data === null) return;
            $('#toprated-carousel .carousel-inner').append(data);
            $('#toprated-carousel').show();
        }
    });
}

function loadTopRatedTV() {
    if (!$('#topratedtv-carousel').length) return;
    $.ajax({
        'url': WEBDIR + 'manager/Carousel?carousel=topratedtv&page=1',
        type: 'get',
            'dataType': 'html',
            'success': function (data) {
            //alert("TopratedTV: " + data);
            if (data === null) return;
            $('#topratedtv-carousel .carousel-inner').append(data);
            $('#topratedtv-carousel').show();
        }
    });
}

function loadInTheaters() {
    if (!$('#theaters-carousel').length) return;
    $.ajax({
        'url': WEBDIR + 'manager/Carousel?carousel=theaters&page=1',
        type: 'get',
            'dataType': 'html',
            'success': function (data) {
            //alert("Theaters: " + data);
            if (data === null) return;
            $('#theaters-carousel .carousel-inner').append(data);
            $('#theaters-carousel').show();
        }
    });
}

function loadUpcomingMovies() {
    if (!$('#upcoming-carousel').length) return;
    $.ajax({
        'url': WEBDIR + 'manager/Carousel?carousel=upcoming&page=1',
        type: 'get',
            'dataType': 'html',
            'success': function (data) {
            //alert("Upcoming: " + data);
            if (data === null) return;
            $('#upcoming-carousel .carousel-inner').append(data);
            $('#upcoming-carousel').show();
        }
    });
}

function loadPopular() {
    if (!$('#popular-carousel').length) return;
    $.ajax({
        'url': WEBDIR + 'manager/Carousel?carousel=popular&page=1',
        type: 'get',
            'dataType': 'html',
            'success': function (data) {
            //alert("Popular: " + data);
            if (data === null) return;
            $('#popular-carousel .carousel-inner').append(data);
            $('#popular-carousel').show();
        }
    });
}

function loadPopularTV() {
    if (!$('#populartv-carousel').length) return;
    $.ajax({
        'url': WEBDIR + 'manager/Carousel?carousel=populartv&page=1',
        type: 'get',
            'dataType': 'html',
            'success': function (data) {
            //alert("PopularTV: " + data);
            if (data === null) return;
            $('#populartv-carousel .carousel-inner').append(data);
            $('#populartv-carousel').show();
        }
    });
}

function loadRecentMovies() {
    if (!$('#movie-carousel').length) return;
    $.getJSON(WEBDIR + 'xbmc/GetRecentMovies', function (data) {
        if (data === null || data.movies === null) return;
        $.each(data.movies, function (i, movie) {
            var itemDiv = $('<div>').addClass('item carousel-item');

            if (i === 0) itemDiv.addClass('active');

            var src = WEBDIR + 'xbmc/GetThumb?h=240&w=430&thumb=' + encodeURIComponent(movie.fanart);
            itemDiv.attr('style', 'background-image: url("' + src + '")');

            itemDiv.append($('<div>').addClass('carousel-caption').click(function () {
                location.href = 'xbmc/#movies';
            }).hover(function () {
                var text = $(this).children('p').stop().slideToggle();
            }).append(
            $('<h4>').html(movie.title + ' (' + movie.year + ')'),
            $('<p>').html(
                '<b>Runtime</b>: ' + parseSec(movie.runtime) + '<br />' +
                '<b>Genre</b>: ' + movie.genre.join(', ') + '<br />' + movie.plot).hide()));
            $('#movie-carousel .carousel-inner').append(itemDiv);
        });
        $('#movie-carousel').show();
    });
}

function loadRecentTVshows() {
    if (!$('#tvshow-carousel').length) return;
    $.getJSON(WEBDIR + 'xbmc/GetRecentShows', function (data) {
        if (data === null) return;
        $.each(data.episodes, function (i, episode) {
            var itemDiv = $('<div>').addClass('item carousel-item');

            if (i === 0) itemDiv.addClass('active');

            var src = WEBDIR + "xbmc/GetThumb?h=240&w=430&thumb=" + encodeURIComponent(episode.fanart);
            itemDiv.attr('style', 'background-image: url("' + src + '")');

            itemDiv.append($('<div>').addClass('carousel-caption').click(function () {
                location.href = 'xbmc/#shows';
            }).hover(function () {
                var text = $(this).children('p').stop().slideToggle();
            }).append(
            $('<h4>').html(episode.showtitle + ': ' + episode.label),
            $('<p>').html(
                '<b>Runtime</b>: ' + parseSec(episode.runtime) + '<br />' + episode.plot).hide()));
            $('#tvshow-carousel .carousel-inner').append(itemDiv);
        });
        $('#tvshow-carousel').show();
    });
}

function loadRecentAlbums() {
    if (!$('#albums-content').length) return;
    $.getJSON(WEBDIR + 'xbmc/GetRecentAlbums/4', function (data) {
        if (data === null) return;
        $.each(data.albums, function (i, album) {
            var imageSrc = WEBDIR + 'js/libs/holder.js/45x45/text:No cover';
            if (album.thumbnail !== '') {
                imageSrc = WEBDIR + 'xbmc/GetThumb?h=45&w=45&thumb=' + encodeURIComponent(album.thumbnail);
            }

            var label = album.label;
            if (album.year !== '0') label += ' (' + album.year + ')';

            $('#albums-content').append(
            $('<li>').addClass('media').append(
            $('<img>').addClass('media-object pull-left img-rounded').attr('src', imageSrc),
            $('<div>').addClass('media-body').append(
            $('<h5>').addClass('media-heading').html(label),
            $('<p>').text(album.artist[0]))).click(function (e) {
                location.href = 'xbmc/#albums';
            }));
        });
        Holder.run();
        $('#albums-content').parent().show();
    });
}

function loadDownloadHistory() {
    if (!$('#downloads_table_body').length) return;
    $.getJSON(WEBDIR + 'sabnzbd/GetHistory?limit=5', function (data) {
        $.each(data.history.slots, function (i, slot) {
            var status = $('<i>').addClass('icon-ok');
            if (slot.status == 'Failed') {
                status.removeClass().addClass('icon-remove').attr('title', slot.fail_message);
            }
            $('#downloads_table_body').append(
            $('<tr>').append(
            $('<td>').html(slot.name).attr('title', slot.name),
            $('<td>').html(status)));
        });
    });
}

function loadNZBGetDownloadHistory() {
    if (!$('#nzbgetdownloads_table_body').length) return;
    $.getJSON(WEBDIR + 'nzbget/GetHistory?limit=5', function (data) {
        $.each(data.result, function (i, slot) {
            var status = $('<i>').addClass('icon-ok');
            if (slot.ParStatus == 'Failed') {
                status.removeClass().addClass('icon-remove').attr('title', slot.fail_message);
            }
            $('#nzbgetdownloads_table_body').append(
            $('<tr>').append(
            $('<td>').html(slot.Name).attr('title', slot.Name),
            $('<td>').html(status)));
        });
    });
}

function loadWantedMovies() {
    if (!$('#wantedmovies_table_body').length) return;
    $.getJSON(WEBDIR + 'couchpotato/GetMovieList?limit=5', function (result) {
        if (result === null) {
            $('#wantedmovies_table_body').append(
            $('<tr>').append($('<td>').html('No wanted movies found').attr('colspan', '2')));
            return;
        }
        $.each(result.movies, function (i, item) {
            $('#wantedmovies_table_body').append(
            $('<tr>').append(
            $('<td>').html(item.library.info.original_title),
            $('<td>').addClass('alignright').html(item.library.year)));
        });
    });
}

function loadNextAired(options) {
    if (!$('#nextaired_table_body').length) return;

    $.getJSON(WEBDIR + 'sickbeard/GetNextAired', function (result) {
        if (result === null || result.data.soon.legth === 0) {
            $('#nextaired_table_body').append(
            $('<tr>').append($('<td>').html('No future episodes found')));
            return;
        }
        var soonaired = result.data.soon;
        var todayaired = result.data.today;
        var nextaired = todayaired.concat(soonaired);
        $.each(nextaired, function (i, tvshow) {
            if (i >= 5) return;
            var name = $('<a>').attr('href', 'sickbeard/view/' + tvshow.tvdbid).html(tvshow.show_name);
            $('#nextaired_table_body').append(
            $('<tr>').append(
            $('<td>').append(name),
            $('<td>').html(tvshow.ep_name),
            $('<td>').html(tvshow.airdate)));
        });
    });
}