#!/usr/bin/env python
# -*- coding: utf-8 -*-

def get_var(var):

    vars = {}
    vars['movienfo'] = """
<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
    <title>%s</title>
    <originaltitle>%s</originaltitle>
    <sorttitle>%s</sorttitle>
    <set>%s</set>
    <setthumb>%s</setthumb>
    <setfanart>%s</setfanart>
    <rating>%s</rating>
    <year>%s</year>
    <top250>%s</top250>
    <votes>%s</votes>
    <outline>%s</outline>
    <plot>%s</plot>
    <tagline>%s</tagline>
    <runtime>%s</runtime> //runtime in minutes
%s      //thumbs
    <fanart>
%s
    </fanart>
    <mpaa>%s</mpaa>
    <playcount>0</playcount>
    <id>${imdb}</id>
    <filenameandpath></filenameandpath>
%s     //trailers
    <genre>${genre}</genre>
    <credits></credits>
    <fileinfo>
        <streamdetails>
            <video>
                <codec>%s</codec>
                <aspect>%s</aspect>
                <width>%s</width>
                <height>%s</height>
            </video>
            <audio>
                <codec>%s</codec>
                <language></language>
                <channels>%s</channels>
            </audio>
            <subtitle>
                <language></language>
            </subtitle>
        </streamdetails>
    </fileinfo>
    <director>%s</director>
    <writer>%s</writer>
%s      //actors
    <art>
%s      //arts
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
    vars['carousel_item'] = """<div class="item carousel-item" style="background-image: url('/manager/GetThumb?h=240&w=430&thumb=http://image.tmdb.org/t/p/original%s')"><div class="carousel-caption"><h4>%s (%s)</h4></div></div>"""

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
    vars['trans_queuetop'] = "<a href='/transmission/Queue_Move?id=%s&pos=%s' class='queue btn btn-mini torrent-action' title='Move to Top'><i class='icon-long-arrow-up'></i></a>"
    vars['trans_queueup'] = "<a href='/transmission/Queue_Move?id=%s&pos=%s' class='queue btn btn-mini torrent-action' title='Move Up 1 Level'><i class='icon-level-up'></i></a>"
    vars['trans_queuedown'] = "<a href='/transmission/Queue_Move?id=%s&pos=%s' class='queue btn btn-mini torrent-action' title='Move Down 1 Level'><i class='icon-level-down'></i></a>"
    vars['trans_queuebottom'] = "<a href='/transmission/Queue_Move?id=%s&pos=%s' class='queue btn btn-mini torrent-action' title='Move to Bottom'><i class='icon-long-arrow-down'></i></a>"
    vars['trans_row'] = """
<tr>
    <td>
        <a href='#' class='show-torr' torr-id='%s'>
            %s
        </a>
        <br>
        <small><i class='icon-download'></i>
            %s
        &nbsp;&nbsp;
        <i class='icon-upload'></i>
            %s
            &nbsp;&nbsp;&nbsp;&nbsp;connected:&nbsp;%s&nbsp;&nbsp;seeds:&nbsp;%s&nbsp;&nbsp;leach:&nbsp;%s
        </small>
    </td>
    <td>
        %s
    </td>
    <td>
        %s
    </td>
    <td>
        %s
    </td>
    <td>
        %s&nbsp;/&nbsp;%s
    </td>
    <td>
        %s
    </td>
    <td>
        <div class = 'progress %s'>
            <div class='bar' style='width:%s;'></div>
            <span><b>%s</b></span>
        </div>
    </td>
    <td>
        <div class='button-group'>
            %s
        </div>
    </td>
</tr>
    """
    vars['trans_start'] = "<a href='/transmission/start/%s' title='Send to Queue' class='btn btn-mini torrent-action'><b>Que</b></a>"

    vars['trans_start_now'] = "<a href='/transmission/start_now/%s' title='Force Start Now' class='btn btn-mini torrent-action'><i class='icon-exclamation'></i>&nbsp;<i class='icon-play'></i></a>"

    vars['trans_pause'] = "<a href='/transmission/stop/%s' title='Pause Torrent' class='btn btn-mini torrent-action'><i class='icon-pause'></i></a>"

    vars['trans_remove'] = "<a href='/transmission/remove/%s' title='Remove Torrent' class='btn btn-mini torrent-action'></i><i class='icon-remove'></i></a>"

    vars['trans_remove_data'] = "<a href='/transmission/remove/%s/True' title='Remove Torrent and Data' class='btn btn-mini torrent-action'><i class='icon-trash'></i></a>"

    vars['trans_reannounce'] = "<a href='/transmission/reannounce/%s' title='Ask Tracker For More Peers' class='btn btn-mini torrent-action'><i class='icon-microphone'></i></a>"

    vars['trans_files'] = "<a href='/transmission/files/%s' title='Edit %s Files' class='btn btn-mini torrent-files'><i class='icon-copy'></i></a>"

    vars['trans_error'] = "<button title='Click for Error Message' class='btn btn-mini btn-danger torrent-error' message='%s'><i class='icon-warning-sign'></i></button>"

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

    vars['actor_li'] = '<li class="pull-left" title="%s --> %s"><a href="#"><img class="thumbnail actor-thumb" src="/manager/GetThumb?w=83&h=125&thumb=%s"></img><h6 class="title">%s</h6><h6 class="title">%s</h6></a></li>'

    vars['row19'] =  "<tr><td>%s<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
    
    vars['tmdb_thumb_item'] = """<li class="pull-left" title="%s"><a href="#" id="%s" class="tmdb"><img class="thumbnail" src="/manager/GetThumb?w=100&h=150&thumb=%s"></img><h6 class="title">%s</h6></a></li>"""

    vars['yify_thumb_item'] = """<li title="%s"><a href="#" id="%s" class="yify"><img src="/manager/GetThumb?w=100&h=150&thumb=%s"></img><h6 class="title">%s</h6></a></li>"""

    vars['trailer_button'] = '<div class="btn-group"><button id="youtube" ytid="%s" class="btn btn-primary">Trailer</button></div>'

    vars['download_button'] = '<div class="btn-group"><button id="download" class="btn btn-primary" title="Find This Movie!" tmdb="%s" imdb="%s" name="%s" year="%s" fanart="%s" thumb="%s" plot="%s" rating="%s" genre="%s" runtime="%s" writers="%s" country="%s" studios="%s" actors="%s" directors="%s">Get It!</button></div>'

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

    vars['torrent_search_table'] = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><button class='btn btn-mini download' torr_link=%s title='Send to Download'><i class=icon-download-alt></button></td></tr>"

    return vars[var]

