
function loadInTheaters() {
    //alert("In Theaters");
    $('#theaters-grid').empty();
    $.ajax({
        url: WEBDIR + "manager/Tmdb?source=intheaters&page=2",
        type: 'get',
        dataType: 'html',
        success: function (data) {
            //alert("Theaters: " + data);
            if (data === null) return errorHandler();
            $('#theaters-grid').append(data);
        },
        complete: function () {
            $('.tmdb').click(function (e) {
                e.preventDefault();
                //alert('click');
                loadMovie($(this).prop('id'));
            });
            $('.spinner').hide();
        }
    });
}


function loadReleases() {
    //alert("In Releases");
    $('#releases-grid').empty();
    $.ajax({
        url: WEBDIR + "manager/Tmdb?source=releases&page=2",
        type: 'get',
        dataType: 'html',
        success: function (data) {
            //alert("Releases: " + data);
            if (data === null) return errorHandler();
            $('#releases-grid').append(data);
        },
        complete: function () {
            $('.tmdb').click(function (e) {
                e.preventDefault();
                //alert('click');
                loadMovie($(this).prop('id'));
            });
            $('.spinner').hide();
        }
    });
}


function loadTopRated() {
    //alert("In Top Rated");
    $('#toprated-grid').empty();
    $.ajax({
        url: WEBDIR + "manager/Tmdb?source=toprated&page=2",
        type: 'get',
        dataType: 'html',
        success: function (data) {
            //alert("Top Rated: " + data);
            if (data === null) return errorHandler();
            $('#toprated-grid').append(data);
        },
        complete: function () {
            $('.tmdb').click(function (e) {
                e.preventDefault();
                //alert('click');
                loadMovie($(this).prop('id'));
            });
            $('.spinner').hide();
        }
    });
}


function loadPopular() {
    //alert("In Popular");
    $('#popular-grid').empty();
    $.ajax({
        url: WEBDIR + "manager/Tmdb?source=popular&page=2",
        type: 'get',
        dataType: 'html',
        success: function (data) {
            //alert("Popular: " + data);
            if (data === null) return errorHandler();
            $('#popular-grid').append(data);
        },
        complete: function () {
            $('.tmdb').click(function(e){
                e.preventDefault();
                //alert('click');
                loadMovie($(this).prop('id'));
            });
            $('.spinner').hide();
        }
    });
}

var movieLoad = {
    offset: 0,
    request: null,
    limit: 15,
    options: null
};


function loadMovie(id) {
    //alert('load movie ' + id);
    var sendData = {
        tmdbid: id
    };
    $.ajax({
        url: WEBDIR + "manager/GetMovie",
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            //alert(data.head);
            //alert(data.body);
            var head = ' + movie.year + ';
            var body = 'body';
            var foot = 'buttons';
            $('#modal_dialog .modal-h3').html(data.head);
            $('#modal_dialog .modal-body').html(data.body);
            $('#modal_dialog .modal-footer').html(data.foot);

            $('#modal_dialog').modal({
                show: true,
                backdrop: false
            });

            //$('.modal-fanart').css({
                //'background-image': 'url(' + WEBDIR + 'xbmc/GetThumb?w=950&h=450&o=10&thumb=' +            encodeURIComponent(movie.fanart) + ')'
    //});
        }
    });
}
 


function loadMovies() {
   $('#movie-table').empty();
    var sendData = {
        offset: movieLoad.offset,
        limit: movieLoad.limit
    };
    $.extend(sendData);
    movieLoad.request = $.ajax({
        url: WEBDIR + "manager/GetMovies",
        type: 'get',
        data: sendData,
        dataType: 'text',
        success: function (data) {
            if (data === null) return errorHandler();
            $('#movie-table').append(data);
        },
        complete: function () {
            $('.spinner').hide();
        }
    });
}

function showMovie(title, content, buttons) {
    alert('showMovie');
    $('#modal_dialog .modal-h3').html(title);
    $('#modal_dialog .modal-body').html(content);
    var footer = $('#modal_dialog .modal-footer').empty();
    $('#modal_dialog').modal({
        show: true,
        backdrop: false
    });
}

var showLoad = {
    offset: 0,
    request: null,
    limit: 15,
    options: null
};

function loadShows() {
   $('#show-table').empty();
    var sendData = {
        offset: showLoad.offset,
        limit: showLoad.limit
    };
    $.extend(sendData);
    showLoad.request = $.ajax({
        url: WEBDIR + "manager/GetShows",
        type: 'get',
        data: sendData,
        dataType: 'text',
        success: function (data) {
            if (data === null) return errorHandler();
            $('#show-table').append(data);
        },
        complete: function () {
            $('.spinner').hide();
        }
    });
}


function reloadTab() {
    if ($('#movies').is(':visible')) {
        loadMovies();
    } 
    else if ($('#shows').is(':visible')) {
        loadShows();
    } 
    else if ($('#theaters').is(':visible')) {
        loadInTheaters();
    } 
    else if ($('#releases').is(':visible')) {
        loadReleases();
    } 
    else if ($('#toprated').is(':visible')) {
        loadTopRated();
    } 
    else if ($('#popular').is(':visible')) {
        loadPopular();
    } 
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
$('#pmovie').click(function () {
    movieLoad.offset -= movieLoad.limit;
    loadMovies();
});
    
$('#nmovie').click(function () {
    movieLoad.offset += movieLoad.limit;
    loadMovies();
});

$('#pshow').click(function () {
    showLoad.offset -= showLoad.limit;
    loadShows();
});
    
$('#nshow').click(function () {
    showLoad.offset += showLoad.limit;
    loadShows();
});


var pageoptions = {
    limit: 30,
    offset: 0
};
    
$(document).ready(function () {
    $('.spinner').show();
    //loadMovies();
    //loadShows();
    //loadInTheaters();
    reloadTab();
    $('.spinner').hide();

    // Load data on tab display
    $('a[data-toggle="tab"]').click(function (e) {
        $('#search').val('');
        searchString = '';
    }).on('shown', reloadTab);
    $(window).trigger('hashchange');

    // Load more titles on scroll
//    $(window).scroll(function () {
//        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 10) {
//            reloadTab();
//        }
//    });
});

