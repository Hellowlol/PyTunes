/**
 * Converts bytes to readable filesize in kb, MB, GB etc.
 */

// For hdd.
function getReadableFileSizeStringHDD(fileSizeInBytes) {
    var i = -1;
    var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB'];
    do {
        fileSizeInBytes = fileSizeInBytes / 1000;
        i++;
    } while (fileSizeInBytes > 1000);
    return fileSizeInBytes.toFixed(1) + byteUnits[i];
}


function getReadableFileSizeString(fileSizeInBytes) {
    var i = -1;
    var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB'];
    do {
        fileSizeInBytes = fileSizeInBytes / 1024;
        i++;
    } while (fileSizeInBytes > 1024);
    return fileSizeInBytes.toFixed(1) + byteUnits[i];
}

// Makes the harddisk lists
function get_diskinfo() {
    $.ajax({
        'url': WEBDIR + 'stats/disk_usage',
            'dataType': 'json',
            'success': function (response) {
            $('#files-table').html("");
            $('#error_message').text("");

            $.each(response, function (i, disk) {
                var row = $('<tr>');
                var progressBar = $('<div>');
                var progress2 = "<div class='progress hddprog'><div class=bar style=width:" + disk.percent + "%><span class=sr-only>" + getReadableFileSizeStringHDD(disk.used) + "</span></div><div class='bar bar-success' style=width:" + (100 - disk.percent) + "% ><span class=sr-only>" + getReadableFileSizeStringHDD(disk.free) + "</span></div>";

                if (disk.percent >= 87) {
                    //progress2.addClass('progress-danger'); // need to check, does not work
                }

                row.append(
                $('<td>').addClass('qbt_name').text(disk.mountpoint),
                $('<td>').addClass('qbt_name').text(disk.device),
                $('<td>').addClass('qbt_name').text(disk.fstype),
                $('<td>').addClass('qbt_ratio').text(getReadableFileSizeStringHDD(disk.free)),
                $('<td>').addClass('qbit_eta').text(getReadableFileSizeStringHDD(disk.used)),
                $('<td>').addClass('qbt_state').text(getReadableFileSizeStringHDD(disk.total)),
                //$('<td>').addClass('span3 qbit_progress').html(progress2),
                $('<td>').addClass('qbt_state').text(disk.percent));
                $('#files-table').append(row);
            });
            $('.spinner').hide();
        }
    });
}

// Makes the harddisk bars
function get_diskinfo2() {
    $.ajax({
        'url': WEBDIR + 'stats/disk_usage2',
            'dataType': 'json',
            'success': function (response) {
            $('#disk-table').html("");
            $('#error_message').text("");
            var bars = $('<span>');
            $.each(response, function (i, disk) {
                var row = $('<tr>');
                var progress2 = "<div class='progress hddprog'>    <div class='bar bar-danger' style='width:" + disk.percent + "%'></div><div class='bar bar-info' style='width:" + (100 - disk.percent) + "%' ></div></div>";

                if (disk.percent >= 87) {
                    //progress2.addClass('progress-danger'); // need to check, does not work
                }

                row.append(
                $('<td>').addClass('qbt_name').text(disk.mountpoint),
                $('<td>').addClass('qbt_name').text(disk.device),
                $('<td>').addClass('qbt_name').text(disk.fstype),
                $('<td>').addClass('qbt_ratio').text(getReadableFileSizeStringHDD(disk.free)),
                $('<td>').addClass('qbit_eta').text(getReadableFileSizeStringHDD(disk.used)),
                $('<td>').addClass('qbt_state').text(getReadableFileSizeStringHDD(disk.total)),
                $('<td>').addClass('span3 qbit_progress').html(progress2),
                $('<td>').addClass('qbt_state').text(disk.percent));
                $("#disk-table").append(row);
            });
            $('.spinner').hide();
        }
    });
}

function uptime() {
    $.getJSON(WEBDIR + "stats/uptime2", function (data) {
        $(".r").text("Uptime: " + data.uptime);
    });
}


$(document).on('click', '.cmd', function () {
    var x = $(this).attr('data-pid');
    //alert(x);
    if (confirm('Are you sure?')) {
        $.getJSON(WEBDIR + "stats/command/" + $(this).attr('data-cmd') + "/" + $(this).attr('data-pid'), function (response) {
            alert('click');
        });
    }
});


function get_external_ip() {
    $.getJSON(WEBDIR + "stats/get_external_ip", function (response) {
        //$(".externalip").append("External ip : "+ response.externalip);
        $(".txip").text(response.externalip);

    });
}


function get_local_ip() {
    $.getJSON(WEBDIR + "stats/get_local_ip", function (response) {
        //$(".localip").text("Local ip: "+ response.localip);
        $(".tlip").text(response.localip);

    });
}

function network_usage() {
    $.getJSON(WEBDIR + "stats/network_usage", function (response) {
        //alert(response);
        $(".nw").append("<div>Recv: " + getReadableFileSizeString(response.bytes_recv) + "</div>");
        $(".nw").append("<div>Sent: " + getReadableFileSizeString(response.bytes_sent) + "</div>");
        $(".nw").append("<div>Error in: " + response.errin + "</div>");
        $(".nw").append("<div>Error out: " + response.errout + "</div>");
        $(".nw").append("<div>Drop in: " + response.dropin + "</div>");
        $(".nw").append("<div>Drop out: " + response.dropout + "</div>");
    });
}

function network_usage_table() {
    $.getJSON(WEBDIR + "stats/network_usage", function (response) {
        //alert(response);
        $("#stat-sent").text(getReadableFileSizeString(response.bytes_sent));
        $("#stat-recv").text(getReadableFileSizeString(response.bytes_recv));
        $(".nw").html("<table class='table-fluid nwtable'><tr><td class=span4>Network</td><td class=span4>In</td><td class=span4>Out</td</tr><tr><td>Drop</td><td>" + response.dropin + "</td><td>" + response.dropout + "</td></tr><tr><td>Error</td><td>" + response.errin + "</td><td>" + response.errout + "</td></tr><tr><td>IP</td><td class=tlip></td><td class=txip></td></tr></tbody></table>");
    });
}

function get_user() {
    $.getJSON(WEBDIR + "stats/get_user", function (response) {
        $(".l").text(response.name + " logged in " + response.started + " ago");
    });
}

function sys_info() {
    $.getJSON(WEBDIR + "stats/sys_info", function (response) {
        //alert(response);
        $(".c").html("<div>" + response.system + ' ' + response.release + ' ' + response.user + "</div>");
    });
}


function virtual_memory_nobar() {
    $.getJSON(WEBDIR + "stats/virtual_memory", function (virtual) {
        //alert(response);
        var progressBar = $('<div>');
        progressBar.addClass('bar');
        progressBar.css('width', (virtual.percent) + '%');
        progressBar.text('Memory: ' + virtual.percent + ' %');
        var progress = $('<div>');
        progress.addClass('progress');

        if (virtual.percent >= 90) {
            progress.addClass('progress-danger');
        }
        progress.append(progressBar);
        //$(".virmem").append(progress);
        $(".virmem").append("<div class=nonbar>Physical Memory: " + virtual.percent + "%</div>");
        $(".virmem").append("<div>Total: " + getReadableFileSizeString(virtual.total) + "</div>");
        $(".virmem").append("<div>Used: " + getReadableFileSizeString(virtual.used) + "</div>");
        $(".virmem").append("<div>Free: " + getReadableFileSizeString(virtual.available) + "</div>");

    });
}

function virtual_memory_bar() {
    $.getJSON(WEBDIR + "stats/virtual_memory", function (virtual) {
        $(".virmem").html("<div>Real Memory</div><div class=progress><div class=bar style=width:" + virtual.percent + "%><span class=sr-only>Used: " + virtual.percent + "%</span></div><div class='bar bar-success' style=width:" + (100 - virtual.percent) + "%><span class=sr-only>Free: " + (100 - virtual.percent) + "%</span></div></div><div class=progress><div class=bar style=width:" + virtual.percent + "%><span class=sr-only>Used: " + getReadableFileSizeString(virtual.total - virtual.available) + "</span></div><div class='bar bar-success' style=width:" + (100 - virtual.percent) + "% ><span class=sr-only>Free: " + getReadableFileSizeString(virtual.available) + "</span></div>");

    });
}

function virtual_memory_table() {
    $.getJSON(WEBDIR + "stats/virtual_memory", function (virtual) {
        $(".virmem").html("<table class='table nwtable'><tr><td class=span4>Real Memory:</td><td class=span4>" + virtual.percent + "%</td></tr><tr><td>Total:</td><td>" + getReadableFileSizeString(virtual.total) + "</td></tr><tr><td>Used:</td><td>" + getReadableFileSizeString(virtual.total - virtual.available) + "</td></tr><tr><td>Free:</td><td>" + getReadableFileSizeString(virtual.available) + "</td></tr></tbody></table>");
    });
}

function swap_memory_bar() {
    $.getJSON(WEBDIR + "stats/swap_memory", function (swap) {
        //alert(response.total);
        $(".swpmem").html("<div>Swap Memory</div><div class=progress><div class=bar style=width:" + swap.percent + "%><span class=sr-only>Used: " + swap.percent + "%</span></div><div class='bar bar-success' style=width:" + (100 - swap.percent) + "%><span class=sr-only>Free: " + (100 - swap.percent) + "%</span></div></div><div class=progress><div class=bar style=width:" + swap.percent + "%><span class=sr-only>Used: " + getReadableFileSizeString(swap.used) + "</span></div><div class='bar bar-success' style=width:" + (100 - swap.percent) + "% ><span class=sr-only>Free: " + getReadableFileSizeString(swap.free) + "</span></div>");

    });
}
function swap_memory_table() {
    $.getJSON(WEBDIR + "stats/swap_memory", function (swap) {
        //alert(response.total);
        $(".swpmem").html("<table class='table nwtable'><tr><td class=span4>Swap Memory:</td><td class=span4>" + swap.percent + "%</td></tr><tr><td>Total:</td><td>" + getReadableFileSizeString(swap.total) + "</td></tr><tr><td>Used:</td><td>" + getReadableFileSizeString(swap.used) + "</td></tr><tr><td>Free:</td><td>" + getReadableFileSizeString(swap.free) + "</td></tr></tbody></table>");
    });
}



function cpu_percent_bar() {
    $.getJSON(WEBDIR + "stats/cpu_percent", function (cpu) {
        //alert(typeof(response.idle));
        $(".cpu").html("<div>CPU</div><div class=progress><div class=bar style=width:" + (cpu.user + cpu.system).toFixed(1) + "%><span class=sr-only>Used: " + (cpu.user + cpu.system).toFixed(1) + "%</span></div><div class='bar bar-success' style=width:" + (100 - (cpu.user + cpu.system)).toFixed(1) + "%><span class=sr-only>Idle: " + cpu.idle.toFixed(1) + "%</span></div></div><div class=progress><div class=bar style=width:" + cpu.user.toFixed(1) + "%><span class=sr-only>User: " + cpu.user.toFixed(1) + "%</span></div><div class='bar bar-warning' style=width:" + cpu.system.toFixed(1) + "%><span class=sr-only>System: " + cpu.system.toFixed(1) + "%</span></div><div class='bar bar-success' style=width:" + (100 - (cpu.user + cpu.system)).toFixed(1) + "%><span class=sr-only>Idle: " + cpu.idle.toFixed(1) + "%</span></div></div>");
    });
}


function cpu_percent_table() {
    $.getJSON(WEBDIR + "stats/cpu_percent", function (cpu) {
        $(".cpu").html("<table class='table nwtable'><tr><td class=span4>CPU:</td><td class=span4>" + (100 - cpu.idle).toFixed(1) + "%</td></tr><tr><td>User:</td><td>" + cpu.user + "%</td></tr><tr><td>System:</td><td>" + cpu.system + "%</td></tr><tr><td>Idle:</td><td>" + cpu.idle + "%</td></tr></tbody></table>");

    });
}

function return_settings3() {
    $.getJSON(WEBDIR + "stats/return_settings", function (return_settings) {
        if (return_settings.stats_use_bars == 'true') {
            cpu_percent_bar();
            swap_memory_bar();
            virtual_memory_bar();
        } else if (return_settings.stats_use_bars == 'false') {
            //cpu_percent_nobar();
            cpu_percent_table();
            //swap_memory_nobar();
            swap_memory_table();
            //virtual_memory_nobar();
            virtual_memory_table();

        } else {
            //pass 
        }
    });
}

function loadProcess(pid) {
    if (confirm('Are you sure you want to kill this process?')) {
        $.getJSON(WEBDIR + "stats/command?cmd=kill&pid=" + pid, function (response) {
            $.pnotify({
                title: 'Response',
                text: response.msg,
                type: 'success',
                width: '500px',
                min_height: '400px'
            });

        });
    }
}

function processes() {
    $.ajax({
        'url': WEBDIR + 'stats/processes',
        'dataType': 'json',
        'success': function (response) {
            $('#proc-table').html("");
            $('#error_message').text("");
            $.each(response, function (i, proc) {
                pid = proc.pid
                var row = $('<tr>');
                //Pid might be used for popen stuff later
                var pidAnchor = $('<a>').attr('href', '#').click(function (e) {
                    e.preventDefault();
                    loadProcess({
                        'pid': pid
                    });
                });
                pidAnchor.append(pid);
                row.attr('data-pid', pid);
                row.append(
                    //pidAnchor,
                    $('<td>').addClass('processes-pid').html(pidAnchor),
                    //$('<td>').addClass('').text(proc.pid),
                    $('<td>').addClass('processes-name span2').text(proc.name),
                    $('<td>').addClass('processes-owner').text(proc.username),
                    $('<td>').addClass('processes-percent span1').text(proc.cpu_percent+ ' %'),
                    $('<td>').addClass('processes-command span3').text(proc.cmdline),
                    $('<td>').addClass('processes-name').text(proc.status),
                    //$('<td>').addClass('processes-memory-info span2').text(proc.memory_percent.toFixed(2) + ' %  / ' + getReadableFileSizeString(proc.memory_info[0])),
                    $('<td>').addClass('processes-memory-info').text(proc.memory_percent.toFixed(2) + '%'),
                    $('<td>').addClass('processes-runningtime').text(proc.r_time),
                    $('<td>').append('<button class="btn btn-mini btn-danger"><i class="icon-remove cmd" data-cmd="kill" data-pid=' + pid + '></i></button>')
                );
                $('#proc-table').append(row);
            });
            $('.spinner').hide();
        }
    });
}

function reloadtab() {
    if ($('#diskt').is(':visible')) {
        get_diskinfo();
    } else if ($('#processes').is(':visible')) {
        processes();
    }
}

   $('#diskt').click(function () {
       get_diskinfo();
   });
    $('#processes').click(function () {
       processes();
   });
    //Can't get the kill to work!
    //Hellow? Hellow? ANYBODY THERE?   
   //Used for kill and signal command
   $(document).on('click', '.cmd', function(){
       var x = $(this).attr('data-pid');
       alert(x);
       if (confirm('Are you sure?')) {
       $.getJSON(WEBDIR + "stats/command/"+ $(this).attr('data-cmd')+"/" + $(this).attr('data-pid'), function (response) {
            alert(response);
       
       });
        }
   });
   
   // Used for popen
    $(document).on('click', '#sendcmd', function(){
        var i = $('#cmdinput').val()
        $('#shellres').append('<b>' + i + '</b>\n')
       $.get(WEBDIR + "stats/cmdpopen/"+ $(this).attr('data-cmd')+"/" + i, function (response) {
            //alert(response);
            $('#shellres').append(response)
       
       });
   });

    $(document).on('click', '#clearhistory', function(){
            $('#shellres').empty()
   });



// Loads the moduleinfo
$(document).ready(function () {
    $('.spinner').show();
    get_diskinfo();
    get_diskinfo2();
    reloadtab();
    uptime();
    get_user();
    processes();
    get_external_ip();
    get_local_ip();
    network_usage_table();
    sys_info();
    return_settings3();
});

setInterval(function () {
    get_diskinfo();
    get_diskinfo2();
    sys_info();
    processes();
}, 10000);
setInterval(function () {
//    get_diskinfo();
//    get_diskinfo2();
//    uptime();
//    get_user();
//    get_external_ip(); // dont want to spam a external service.
//    get_local_ip();
//    network_usage_table();
//    sys_info();
    return_settings3();
}, 2000);


