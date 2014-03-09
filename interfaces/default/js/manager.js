
var movieLoad = {
    offset: 0,
    request: null,
    limit: 15,
    options: null
};

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
    loadMovies();
    loadShows();
    $('.spinner').hide();
});

