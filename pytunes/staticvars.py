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

    vars['tmdb_movie_modal_middle'] = """
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

    vars['tmdb_tv_modal_middle'] = """
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
                                    Status:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    First Aired:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Last Aired:
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
                            <p class="modal-info-item">
                                <b>
                                    Seasons:
                                </b>
                                 %s
                            </p>
                            <p class="modal-info-item">
                                <b>
                                    Episodes:
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

    vars['proc_row'] = """
<tr>
    <td class="processes-pid">
        <a href="#" class="show-proc" data-pid="%s">
            %s
        </a>
    </td>
    <td class="processes-name span2">
        %s
    </td>
    <td class="processes-owner">
        %s
    </td>
    <td class="processes-cpu span1">
        %s
    </td>
    <td class="processes-command span3">
        %s
    </td>
    <td class="processes-status">
        %s
    </td>
    <td class="processes-memory">
        %s
    </td>
    <td class="processes-runningtime">
        %s
    </td>
    <td>
        <button class="btn btn-mini btn-danger cmd" data-pid="%s" data-cmd="kill">
            <i class="icon-remove"></i>
        </button>
    </td>
</tr>

    """

    vars['yify_carousel'] = """
<div class="item carousel-item" style="background-image: url('/manager/GetThumb?h=240&w=430&thumb=%s')">
    <div class="carousel-caption">
        <h4>
            %s
        </h4>
        <p style="display: none;">
            <b>
                Runtime
            </b>
            : %s
            <br>
            <b>
                Genre
            </b>
            : %s
            <br>
            %s
        </p>
    </div>
</div>
    """

    vars['imdb'] = '<a href="http://www.imdb.com/title/%s" target="_blank"><button class="btn btn-primary">IMDB</button></a>&nbsp;&nbsp;'

    vars['actor_imdb'] = '<a href="http://www.imdb.com/name/%s" title="%s-->%s" target="_blank">%s</a>'

    vars['yify_link'] = 'http://yts.re/api/list.json?limit=%s&set=%s&quality=%s&rating=%s&keywords=%s&genre=%s&sort=%s&order=%s'

    vars['actor_li'] = '<li title="%s --> %s"><a href="#"><img class="thumbnail actor-thumb" src="/manager/GetThumb?w=83&h=125&thumb=%s"></img><h6 class="title">%s</h6><h6 class="title">%s</h6></a></li>'

    vars['row19'] =  "<tr><td>%s<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
    
    vars['tmdb_thumb_item'] = """<li title="%s"><a href="#" id="%s" class="tmdb"><img class="thumbnail" src="/manager/GetThumb?w=100&h=150&thumb=%s"></img><h6 class="title">%s</h6></a></li>"""

    vars['yify_thumb_item'] = """<li title="%s"><a href="#" id="%s" class="yify"><img src="/manager/GetThumb?w=100&h=150&thumb=%s"></img><h6 class="title">%s</h6></a></li>"""

    vars['carousel_item'] = """<div class="item carousel-item" style="background-image: url('/manager/GetThumb?h=240&w=430&thumb=http://image.tmdb.org/t/p/original%s')"><div class="carousel-caption"><h4>%s (%s)</h4></div></div>"""

    vars['trailer_button'] = '<div class="btn-group"><button id="youtube" ytid="%s" class="btn btn-primary">Trailer</button></div>'

    vars['download_button'] = '<div class="btn-group"><button id="download" class="btn btn-primary" title="Find This Movie!" tmdb="%s">Get It!</button></div>'

    vars['addshow_button'] = '<div class="btn-group"><a href="/sickbeard?query=%s"><button id="addshow" class="btn btn-primary" title="Add This Show!">Add Show</button></a></div>'

    vars['torrent_button'] = '<div class="btn-group"><button id="download" class="btn btn-primary" title="Download This Movie!" yify_link="%s">Download</button></div>'

    vars['close_button'] = '<div class="btn-group"><button class="btn btn-primary" data-dismiss="modal">Close</button></div>'

    vars['terminate_button'] = '<div class="btn-group"><button class="btn btn-primary process modal-cmd" data-pid="%s" data-cmd="terminate" data-dismiss="modal">Terminate</button></div>'

    vars['kill_button'] = '<div class="btn-group"><button class="btn btn-primary process modal-cmd" data-pid="%s" data-cmd="kill" data-dismiss="modal">Kill</button></div>'

    vars['suspend_button'] = '<div class="btn-group"><button class="btn btn-primary process modal-cmd" data-pid="%s" data-cmd="suspend cmd" data-dismiss="modal">Suspend</button></div>'

    vars['resume_button'] = '<div class="btn-group"><button class="btn btn-primary process modal-cmd" data-pid="%s" data-cmd="resume" data-dismiss="modal">Resume</button></div>'

    vars['dash_stats'] = "<tr><td>%s</td><td>%s</td><td><div class='progress'><div class='bar bar-danger' style='width:%s'></div><div class='bar bar-info' style='width:%s' ></div></div></td></tr>"

    vars['stats_modal'] = """
<table class="span6">
<tr><td class="span1"><b>Command</b></td><td class="span5">%s</td></tr>
</table>
<table class="span6">
<tr><td><b>PID</b></td><td>%s</td><td><b>CPU</b></td><td>%s</td></tr>
<tr><td><b>Owner</b></td><td>%s</td><td><b>Status</b></td><td>%s</td><tr>
<tr><td><b>UID</b></td><td>%s</td><td><b>GID</b></td><td>%s</td><tr>
<tr><td><b>Nice</b></td><td>%s</td><td><b>Memory</b></td><td>%s</td></tr>
<tr><td><b>Started</b></td><td>%s</td><td><b>Run time</b></td><td>%s</td></tr>
</table>
    """

    return vars[var]

