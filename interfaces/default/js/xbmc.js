var searchString = '';
var hideWatched = 0;
var playerLoader = null;
var position1 = null;
var sorting = {
    method: 'title',
    order: 'ascending'
};
var spacerh10 = "<img src='../img/spacer.png' class='spacer-h10'>";

$(document).ready(function () {
    playerLoader = setInterval('loadNowPlaying()', 1000);
    hideWatched = $('#hidewatched').hasClass('active') ? 1 : 0;

    // Load data on tab display
    $('a[data-toggle="tab"]').click(function (e) {
        $('#search').val('');
        searchString = '';
    }).on('shown', reloadTab);
    $(window).trigger('hashchange');

    // Catch keyboard event and send to XBMC
    $(document).keydown(function (e) {
        if (!$('input').is(":focus")) {
            arrow = {
                8: 'back',
                27: 'back',
                13: 'select',
                37: 'left',
                38: 'up',
                39: 'right',
                40: 'down',
                88: 'stop',
                32: 'playpause',
                67: 'contextmenu',
                73: 'info',
                77: 'mute'
            };
            command = arrow[e.which];
            if (command) {
                $.get(WEBDIR + 'xbmc/ControlPlayer?action=' + command);
                e.preventDefault();
            }
        }
    });

    // Load serverlist and send command on change.
    var servers = $('#servers').change(function () {
        $.get(WEBDIR + 'xbmc/changeserver?id=' + $(this).val(), function (data) {
            notify('XBMC', 'Server change ' + data, 'info');
        });
    });
    $.get(WEBDIR + 'xbmc/getserver', function (data) {
        if (data === null) return;
        $.each(data.servers, function (i, item) {
            server = $('<option>').text(item.name).val(item.id);
            if (item.name == data.current) server.attr('selected', 'selected');
            servers.append(server);
        });
    }, 'json');

    // Enable player controls
    $('[data-player-control]').click(function () {
        var action = $(this).attr('data-player-control');
        $.get(WEBDIR + 'xbmc/ControlPlayer?action=' + action);
    });
    $('#nowplaying #player-progressbar').click(function (e) {
        pos = ((e.pageX - this.offsetLeft) / $(this).width() * 100).toFixed(2);
        $.get(WEBDIR + 'xbmc/ControlPlayer?action=seek&value=' + pos);
    });

    // Toggle wether to show already seen episodes
    $('#hidewatched').click(function (e) {
        e.preventDefault();
        hideWatched = $(this).toggleClass('active').hasClass('active') ? 1 : 0;
        $(this).text(hideWatched ? ' Show Watched' : ' Hide Watched');
        $(this).prepend('<i class="icon-eye-open"></i>');
        $.get(WEBDIR + 'settings?xbmc_hide_watched=' + hideWatched);
        reloadTab();
    });

    // Define sort method
    $('[data-sort-method]').click(function (e) {
        e.preventDefault();
        sorting.method = $(this).attr('data-sort-method');
        sorting.order = $(this).attr('data-sort-order');
        $('[data-sort-method]').removeClass('active');
        $(this).addClass('active');
        reloadTab();
    });

    $('.myFilters li').click(function (e) {
        e.preventDefault();
        var v = $(this).text()[0]
        $('.myFilterItems li').hide().filter(function(){
            return $(this).text().toUpperCase()[0] == v;
         }).show()
     });

    // Send notification to XBMC
    $('#xbmc-notify').click(function () {
        msg = prompt("Message");
        if (msg) {
            $.post(WEBDIR + 'xbmc/Notify', {
                'text': msg
            }, function (data) {
                notify('XBMC', 'Notification sent successfully', 'info');
            });
        }
    });

    // Show subtitle selector if current has a subtitle track
    var subtitles = $('#subtitles').change(function () {
        $.get(WEBDIR + 'xbmc/Subtitles?subtitle=' + $(this).val(), function (data) {
            notify('Subtitles', 'Change successful', 'info');
        });
    });
    // Show audio selector if current has multiple subtitles tracks
    var audio = $('#audio').change(function () {
        $.get(WEBDIR + 'xbmc/Audio?audio=' + $(this).val(), function (data) {
            notify('Audio', 'Change successful', 'info');
        });
    });

    // Make the playlist sortable
    $('#playlist-table tbody').sortable({
        handle: ".handle",
        containment: "parent",
        start: function (event, ui) {
            clearInterval(playerLoader);
            position1 = ui.item.index();
        },
        stop: function (event, ui) {
            $.get(WEBDIR + 'xbmc/PlaylistMove', {
                position1: position1,
                position2: ui.item.index()
            }, function (data) {
                nowPlayingId = null;
                playerLoader = setInterval('loadNowPlaying()', 1000);
            });
        }
    });

    // Filter on searchfield changes
    $("#search").on('input', function (e) {
        searchString = $(this).val();
        reloadTab();
    });

    // Load more titles on scroll
    $(window).scroll(function () {
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 10) {
            reloadTab();
        }
    });
});

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
        url: WEBDIR + 'xbmc/GetMovies',
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

function loadMovie(movie) {
    var poster = WEBDIR + 'xbmc/GetThumb?w=133&h=200&thumb=' + encodeURIComponent(movie.thumbnail);
    var info = $('<div>').addClass('modal-movieinfo');
    var footerbuttons = $('<div>').addClass('modal-footerbuttons');
    var actors = "";
    var castshow = $('<ul>').addClass('thumbnails');
    var actorItem = "";    
    var actors = [];
    var director = "";
    var writers = "";
    var genre = "";
    var path = "";
    var country = "";
    var studio = "";
    var runtime = "";
	var rating = "";
    var moviethumb = "";
    var mpaaicon = "";
    var resolutionicon = "";
    var sourceicon = "";
    var aspecticon = "";
    var videocodec ="";
    var plot = movie.plot;
    var actorthumb = "";
    if (movie.mpaa) {
        mpaaicon = "<img src='../img/media/usmpaa/" + movie.mpaa + ".png' class='modal-codec'>";
    }
            if (movie.cast) {
                $.each(movie.cast, function (i, castmember) {
                    var castItem = $('<li>').attr('title', castmember.name + ' --> ' + castmember.role);

                    var castAnchor = $('<a>').attr('href', '#').click(function (e) {
                        e.preventDefault();
                        loadCast(castmember.name);
                    });

                    var src = 'holder.js/83x125/text:No artwork';
                    if (castmember.thumbnail !== '') {
                        src = WEBDIR + 'xbmc/GetThumb?w=83&h=125&thumb=' + encodeURIComponent(castmember.thumbnail);
                    }
                    castAnchor.append($('<img>').attr('src', src).addClass('thumbnail actor-thumb'));

                    castAnchor.append($('<h6>').addClass('title').html(shortenText(castmember.name, 11)));

                    castAnchor.append($('<h6>').addClass('title').html(shortenText(castmember.role, 11)));

                    castItem.append(castAnchor);

                    castshow.append(castItem);

                    Holder.run();
                });
            }
    if (movie.director) {
        director = movie.director.join(', ');
    }
    if (movie.writer) {
        writer = movie.writer.join(', ');
    }
    if (movie.genre) {
        genre = movie.genre.join(', ');
    }
    if (movie.country) {
        country = movie.country.join(', ');
    }
    if (movie.studio) {
        studio = movie.studio.join(', ');
    }
    if (movie.streamdetails && movie.streamdetails.video[0]) {
        runtime = parseSec(movie.streamdetails.video[0].duration);
        var height = movie.streamdetails.video[0].height;
        var width = movie.streamdetails.video[0].width;
        if ((width == '1920') || (height == '1080')) {
            resolutionicon = "<img src='../img/media/resolution/white_400x200/1080.png' class='modal-resolution'>";
            sourceicon = "<img src='../img/media/videocodec/white_400x200/bluray.png' class='modal-source'>";
        } else if ((width == '1280') || (height == '720')) {
                resolutionicon = "<img src='../img/media/resolution/white_400x200/720.png' class='modal-resolution'>";
                sourceicon = "<img src='../img/media/videocodec/white_400x200/bluray.png' class='modal-source'>";
        } else {
                resolutionicon = "<img src='../img/media/resolution/white_400x200/480.png' class='modal-resolution'>";
                sourceicon = "<img src='../img/media/videocodec/white_400x200/dvd.png' class='modal-source'>";
        }
        var aspect = Math.round(movie.streamdetails.video[0].aspect*100)/100;
        if ((aspect > 1.82) && (aspect < 1.88)) {
            aspecticon = "<img src='../img/media/aspectratio/white_400x200/1.85.png' class='modal-aspect'>";
         }
        if ((aspect > 1.28) && (aspect < 1.36)) {
            aspecticon = "<img src='../img/media/aspectratio/white_400x200/1.33.png' class='modal-aspect'>";
        }
        if ((aspect > 1.62) && (aspect < 1.70)) {
            aspecticon = "<img src='../img/media/aspectratio/white_400x200/1.66.png' class='modal-aspect'>";
        }
        if ((aspect > 1.74) && (aspect < 1.82)) {
            aspecticon = "<img src='../img/media/aspectratio/white_400x200/1.78.png' class='modal-aspect'>";
        }
        if ((aspect > 2.14) && (aspect < 2.26)) {
            aspecticon = "<img src='../img/media/aspectratio/white_400x200/2.20.png' class='modal-aspect'>";
        }
        if ((aspect > 2.30) && (aspect < 2.45)) {
            aspecticon = "<img src='../img/media/aspectratio/white_400x200/2.35.png' class='modal-aspect'>";
        }
        var codec = movie.streamdetails.video[0].codec;
        videocodec = "<img src='../img/media/videocodec/white_400x200/" + codec + ".png' class='modal-codec'>";
    }
    if (movie.rating) {
		rating = $('<span>').raty({
        readOnly: true,
        path: WEBDIR + 'img',
        score: (movie.rating / 2)
        })
    }
    var buttons = {
        'Play': function () {
            playItem(movie.movieid, 'movie');
            hideModal();
        },
        'Cinema-X': function () {
            executeAddon('script.cinema.experience', movie.movieid);
            hideModal();
        },
        'Queue': function () {
           queueItem(movie.movieid, 'movie');
           hideModal();
        },
        'Remove': function () {
            var confirmed = confirm('Are you sure? Remove: ' + movie.title + '? This will remove this entry forever!');
            if (confirmed === true) {
                removeLibraryItem(movie.movieid, 'movie');
                reloadTab();
                hideModal();
            }
        }
     };
    if (movie.imdbnumber) {
        $.extend(buttons, {
            'IMDb': function () {
                window.open('http://www.imdb.com/title/' + movie.imdbnumber, 'IMDb');
            }
        });
    }
    if (movie.trailer) {
        $.extend(buttons, {
            'Trailer Here': function () {
                var trailerid = movie.trailer.substr(movie.trailer.length - 11);
                var src = 'http://www.youtube.com/embed/' + trailerid + '?rel=0&autoplay=1';
                var youtube = $('<iframe>').attr('src', src).addClass('modal-youtube');
                $('#modal_dialog .modal-body').html(youtube);
            }
        });
    }
    if (movie.trailer) {
        $.extend(buttons, {
            'Trailer XBMC': function () {
                var trailerid = movie.trailer.substr(movie.trailer.length - 11);
                //var url = encodeURIComponent('http://www.youtube.com/embed/' + trailerid + '?rel=0&autoplay=1');
                ExecuteAddon(addon='plugin.video.youtube', cmd0=trailerid);
            }
        });
    }
    var stars = $('<p>').attr('id', 'modal-star-rating').addClass('modal-star-rating').append(rating);
    var stream = "<span class='pull-right'>" + sourceicon + spacerh10 + resolutionicon + spacerh10  + mpaaicon + spacerh10 + aspecticon + spacerh10 + videocodec + spacerh10 +  spacerh10 + "</span>";
    plot = $('<p>').html('<b>Plot:</b> ' + plot);
    path = $('<div>').html('<b>Path:</b> ' + movie.file);
    director = $('<p>').addClass('modal-info-item').html('<b>Director:</b> ' + director);
    writer = $('<p>').addClass('modal-info-item').html('<b>Writer:</b> ' + writer);
    genre = $('<p>').addClass('modal-info-item').html('<b>Genre:</b> ' + genre);
    country = $('<p>').addClass('modal-info-item').html('<b>Country:</b> ' + country);
    studio = $('<p>').addClass('modal-info-item').html('<b>Studio:</b> ' + studio);
    runtime = $('<p>').addClass('modal-info-item').html('<b>Runtime:</b> ' + runtime);
    moviethumb = $('<img>').attr('src', poster).addClass('thumbnail modal-movie-poster');
    moviethumb = $('<p>').append(moviethumb);
    
    info.append(plot, director, writer, genre, country, studio, runtime);

    var bodymiddleleft = $('<div>').addClass('pull-left modal-body-middle-left').append(moviethumb, stars);
    var infocolumbleft = $('<div>').addClass('pull-left').append(director, genre, runtime);
    var infocolumbright = $('<div>').addClass('pull-right').append(writer, country, studio);
    var bodymiddlebottom = $('<div>').addClass('pull-left').append(path);
    var bodymiddleright = $('<div>').addClass('modal-body-middle-right').append(plot, infocolumbleft, infocolumbright, bodymiddlebottom);
    var bodymiddle = $('<div>').addClass('modal-body-middle').append(bodymiddleleft, bodymiddleright);
    var bodybottom = $('<div>').addClass('modal-body-bottom pull-left').append(castshow);
    var bodycontent = $('<div>').append(bodymiddle, bodybottom);


    var head = movie.title + ' (' + movie.year + ')' + stream;
    var body = $('<div>').append(bodycontent);
    var foot = buttons;

    showModal(head, body, foot);

    $('.modal-fanart').css({
        'background-image': 'url(' + WEBDIR + 'xbmc/GetThumb?w=950&h=450&o=10&thumb=' + encodeURIComponent(movie.fanart) + ')'
    });
}

var showLoad = {
    last: 0,
    request: null,
    limit: 50,
    options: null
};

function loadShows(options) {
    var optionstr = JSON.stringify(options) + hideWatched + JSON.stringify(sorting);
    if (showLoad.options != optionstr) {
        showLoad.last = 0;
        $('#show-grid').empty();
    }
    showLoad.options = optionstr;

    var active = (showLoad.request !== null && showLoad.request.readyState !== 4);
    if (active || showLoad.last == -1) return;

    var sendData = {
        start: showLoad.last,
        end: (showLoad.last + showLoad.limit),
        hidewatched: hideWatched,
        sortmethod: sorting.method,
        sortorder: sorting.order
    };
    $.extend(sendData, options);

    $('.spinner').show();
    showLoad.request = $.ajax({
        url: WEBDIR + 'xbmc/GetShows',
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            if (data === null) return errorHandler();

            if (data.limits.end == data.limits.total) {
                showLoad.last = -1;
            } else {
                showLoad.last += showLoad.limit;
            }

            if (data.tvshows !== undefined) {
                $.each(data.tvshows, function (i, show) {
                    var showItem = $('<li>').attr('title', show.title);

                    var showAnchor = $('<a>').attr('href', '#').click(function (e) {
                        e.preventDefault();
                        loadEpisodes({
                            'tvshowid': show.tvshowid
                        });
                    });

                    var src = 'holder.js/100x150/text:No artwork';
                    if (show.thumbnail !== '') {
                        src = WEBDIR + 'xbmc/GetThumb?w=100&h=150&thumb=' + encodeURIComponent(show.thumbnail);
                    }
                    showAnchor.append($('<img>').attr('src', src).addClass('thumbnail'));

                    if (show.playcount >= 1) {
                        showAnchor.append($('<i>').attr('title', 'Watched').addClass('icon-white icon-ok-sign watched'));
                    }

                    showAnchor.append($('<h6>').addClass('title').html(shortenText(show.title, 11)));

                    showItem.append(showAnchor);

                    $('#show-grid').append(showItem);
                });
            }
            Holder.run();
        },
        complete: function () {
            $('.spinner').hide();
        }
    });
}

var episodeLoad = {
    last: 0,
    request: null,
    limit: 50,
    options: null
};
var currentShow = null;

function loadEpisodes(options) {
    currentShow = options.tvshowid;
    var optionstr = JSON.stringify(options) + hideWatched;
    if (episodeLoad.options != optionstr) {
        episodeLoad.last = 0;
        $('#episode-grid').empty();
    }
    episodeLoad.options = optionstr;

    var active = (episodeLoad.request !== null && episodeLoad.request.readyState !== 4);
    if (active || episodeLoad.last == -1) return;

    var sendData = {
        start: episodeLoad.last,
        end: (episodeLoad.last + episodeLoad.limit),
        hidewatched: hideWatched
    };
    $.extend(sendData, options);

    $('.spinner').show();
    episodeLoad.request = $.ajax({
        url: WEBDIR + 'xbmc/GetEpisodes',
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            if (data === null || data.limits.total === 0) return;

            if (data.limits.end == data.limits.total) {
                episodeLoad.last = -1;
            } else {
                episodeLoad.last += episodeLoad.limit;
            }

            if (data.episodes !== undefined) {
                $.each(data.episodes, function (i, episode) {
                    var episodeItem = $('<li>').attr('title', episode.plot);

                    var episodeAnchor = $('<a>').attr('href', '#').click(function (e) {
                        e.preventDefault();
                        playItem(episode.episodeid, 'episode');
                    });

                    var src = 'holder.js/150x85/text:No artwork';
                    if (episode.thumbnail !== '') {
                        src = WEBDIR + 'xbmc/GetThumb?w=150&h=85&thumb=' + encodeURIComponent(episode.thumbnail);
                    }
                    episodeAnchor.append($('<img>').attr('src', src).addClass('thumbnail'));

                    if (episode.playcount >= 1) {
                        episodeAnchor.append($('<i>').attr('title', 'Watched').addClass('icon-white icon-ok-sign watched'));
                    }

                    episodeAnchor.append($('<h6>').addClass('title').html(shortenText(episode.label, 18)));

                    episodeItem.append(episodeAnchor);

                    $('#episode-grid').append(episodeItem);
                });
            }
            Holder.run();
        },
        complete: function () {
            $('.spinner').hide();
            $('a[href=#episodes]').tab('show');
        }
    });
    $('#episode-grid').slideDown();
}

var artistLoad = {
    last: 0,
    request: null,
    limit: 50,
    options: null
};

function loadArtists(options) {
    var optionstr = JSON.stringify(options);
    if (artistLoad.options != optionstr) {
        artistLoad.last = 0;
        $('#artist-grid').empty();
    }
    artistLoad.options = optionstr;

    var active = (artistLoad.request !== null && artistLoad.request.readyState !== 4);
    if (active || artistLoad.last == -1) return;

    var sendData = {
        start: artistLoad.last,
        end: (artistLoad.last + artistLoad.limit)
    };
    $.extend(sendData, options);

      $('.spinner').show();
    artistLoad.request = $.ajax({
        url: WEBDIR + 'xbmc/GetArtists',
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            if (data === null) return errorHandler();

            if (data.limits.end == data.limits.total) {
                artistLoad.last = -1;
            } else {
                artistLoad.last += artistLoad.limit;
            }

            if (data.artists !== undefined) {
                $.each(data.artists, function (i, artist) {
                    $('#artist-grid').append($('<tr>').append(
                    $('<td>').append(
                    $('<a>').attr('href', '#').attr('title', 'Play all').html('<i class="icon-play">').click(function (e) {
                        e.preventDefault();
                        playItem(artist.artistid, 'artist');
                    }),
                    $('<a>').attr('href', '#').attr('title', 'Enqueue all').html('<i class="icon-plus">').click(function (e) {
                        e.preventDefault();
                        queueItem(artist.artistid, 'artist');
                    })),
                    $('<td>').append($('<a>').attr('href',WEBDIR  + 'xbmc/ViewArtist?artist_id=' + artist.artistid + '&artist=' + encodeURIComponent(artist.artist)).addClass('artist-link').text(artist.artist))
                    ));
                });
            }
            Holder.run();
        },
        complete: function () {
            $('.spinner').hide();
        }
    });
}
var albumLoad = {
    last: 0,
    request: null,
    limit: 50,
    options: null,
    artist: null
};

function loadAlbums(options) {
    var elem = $('#album-grid');
    if (options && options.artistid !== undefined) {
        $('.artist-albums:visible').slideUp(300, function () {
            $(this).remove();
        });
        if (options.artistid == loadAlbums.artist) {
            loadAlbums.artist = null;
            return;
        }
        loadAlbums.artist = options.artistid;
        elem = $('<ul>').addClass('artist-albums thumbnails').hide();
    }

    var optionstr = JSON.stringify(options);
    if (albumLoad.options != optionstr) {
        albumLoad.last = 0;
        elem.empty();
    }
    albumLoad.options = optionstr;

    var active = (albumLoad.request !== null && albumLoad.request.readyState !== 4);
    if (active || albumLoad.last === -1) return;

    var sendData = {
        start: albumLoad.last,
        end: (albumLoad.last + albumLoad.limit)
    };
    $.extend(sendData, options);

    $('.spinner').show();
    albumLoad.request = $.ajax({
        url: WEBDIR + 'xbmc/GetAlbums',
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            if (data === null) return errorHandler();

            if (data.limits.end == data.limits.total) {
                albumLoad.last = -1;
            } else {
                albumLoad.last += albumLoad.limit;
            }

            if (data.albums !== undefined) {
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
                        loadSongs({
                            'albumid': album.albumid,
                            'search': album.title
                        });
                    }),
                    $('<div>').addClass('grid-control').append(
                    $('<a>').attr('href', '#').append(
                    $('<img>').attr('src', WEBDIR + 'img/play.png').attr('title', 'Play')).click(function (e) {
                        e.preventDefault();
                        playItem(album.albumid, 'album');
                    }),
                    $('<a>').attr('href', '#').append(
                    $('<img>').attr('src', WEBDIR + 'img/add.png').attr('title', 'Queue')).click(function (e) {
                        e.preventDefault();
                        queueItem(album.albumid, 'album');
                        notify('Added', 'Album has been added to the playlist.', 'info');
                    })));
                    albumItem.append(albumCaption);
                    elem.append(albumItem);
                });
            }
            Holder.run();
            elem.slideDown();
        },
        complete: function () {
            $('.spinner').hide();
        }
    });
    return elem;
}

var songsLoad = {
    last: 0,
    request: null,
    limit: 50,
    options: {},
    filter: ''
};

function loadSongs(options) {
    searchString = $('#search').val();
    if (options !== undefined || searchString !== songsLoad.filter) {
        songsLoad.last = 0;
        $('#songs-grid tbody').empty();
        if (options !== undefined) {
            songsLoad.options = options;
            if (options.search) {
                $("#search").val(options.search);
                songsLoad.filter = options.search;
            }
        } else {
            songsLoad.options = {};
            songsLoad.filter = searchString;
        }
    }

    var active = (songsLoad.request !== null && songsLoad.request.readyState !== 4);
    if (active || songsLoad.last == -1) return;

    var sendData = {
        start: songsLoad.last,
        end: (songsLoad.last + songsLoad.limit),
        filter: (options && options.search ? '' : songsLoad.filter)
    };
    $.extend(sendData, songsLoad.options);

    $('.spinner').show();
    songsLoad.request = $.ajax({
        url: WEBDIR + 'xbmc/GetSongs',
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            if (data === null || data.limits.total === 0) return;

            if (data.limits.end == data.limits.total) {
                songsLoad.last = -1;
            } else {
                songsLoad.last += songsLoad.limit;
            }
            if (data.songs !== undefined) {
                $.each(data.songs, function (i, song) {
                    var row = $('<tr>');
                    row.append(
                    $('<td>').append(
                    $('<a>').attr('href', '#').append($('<i>').addClass('icon-plus')).click(function (e) {
                        e.preventDefault();
                        queueItem(song.songid, 'song');
                    }),
                    $('<a>').attr('href', '#').text(' ' + song.label).click(function (e) {
                        e.preventDefault();
                        playItem(song.songid, 'song');
                    })),
                    $('<td>').append(
                    $('<a>').attr('href', '#').text(song.artist).click(function (e) {
                        e.preventDefault();
                        loadSongs({
                            'artistid': song.artistid[0],
                            'search': song.artist
                        });
                    })),
                    $('<td>').append(
                    $('<a>').attr('href', '#').text(song.album).click(function (e) {
                        e.preventDefault();
                        loadSongs({
                            'albumid': song.albumid,
                            'search': song.album
                        });
                    })),
                    $('<td>').append(parseSec(song.duration)));
                    $('#songs-grid tbody').append(row);
                });
            }
        },
        complete: function () {
            $('a[href=#songs]').tab('show');
            $('.spinner').hide();
        }
    });
}

var channelsLoaded = false;

function loadChannels() {
    if (channelsLoaded) return;
    var list = $('#pvr-grid').empty();
    $('.spinner').show();
    $.ajax({
        url: WEBDIR + 'xbmc/GetChannels',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            $('.spinner').hide();
            if (data === null) return errorHandler();
            $.each(data.channels, function (i, channel) {
                var item = $('<li>').attr('title', channel.label);
                var link = $('<a>').attr('href', '#').click(function (e) {
                    e.preventDefault();
                    playItem(channel.channelid, 'channel');
                });
                var src = 'holder.js/75x75/text:' + channel.label;
                if (channel.thumbnail) {
                    src = WEBDIR + 'xbmc/GetThumb?w=75&h=75&thumb=' + encodeURIComponent(channel.thumbnail);
                }
                link.append($('<img>').attr('src', src).addClass('thumbnail'));
                link.append($('<h6>').addClass('title').html(shortenText(channel.label, 21)));
                item.append(link);
                list.append(item);
            });
            channelsLoaded = true;
            Holder.run();
        },
        complete: function () {
            $('.spinner').hide();
        }
    });
}

var nowPlayingId = false;

function loadNowPlaying() {
    $.ajax({
        url: WEBDIR + 'xbmc/NowPlaying',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            if (data === null) {
                $('#nowplaying').hide();
                $('a[href=#playlist]').parent().hide();
                return;
            }
            if (nowPlayingId != data.itemInfo.item.id) {
                var nowPlayingThumb = encodeURIComponent(data.itemInfo.item.thumbnail);
                var thumbnail = $('#nowplaying .thumb img').attr('alt', data.itemInfo.item.label);
                if (nowPlayingThumb === '') {
                    thumbnail.attr('src', 'holder.js/140x140/text:No artwork');
                    thumbnail.attr('width', '140').attr('height', '140');
                    Holder.run();
                } else {
                    switch (data.itemInfo.item.type) {
                        case 'episode':
                            thumbnail.attr('src', WEBDIR + 'xbmc/GetThumb?w=150&h=75&thumb=' + nowPlayingThumb);
                            thumbnail.attr('width', '200').attr('height', '100');
                            break;
                        case 'movie':
                            thumbnail.attr('src', WEBDIR + 'xbmc/GetThumb?w=200&h=300&thumb=' + nowPlayingThumb);
                            thumbnail.attr('width', '200').attr('height', '300');
                            break;
                        case 'song':
                            thumbnail.attr('src', WEBDIR + 'xbmc/GetThumb?w=180&h=180&thumb=' + nowPlayingThumb);
                            thumbnail.attr('width', '250').attr('height', '250');
                            break;
                        default:
                            thumbnail.attr('src', WEBDIR + 'xbmc/GetThumb?w=140&h=140&thumb=' + nowPlayingThumb);
                            thumbnail.attr('width', '140').attr('height', '140');
                    }
                }
                if (data.itemInfo.item.fanart) {
                    var background = encodeURIComponent(data.itemInfo.item.fanart);
                    background = WEBDIR + 'xbmc/GetThumb?w=1150&h=640&o=10&thumb=' + background;
                    $('#nowplaying').css({
                        'background-image': 'url(' + background + ')'
                    });
                }
            }

            if (data.playerInfo.speed == 1) {
                $('#nowplaying i.icon-play').removeClass().addClass('icon-pause');
            } else {
                $('#nowplaying i.icon-pause').removeClass().addClass('icon-play');
            }
            if (data.app.muted) {
                $('#nowplaying i.icon-remove').removeClass().addClass('icon-plus');
                $('#button.mute btn-primary').removeClass().addClass('btn-danger');
            } else {
                $('#nowplaying i.icon-plus').removeClass().addClass('icon-remove');
                $('#button.mute btn-danger').removeClass().addClass('btn-primary');
            }

            var playingTime = pad(data.playerInfo.time.hours, 2) + ':' + pad(data.playerInfo.time.minutes, 2) + ':' + pad(data.playerInfo.time.seconds, 2);
            var totalTime = pad(data.playerInfo.totaltime.hours, 2) + ':' + pad(data.playerInfo.totaltime.minutes, 2) + ':' + pad(data.playerInfo.totaltime.seconds, 2);
            var itemTime = $('#nowplaying #player-item-time').html(playingTime + ' / ' + totalTime);

            var itemTitle = $('#nowplaying #player-item-title');
            var itemYear = $('#nowplaying #player-item-year');
            var itemTagline = $('#nowplaying #player-item-tagline');
            var itemPlotOutline = $('#nowplaying #player-item-plotoutline');
            var itemPlot = $('#nowplaying #player-item-plot');
            var itemRating = $('#nowplaying #player-item-rating');
            var itemDescription = $('#nowplaying #player-item-description');
            var playingTitle = '';
            var playingSubtitle = '';
            var playingTagline = '';
            var playingPlotOutline = '';
            var playingPlot = '';
            var playingRating = '';
            var playingYear = '';
            var playingDescription = '';
            if (data.itemInfo.item.type == 'episode') {
                playingTitle = data.itemInfo.item.showtitle;
                playingPlot = data.itemInfo.item.plot;
                playingYear = data.itemInfo.item.year;
                playingRating = data.itemInfo.item.rating;
                playingTagline = data.itemInfo.item.label + ' Season: ' + data.itemInfo.item.season + ' Episode: ' + data.itemInfo.item.episode;
            } else if (data.itemInfo.item.type == 'movie') {
                playingTitle = data.itemInfo.item.label;
                playingYear = data.itemInfo.item.year;
                //playingTagline = shortenText(data.itemInfo.item.tagline, 100);
                playingTagline = data.itemInfo.item.tagline;
                playingPlotOutline = data.itemInfo.item.plotoutline;
                playingPlot = data.itemInfo.item.plot;
                playingRating = data.itemInfo.item.rating;
                playingDescription = data.itemInfo.item.description;
            } else if (data.itemInfo.item.type == 'song') {
                playingTitle = data.itemInfo.item.title;
                playingSubtitle = data.itemInfo.item.artist[0] + ' (' + data.itemInfo.item.album + ')';
            } else {
                playingTitle = data.itemInfo.item.label;
            }
            itemTitle.html(playingTitle);
            itemYear.html(playingYear);
            itemTagline.html(playingTagline);
            itemPlotOutline.html(playingPlotOutline);
            itemPlot.html(playingPlot);
            itemDescription.html(playingDescription);

            var progressBar = $('#nowplaying #player-progressbar .bar');
            progressBar.css('width', data.playerInfo.percentage + '%');

            var select = $('#audio').html('');
            var current = "";
            select.parent().hide();
            if (data.playerInfo.audiostreams && data.playerInfo.audiostreams.length > 1) {
                current = data.playerInfo.currentaudiostream.index;
                $.each(data.playerInfo.audiostreams, function (i, item) {
                    var option = $('<option>').html(item.name).val(item.index);
                    if (item.index == current) option.attr('selected', 'selected');
                    select.append(option);
                });
                select.parent().show();
            }
            select = $('#subtitles').html('');
            select.parent().hide();
            if (data.playerInfo.subtitles && data.playerInfo.subtitles.length > 0) {
                data.playerInfo.subtitles.unshift({
                    'index': 'off',
                    'name': 'None'
                });
                current = data.playerInfo.currentsubtitle.index;
                if (data.playerInfo.subtitleenabled === false || current === '') current = 'off';
                $.each(data.playerInfo.subtitles, function (i, item) {
                    var name = item.name;
                    if (item.language && item.name != item.language) name += ' [' + item.language + ']';
                    var option = $('<option>').html(name).val(item.index);
                    if (item.index == current) option.attr('selected', 'selected');
                    select.append(option);
                });
                select.parent().show();
            }

            $('[data-player-control]').attr('disabled', false);

            if (nowPlayingId != data.itemInfo.item.id) {
                loadPlaylist(data.itemInfo.item.type == 'song' ? 'audio' : 'video');
                nowPlayingId = data.itemInfo.item.id;
            }
            $('#nowplaying').slideDown();
        }
    });
}

function loadPlaylist(type) {
    $.ajax({
        url: WEBDIR + 'xbmc/Playlist/' + type,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            var playlist = $('#playlist-table tbody').html('');

            if (data.items === undefined || data.limits.total === 0) {
                playlist.html('<tr><td colspan="4">Playlist is empty</td></tr>');
                return;
            }
            $('a[href=#playlist]').parent().show();

            $.each(data.items, function (i, item) {
                var listItem = $('<tr>').attr('title', item.title).click(function (e) {
                    e.preventDefault();
                    playlistJump(i);
                });

                if (item.id == nowPlayingId) {
                    listItem.addClass('info active');
                }

                if (item.type == 'song') {
                    listItem.append(
                    $('<td>').html(shortenText(item.title, 90)).prepend(
                    $('<i>').addClass('remove icon-remove').click(function (e) {
                        e.stopPropagation();
                        removeItem(i);
                        nowPlaying = null;
                    })),
                    $('<td>').html(item.artist[0]),
                    $('<td>').html(item.album),
                    $('<td>').html(parseSec(item.duration)),
                    $('<td>').append($('<i>').addClass('handle icon-align-justify')));
                } else {
                    var label = item.label + ' (' + item.year + ')';
                    if (item.episode != -1) {
                        label = item.showtitle + ': ' + item.season + 'x' + item.episode + '. ' + item.label;
                    }
                    listItem.append(
                    $('<td>').html(label).attr('colspan', '3'),
                    $('<td>').html(parseSec(item.runtime)));
                }
                playlist.append(listItem);
            });
        }
    });
}

function playItem(item, type) {
    type = typeof type !== 'undefined' ? '&type=' + type : '';
    $.get(WEBDIR + 'xbmc/PlayItem?item=' + item + type);
}

function executeAddon(addon, cmd0, cmd1) {
    confirm('Execute: ' + addon + ' with cmd0: ' + cmd0 + ' and cmd1: ' + cmd1);
    cmd0 = typeof cmd0 !== 'undefined' ? '&cmd0=' + cmd0 : '';
    cmd1 = typeof cmd1 !== 'undefined' ? '&cmd1=' + cmd1 : '';
    $.get(WEBDIR + 'xbmc/ExecuteAddon?addon=' + addon + cmd0 + cmd1);
}

function queueItem(item, type) {
    type = typeof type !== 'undefined' ? '&type=' + type : '';
    $.get(WEBDIR + 'xbmc/QueueItem?item=' + item + type);
    nowPlayingId = null;
}

function removeItem(item) {
    $.get(WEBDIR + 'xbmc/RemoveItem?item=' + item);
    nowPlayingId = null;
}

function removeLibraryItem(id, type) {
    $.get(WEBDIR + 'xbmc/LibraryRemoveItem?libraryid=' + id + '&media=' + type);
    nowPlayingId = null;
}

function playlistJump(position) {
    $.get(WEBDIR + 'xbmc/ControlPlayer/jump/' + position);
}

function errorHandler() {
    $('.spinner').hide();
    notify('Error', 'Error connecting to XBMC', 'error');
    moviesLoading = false;
    return false;
}

function substring(str, part) {
    return str.substring(0, part.length) == part;
}

function loadShowFromHash(hash) {
    options = {
        'filter': searchString
    };
    if (substring(hash, '#tvshow-')) {
        var tvShowId = hash.substring(8);
        loadEpisodes({
            'tvshowid': tvShowId
        });
    }
}

function reloadTab() {
    options = {
        'filter': searchString
    };

    if ($('#movies').is(':visible')) {
        loadMovies(options);
    } else if ($('#shows').is(':visible')) {
        loadShows(options);
    } else if ($('#episodes').is(':visible')) {
        options = $.extend(options, {
            'tvshowid': currentShow
        });
        loadEpisodes(options);
    } else if ($('#artists').is(':visible')) {
        loadArtists(options);
    } else if ($('#albums').is(':visible')) {
        loadAlbums(options);
    } else if ($('#songs').is(':visible')) {
        loadSongs();
    } else if ($('#pvr').is(':visible')) {
        loadChannels();
    }
}

