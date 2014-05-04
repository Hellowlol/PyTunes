def get_var(var):

    vars = {}
    vars['movienfo'] = """
<movie>
    <title>${title}</title>
    <originaltitle>${originaltitle}</originaltitle>
    <sorttitle></sorttitle>
    <set>${setname}</set>
    <setthumb>${setthumb}</setthumb>
    <setfanart>${setfanart}</setfanart>
    <rating>${rating}</rating>
    <year>${year}</year>
    <top250>${top250}</top250>
    <votes>${votes}</votes>
    <outline>${outline}</outline>
    <plot>${plot}</plot>
    <tagline>${tagline}</tagline>
    <runtime>${runtime}</runtime> //runtime in minutes
${thumbs}
    <fanart>
${fanarts}
    </fanart>
    <mpaa>${mpaa}</mpaa>
    <playcount>0</playcount>
    <id>${imdb}</id>
    <filenameandpath></filenameandpath>
${trailers}
    <genre>${genre}</genre>
    <credits></credits>
    <fileinfo>
        <streamdetails>
            <video>
                <codec>${vcodec}</codec>
                <aspect>$aspect}</aspect>
                <width>${width}</width>
                <height>${height}</height>
            </video>
            <audio>
                <codec>${acodec}</codec>
                <language></language>
                <channels>${channels}</channels>
            </audio>
            <subtitle>
                <language></language>
            </subtitle>
        </streamdetails>
    </fileinfo>
    <director>${director}</director>
    <writer>${writer}</writer>
${actors}
    <art>
${arts}
    </art>
</movie>
    """

    vars['actor'] = """
    <actor>
        <name>%s</name>
        <role>%s</role>
        <thumb>%s</thumb>
    </actor> 
    """
    vars['carousel_item'] = "<div class='item carousel-item' style='background-image: url(\"/xbmc/GetThumb?h=240&w=430&thumb=http://image.tmdb.org/t/p/original%s\")'><div class='carousel-caption'><h4>%s (%s)</h4></div></div>"
    
    vars['carousel_item2'] = """
<div class="item carousel-item" style="background-image: url('/manager/GetThumb?h=240&w=430&thumb=http://image.tmdb.org/t/p/original%s')">
    <div class='carousel-caption'>
        <h4>%s (%s)</h4>
            <b>Rating</b>: 
    </div>
</div> 
    """

    vars['modal_middle'] = """
            <div>
                <div class="modal-body-middle">
                    <div class="pull-left modal-body-middle-left">

                        <p>
                            <img class="thumbnail modal-movie-poster" src="/manager/GetThumb?w=133&h=200&thumb=%s"></img>
                        </p>
                    </div>
                    <div class="modal-body-middle-right">
                        <p>
                            <b>
                                Plot:
                            </b>
                            %s
                        </p>
                        <div class="pull-left">
                            <p class="modal-info-item">
                                <b>
                                    Director:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Genre:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Runtime:
                                </b>
                                 %s
                            </p>
                        </div>
                        <div class="pull-right">
                            <p class="modal-info-item">
                                <b>
                                    Writer:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Country:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Studio:
                                </b>
                                 %s
                            </p>
                        </div>
                   </div>
                </div>
                <div class="modal-body-bottom pull-left">
                    <ul class="thumbnails">%s</ul>
                </div>

    """



    
    return vars[var]

