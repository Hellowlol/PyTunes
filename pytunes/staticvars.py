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

    vars['yify_modal_middle'] = """
            <div>
                <div class="modal-body-middle">
                    <div class="pull-left modal-body-middle-left">
                        <p>
                            <img class="modal-movie-poster" src="/manager/GetThumb?w=133&h=200&thumb=%s"></img>
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
                                    Rating:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Runtime:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    MPAA:
                                </b>
                                 %s
                            </p>
                        </div>
                        <div class="pull-right">
                            <p class="modal-info-item">
                                <b>
                                    Actors:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Size:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Seeds:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Language:
                                </b>
                                 %s
                            </p>
                        </div>
                   </div>
                </div>

    """

    vars['imdb'] = '<a href="http://www.imdb.com/title/%s" target="_blank"><button class="btn btn-primary">IMDB</button></a>&nbsp;&nbsp;'

    vars['actor_imdb'] = '<a href="http://www.imdb.com/name/%s" title="%s-->%s" target="_blank">%s</a>'

    vars['trailer'] = '<button id="youtube" ytid="%s" class="btn btn-primary">Trailer</button>'

    vars['actor_li'] = '<li title="%s --> %s"><a href="#"><img class="thumbnail actor-thumb" src="/manager/GetThumb?w=83&h=125&thumb=%s"></img><h6 class="title">%s</h6><h6 class="title">%s</h6></a></li>'

    vars['row19'] =  "<tr><td>%s<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
    
    vars['thumb_item'] = """<li title="%s"><a href="#" id="%s" class="tmdb"><img class="thumbnail" src="/manager/GetThumb?w=100&h=150&thumb=%s"></img><h6 class="title">%s</h6></a></li>"""

    vars['yify_thumb_item'] = """<li title="%s"><a href="#" id="%s" class="yify"><img src="/manager/GetThumb?w=100&h=150&thumb=%s"></img><h6 class="title">%s</h6></a></li>"""

    vars['carousel_item'] = """<div class="item carousel-item" style="background-image: url('/manager/GetThumb?h=240&w=430&thumb=http://image.tmdb.org/t/p/original%s')"><div class="carousel-caption"><h4>%s (%s)</h4></div></div>"""

    vars['download_button'] = '<button id="download" class="btn btn-primary" title="Find This Movie!" tmdb="%s">Get It!</button>'

    vars['torrent_button'] = '<button id="download" class="btn btn-primary" title="Download This Movie!" yify_link="%s">Download</button>'

    vars['close_button'] = '<button class="btn btn-primary" data-dismiss="modal">Close</button>'

    return vars[var]

