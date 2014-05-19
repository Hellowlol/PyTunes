/**
 * Converts bytes to readable filesize in kb, MB, GB etc.
 */

// For hdd.
function getReadableFileSizeStringHDD(fileSizeInBytes) {
    var i = -1;
    var byteUnits = [' kB', ' MB', ' GB', ' TB', ' PB'];
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
            //alert(response);
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
                $('<td>').addClass('stats_name').text(disk.mountpoint),
                $('<td>').addClass('stats_name').text(disk.device),
                $('<td>').addClass('stats_name').text(disk.fstype),
                $('<td>').addClass('stats_ratio').text(getReadableFileSizeStringHDD(disk.free)),
                $('<td>').addClass('qbit_eta').text(getReadableFileSizeStringHDD(disk.used)),
                $('<td>').addClass('stats_state').text(getReadableFileSizeStringHDD(disk.total)),
                //$('<td>').addClass('span3 qbit_progress').html(progress2),
                $('<td>').addClass('stats_state').text(disk.percent));
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
                $('<td>').addClass('stats_name').text(disk.mountpoint),
                $('<td>').addClass('stats_name').text(disk.device),
                $('<td>').addClass('stats_name').text(disk.fstype),
                $('<td>').addClass('stats_ratio').text(getReadableFileSizeStringHDD(disk.free)),
                $('<td>').addClass('stats_eta').text(getReadableFileSizeStringHDD(disk.used)),
                $('<td>').addClass('stats_state').text(getReadableFileSizeStringHDD(disk.total)),
                $('<td>').addClass('span3 qbit_progress').html(progress2),
                $('<td>').addClass('stats_state').text(disk.percent));
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
        $(".txip").text(response.externalip);

    });
}

function get_local_ip() {
    $.getJSON(WEBDIR + "stats/get_local_ip", function (response) {
        $(".tlip").text(response.localip);

    });
}

function network_usage() {
    $.getJSON(WEBDIR + "stats/network_usage", function (response) {
        //alert(response);
        $("#stat-sent").text(getReadableFileSizeString(response.bytes_sent));
        $("#stat-recv").text(getReadableFileSizeString(response.bytes_recv));
        $("#errin").text(response.errin);
        $("#errout").text(response.errout);
        $("#dropin").text(response.dropin);
        $("#dropout").text(response.dropout);
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

function virtual_memory() {
    $.getJSON(WEBDIR + "stats/virtual_memory", function (virtual) {
        $('#vperc').text(virtual.percent + "%");
        $('#vtot').text(getReadableFileSizeString(virtual.total));
        $('#vused').text(getReadableFileSizeString(virtual.total - virtual.available));
        $('#vfree').text(getReadableFileSizeString(virtual.available));
    });
}

function swap_memory() {
    $.getJSON(WEBDIR + "stats/swap_memory", function (swap) {
        //alert(response.total);
        $('#stot').text(getReadableFileSizeString(swap.total));
        $('#sfree').text(getReadableFileSizeString(swap.free));
        $('#sused').text(getReadableFileSizeString(swap.used));
        $('#sperc').text(swap.percent + '%');
    });
}

function cpu_percent() {
    $.getJSON(WEBDIR + "stats/cpu_percent", function (cpu) {
        $('#cuser').text(cpu.user + '%');
        $('#cidle').text(cpu.idle + '%');
        $('#csys').text(cpu.system +'%');
        $("#cpu").text((100 - cpu.idle).toFixed(1) + '%');
    });
}

function return_settings() {
    $.getJSON(WEBDIR + "stats/return_settings", function (return_settings) {
        if (return_settings.stats_use_bars == 'true') {
            cpu_percent_bar();
            swap_memory_bar();
            virtual_memory_bar();
        } else if (return_settings.stats_use_bars == 'false') {
            //cpu_percent_nobar();
            cpu_percent();
            //swap_memory_nobar();
            swap_memory();
            //virtual_memory_nobar();
            virtual_memory();

        } else {
            //pass 
        }
    });
}

function processes() {
    $.ajax({
        'url': WEBDIR + 'stats/processes',
            'dataType': 'html',
            'success': function (response) {
            $('#proc-table').append(response);
            $('.show_proc').click(function () {
                alert('PID: ' + $(this).attr('data-pid'));
                showProcess($(this).attr('data-pid'));
            });
            $('.cmd').click(function () {
                alert('PID: ' + $(this).attr('data-pid'));
                if (confirm('Are you sure?')) {
                    $.getJSON(WEBDIR + "stats/command/" + $(this).attr('data-cmd') + "/" + $(this).attr('data-pid'), function (response) {
                        alert(response);
                    });
                }
            });
            $('.show-proc').click(function (e) {
                //alert('PID: ' + $(this).attr('data-pid'));
                e.preventDefault();
                showProcess($(this).attr('data-pid'))
            });
            $('.spinner').hide();
        }
    });
}

function showProcess(pid) {
    //alert('show process ' + pid);
    var sendData = {
        'pid': pid
    };
    $.ajax({
        url: WEBDIR + "stats/ShowProcess",
        type: 'get',
        data: sendData,
        dataType: 'json',
        success: function (data) {
            //alert(data);
            $('#modal_stats .modal-h3-stats').html(data.head);
            $('#modal_stats .modal-body-stats').html(data.body);
            $('#modal_stats .modal-footer-stats').html(data.foot);

            $('#modal_stats').modal({
                show: true,
                backdrop: false
            });
        }
    });
}


function loadtabs() {
    if ($('#summary_tab').is(':visible')) {
        get_diskinfo2();
        uptime();
        get_user();
        cpu_percent();
        swap_memory();
        virtual_memory();
        get_external_ip();
        get_local_ip();
        network_usage();
        sys_info();
    } 
    else if ($('#filesystems_tab').is(':visible')) {
        disk_info();
    }
    else if ($('#processes_tab').is(':visible')) {
        processes();
    }
}

   $('#summary_tab').click(function () {
        get_diskinfo2();
        uptime();
        get_user();
        cpu_percent();
        swap_memory();
        virtual_memory();
        get_external_ip();
        get_local_ip();
        network_usage();
        sys_info();
   });
   $('#filesystems_tab').click(function () {
       get_diskinfo();
   });
    $('#processes_tab').click(function () {
       processes();
   });

   // Used for popen
    $(document).on('click', '#sendcmd', function(){
        var i = $('#cmdinput').val();
        $('#shellres').append('<b>' + i + '</b>\n')
       $.get(WEBDIR + "stats/cmdpopen/"+ $(this).attr('data-cmd')+"/" + i, function (response) {
            $('#shellres').append(response);
            document.getElementById("cmdinput").value = "";
       
       });
   });

    $(document).on('click', '#clearhistory', function(){
            $('#shellres').empty();
   });



// Loads the moduleinfo
$(document).ready(function () {
    $('.spinner').show();
    //get_diskinfo();
    //get_diskinfo2();
    loadtabs();
    //uptime();
    //get_user();
    //cpu_percent();
    //swap_memory();
    //virtual_memory();
    //processes();
    //get_external_ip();
    //get_local_ip();
    //network_usage();
    //sys_info();
    //return_settings();
});

setInterval(function () {
    //get_diskinfo();
    //get_diskinfo2();
    //sys_info();
    //processes();
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
//    return_settings3();
}, 2000);


