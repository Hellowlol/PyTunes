def get_var(var):

    movienfo = """
    <movie>
        <title>%s</title>
        <originaltitle>%s</originaltitle>
        <sorttitle></sorttitle>
        <set>%s</set>
        <rating>%s</rating>
        <year>%s</year>
        <top250>%s</top250>
        <votes>%s</votes>
        <outline>%s</outline>
        <plot>%s</plot>
        <tagline>%s</tagline>
        <runtime>%s</runtime> //runtime in minutes
        <thumb>%s</thumb>
        <mpaa>%s</mpaa>
        <playcount>0</playcount><!-- setting this to > 0 will mark the movie as watched if the "importwatchedstate" flag is set in advancedsettings.xml -->
        <id>%s</id><!--imdb-->
        <filenameandpath>%s</filenameandpath>
        <trailer>%s</trailer>
        <genre>%s</genre>
        <credits>%s</credits>
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
                    <language>%s</language>
                    <channels>%s</channels>
                </audio>
                <subtitle>
                    <language></language>
                </subtitle>
            </streamdetails>
        </fileinfo>
        <director>%s</director>
        %s<!--actors-->
        <actor>
            <name></name>
            <role></role>
            <thumb></thumb>
        </actor>
        <art>
        %s <!--folder art-->
        </art>
    </movie>
    """
    if var == 'movienfo':
        return movienfo
    else: 
        return 'Invalid Variable Name'

