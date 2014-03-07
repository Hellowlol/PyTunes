function show_data() {
    $.getJSON(WEBDIR + "manager/GetData", function (response) {
        alert(response);
        $("#data").html('response');
    });
}

var movieLoad = {
    last: 0,
    request: null,
    limit: 50,
    options: null
};


function loadMovies(options) {
    var optionstr = JSON.stringify(options) + hideWatched + JSON.stringify(sorting);
    if (movieLoad.options != optionstr) {
        movieLoad.last = 0;
        $('#movie-grid').empty();
    }
    movieLoad.options = optionstr;

    var active = (movieLoad.request !== null && movieLoad.request.readyState !== 4);
    if (active || movieLoad.last == -1) return;

    var sendData = {
        start: movieLoad.last,
        end: (movieLoad.last + movieLoad.limit),
        hidewatched: hideWatched,
        sortmethod: sorting.method,
        sortorder: sorting.order
    };
    $.extend(sendData, options);

    $('.spinner').show();
    movieLoad.request = $.ajax({
        url: WEBDIR + 'manager/GetMovies',
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            if (data === null) return errorHandler();

            if (data.limits.end == data.limits.total) {
                movieLoad.last = -1;
            } else {
                movieLoad.last += movieLoad.limit;
            }

            if (data.movies !== undefined) {
                $.each(data.movies, function (i, movie) {
                    var movieItem = $('<li>').attr('title', movie.title);

                    var movieAnchor = $('<a>').attr('href', '#').click(function (e) {
                        e.preventDefault();
                        loadMovie(movie);
                    });

                    var src = 'holder.js/100x150/text:No artwork';
                    if (movie.thumbnail !== '') {
                        src = WEBDIR + 'xbmc/GetThumb?w=100&h=150&thumb=' + encodeURIComponent(movie.thumbnail);
                    }
                    movieAnchor.append($('<img>').attr('src', src).addClass('thumbnail'));

                    if (movie.playcount >= 1) {
                        movieAnchor.append($('<i>').attr('title', 'Watched').addClass('icon-white icon-ok-sign watched'));
                    }

                    movieAnchor.append($('<h6>').addClass('title').html(shortenText(movie.title, 12)));

                    movieItem.append(movieAnchor);

                    $('#movie-grid').append(movieItem);
                });
            }
            Holder.run();
        },
        complete: function () {
            $('.spinner').hide();
        }
    });
}


function reloadTab() {
    options = {
        'filter': searchString
    };

    //if ($('#movies').is(':visible')) {
    //    loadMovies(options);
    //} 
    //else if ($('#shows').is(':visible')) {
    //    loadShows(options);
    //} 
    //else if ($('#episodes').is(':visible')) {
    //    options = $.extend(options, {
    //        'tvshowid': currentShow
    //   });
    //    loadEpisodes(options);
    //} 
    //else if ($('#artists').is(':visible')) {
    //    loadArtists(options);
    //} 
    //else if ($('#albums').is(':visible')) {
    //    loadAlbums(options);
    //} 
    //else if ($('#songs').is(':visible')) {
    //    loadSongs();
    //} 
    //else if ($('#pvr').is(':visible')) {
    //    loadChannels();
    //}
}
$(document).ready(function () {
    $('.spinner').show();
    show_data();
    $('.spinner').hide();
});

