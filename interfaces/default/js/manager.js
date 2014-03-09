
var movieLoad = {
    offset: 0,
    request: null,
    limit: 15,
    options: null
};

function loadMovies() {
   $('#movie-table').empty();
    var sendData = {
        //offset: (movieLoad.offset + movieLoad.limit),
        //limit: movieLoad.limit,
        offset: movieLoad.offset,
        limit: movieLoad.limit
    };
    $.extend(sendData);
     //var start = 50;
    //$.get(WEBDIR + "manager/GetData?offset=" + offset + "&limit=" + limit, function (response) {
    movieLoad.request = $.ajax({
        //url: WEBDIR + "manager/GetData?offset=" + offset + "&limit=" + limit,
        url: WEBDIR + "manager/GetData",
        type: 'get',
        data: sendData,
        dataType: 'text',
        success: function (data) {
            //if (data === null) return errorHandler();
            $('#movie-table').append(data);
        },
        complete: function () {
            $('.spinner').hide();
        }
    });
        //alert(response);
        //$("#movie-table").append(response);
        //$('#pages').bootstrapPaginator(pageoptions);
        //$('#pages').append('pageoptions');
}

//var movieLoad = {
//    last: 0,
//    request: null,
//    limit: 50,
//    options: null
//};


function loadMovies2(options) {
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
        end: (movieLoad.last + movieLoad.limit)
    };
    $.extend(sendData, options);

    $('.spinner').show();
    movieLoad.request = $.ajax({
        url: WEBDIR + 'manager/GetMovies',
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
$('#pmovie').click(function () {
    movieLoad.offset = movieLoad.offset - movieLoad.limit;
    loadMovies();
});
    
$('#nmovie').click(function () {
    movieLoad.offset = movieLoad.offset + movieLoad.limit;
    loadMovies();
});
    
$(document).ready(function () {
    var pageoptions = {
        limit: 30,
        offset: 0
    };
    $('.spinner').show();
    loadMovies();
    $('.spinner').hide();
});

