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
    return vars[var]

