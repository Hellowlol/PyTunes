
var page_counts = {
    theaters: 1,
    releases: 1,
    popular: 1,
    toprated: 1
};    


function loadInTheaters(page) {
    alert("In Theaters" + page);
    $.ajax({
        url: WEBDIR + "manager/Tmdb?source=intheaters&page=" + page,
        type: 'get',
        dataType: 'html',
        success: function (data) {
            //alert("Theaters: " + data);
            if (data === null) return errorHandler();
            $('#theaters-grid').append(data);
            //page_counts.theaters += 1;
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


function loadReleases(page) {
    alert("In Releases" + page);
    $.ajax({
        url: WEBDIR + "manager/Tmdb?source=releases&page=" + page,
        type: 'get',
        dataType: 'html',
        success: function (data) {
            //alert("Releases: " + data);
            if (data === null) return errorHandler();
            $('#releases-grid').append(data);
            //page_counts.releases += 1;
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

function loadTopRated(page) {
    alert("In Top Rated" + page);
    $.ajax({
        url: WEBDIR + "manager/Tmdb?source=toprated&page=" + page,
        type: 'get',
        dataType: 'html',
        success: function (data) {
            //alert("Top Rated: " + data);
            if (data === null) return errorHandler();
            $('#toprated-grid').append(data);
            //page_counts.toprated += 1;
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


function loadPopular(page) {
    alert("In Popular" + page);
    $.ajax({
        url: WEBDIR + "manager/Tmdb?source=popular&page=" + page,
        type: 'get',
        dataType: 'html',
        success: function (data) {
            //alert("Popular: " page_counts.popular);
            if (data === null) return errorHandler();
            $('#popular-grid').append(data);
            //page_counts.popular += 1;
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

            $('.modal-fanart').css({
                'background-image': 'url(' + WEBDIR + 'manager/GetThumb?w=950&h=450&o=10&thumb=' + encodeURIComponent(data.fanart) + ')'
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

//Initial Load
function loadTab() {
    if ($('#movies').is(':visible')) {
        loadMovies();
    } 
    else if ($('#shows').is(':visible')) {
        loadShows();
    } 
    else if ($('#theaters').is(':visible')) {
        $('#theaters-grid').empty();
        loadInTheaters(page_counts['theaters']);
        page_counts['theaters'] += 1;
    } 
    else if ($('#releases').is(':visible')) {
        $('#releases-grid').empty();
        loadReleases(page_counts['releases']);
        page_counts['releases'] += 1;
    } 
    else if ($('#toprated').is(':visible')) {
        $('#toprated-grid').empty();
        loadTopRated(page_counts['toprated']);
        page_counts['toprated'] += 1;
    } 
    else if ($('#popular').is(':visible')) {
        $('#popular-grid').empty();
        loadPopular(page_counts['popular']);
        page_counts['popular'] += 1;
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

//reLoad
function reloadTab() {
    if ($('#theaters').is(':visible')) {
        loadInTheaters(page_counts['theaters']);
        page_counts['theaters'] += 1;
    } 
    else if ($('#releases').is(':visible')) {
        loadReleases(page_counts['releases']);
        page_counts['releases'] += 1;
    } 
    else if ($('#toprated').is(':visible')) {
        loadTopRated(page_counts['toprated']);
        page_counts['toprated'] += 1;
    } 
    else if ($('#popular').is(':visible')) {
        loadPopular(page_counts['popular']);
        page_counts['popular'] += 1;
    } 
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
    loadTab();
    $('.spinner').hide();

    // Load data on tab display
    $('a[data-toggle="tab"]').click(function (e) {
        $('#search').val('');
        searchString = '';
    }).on('shown', loadTab);

    $(window).trigger('hashchange');

    // Load more titles on scroll
    $(window).scroll(function () {
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 10) {
            reloadTab();
        }
    });


});

