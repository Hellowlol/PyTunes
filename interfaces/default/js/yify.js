function loadNewest() {
    //alert("In Newest" + page);
    $.ajax({
        url: WEBDIR + "yify/newest",
        type: 'get',
        dataType: 'html',
        success: function (data) {
            //alert("Newest: " page_counts.popular);
            if (data === null) return errorHandler();
            $('#yify-grid').append(data);
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

$(document).ready(function () {
    $('.spinner').show();
    loadNewest();
    //loadShows();
    //loadInTheaters();
    //loadTab();
    $('.spinner').hide();
    // Load data on tab display
    //$('a[data-toggle="tab"]').click(function (e) {
    //    $('#search').val('');
     //   searchString = '';
    //}).on('shown', loadTab);


    // Load more titles on scroll
    //$(window).scroll(function () {
    //    if ($(window).scrollTop() + $(window).height() >= $(document).height() - 10) {
//reloadTab();
     //   }
    //});
});

