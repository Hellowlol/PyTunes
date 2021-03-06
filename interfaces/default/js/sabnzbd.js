$(document).ready(function () {
    $(window).trigger('hashchange');
    $('#nzb_pause_button').click(function () {
        var clickItem = $(this);
        clickItem.button('loading');
        $.ajax({
            url: WEBDIR + 'sabnzbd/TogglePause?mode=' + queueToggleStatusAction,
            dataType: 'json',
            type: 'get'
        });
    });


    $('#add_nzb_form').ajaxForm({
        url: WEBDIR + 'sabnzbd/AddNzbFromUrl',
        type: 'post',
        dataType: 'json',
        success: function (result) {
            if (result.status !== undefined && result.status) {
                $('[href=#active]').trigger('click');
                $('#nzb_url').val('');
                $('#nzb_category').val('');
            }
        }
    });

    setCategories('#nzb_category', 'Default');

    $('#nzb_set_speed').click(function () {
        var speed = ($('#nzb_get_speed').val());
        $.ajax({
            url: WEBDIR + 'sabnzbd/SetSpeed?speed=' + speed,
            type: 'post',
            dataType: 'json'
        });
    });
    loadQueue(1);
    setInterval(function () {
        loadQueue(0);
    }, 60000);
    loadHistory();
    loadWarnings();
});


$(function () {
    var name = $("#name"),
        email = $("#email"),
        password = $("#password"),
        allFields = $([]).add(name).add(email).add(password),
        tips = $(".validateTips");
    $("#dialog-form").dialog({
        autoOpen: false,
        height: 375,
        width: 450,
        modal: true,
        buttons: {
            Cancel: function () {
                $(this).dialog("close");
            }
        },
        close: function () {
            allFields.val("").removeClass("ui-state-error");
        }
    });
    $("#add-nzb")
        .button()
        .click(function () {
        $("#dialog-form").dialog("open");
    });
});

function removeHistoryItem(id) {
    if (confirm("Are you sure?")) {
        $.ajax({
            url: WEBDIR + 'sabnzbd/DeleteHistory?id=' + id,
            type: 'get',
            dataType: 'json',
            success: function (data) {
                loadQueue(1);
                loadHistory();
            }
        });
    }
}


function retryHistoryItem(id) {
    if (confirm('Are you sure retry?')) {
        $.ajax({
            url: WEBDIR + 'sabnzbd/Retry?id=' + id,
            type: 'get',
            dataType: 'json',
            success: function (data) {
                loadQueue(1);
                loadHistory();
            }
        });
    }
}


function loadHistory() {
    $.ajax({
        url: WEBDIR + 'sabnzbd/GetHistory?limit=20',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            if (data.status === false) {
                $('#notification_area').addClass('alert alert-error');
                $('#notification_area').html('<strong>Error</strong> Could not connect to SABnzbd, go to <a href="' + WEBDIR + 'settings">settings</a>');
                return false;
            }
            $('#history_table_body').html('');
            $.each(data.history.slots, function (i, slot) {
                var deleteImage = makeIcon('icon-remove', 'Delete');
                deleteImage.click(function () {
                    removeHistoryItem(slot.nzo_id);
                });

                var retryImage = null;
                if (slot.status == 'Failed') {
                    retryImage = makeIcon('icon-repeat', 'Retry');
                    retryImage.click(function () {
                        retryHistoryItem(slot.nzo_id);
                    });
                }

                var failMessage = $('<span>');
                failMessage.addClass('label');
                failMessage.addClass('label-important');
                failMessage.html(slot.fail_message);

                var row = $('<tr>');

                var name = $('<td>').html(slot.name);
                if (slot.category != '*') {
                    name.append('&nbsp;').append(sabnzbdStatusLabel(slot.category));
                }
                if (slot.status == 'Failed') {
                    $(name).append('&nbsp;').append(failMessage);
                }

                row.append(name);
                row.append($('<td>').append(sabnzbdStatusLabel(slot.status)));
                row.append($('<td>').html(slot.size));
                row.append($('<td>').append(deleteImage));
                row.append($('<td>').append(retryImage));

                $('#history_table_body').append(row);
            });
        }
    });
}



function removeQueueItem(id) {
    if (confirm('Are you want to remove ' + id + ' from queue?')) {
        $.ajax({
            url: WEBDIR + 'sabnzbd/DeleteNzb?id=' + id,
            type: 'get',
            dataType: 'json',
            success: function (data) {
                loadQueue(1);
                loadHistory();
            }
        });
    }
}

function changeCategory(id, cat) {
    $.ajax({
        url: WEBDIR + 'sabnzbd/ChangeCategory?id=' + id + '&cat=' + cat,
        type: 'get',
        dataType: 'json'
    });
}

var queueToggleStatusAction = '';


function loadQueue(once) {
    $.ajax({
        url: WEBDIR + 'sabnzbd/GetStatus',
        type: 'get',
        dataType: 'json',
        success: function (object) {
            if (object.status === false) {
                $('#notification_area').addClass('alert alert-error');
                $('#notification_area').html('<strong>Error</strong> Could not connect to SABnzbd, go to <a href="' + WEBDIR + 'settings">settings</a>');
                return false;
            }
            data = object.queue;
            if (once == 1) {
                $('#nzb_get_speed').val(data.speedlimit);
            }

            $('#nzb_pause_button').button('reset');
            if (data.status == 'Paused') {
                $('#nzb_pause_button').html('<i class="icon-play icon-white"></i> <font color="white">Resume</font>');
                queueToggleStatusAction = 'resume';
            } else {
                $('#nzb_pause_button').html('<i class="icon-pause icon-white"></i> <font color="white">Pause</font>');
                queueToggleStatusAction = 'pause';
            }

            var state = data.status.toLowerCase();
            var formattedState = state.charAt(0).toUpperCase() + state.slice(1);

            $('#queue_state').html(formattedState + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
            $('#queue_speed').html(data.speed + 'B/Sec&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
            $('#eta').html(data.eta + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp');
            $('#load_avg').html(data.loadavg);
            $('#remaining').html(data.mbleft + ' MB&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
            $('#total_disk_space_1').html(data.diskspacetotal1 + ' GB&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
            $('#disk_space_left_1').html(data.diskspace1 + ' GB&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');

            $('#active_table_body').html('');

            if (data.slots.length === 0) {
                var row = $('<tr>');
                row.append($('<td>').html('Queue is empty').attr('colspan', 5));
                $('#active_table_body').append(row);
            }

            $.each(data.slots, function (i, job) {
                var progressBar = $('<div>').addClass('bar').css('width', job.percentage + '%');

                var progress = $('<div>').addClass('progress progress-success').append(progressBar);

                var row = $('<tr>');
                row.append($('<td>').html(job.filename));

                var categories = $('<select>');
                categories.addClass('span1 sab-select');
                categories.change(function () {
                    changeCategory(job.nzo_id, $(this).val());
                });
                setCategories(categories, job.cat);

                row.append($('<td>').html(categories));

                row.append($('<td>').html(progress));
                row.append($('<td>').html(job.timeleft + ' / ' + job.mbleft + 'MB').addClass('span3'));

                var deleteImage = makeIcon('icon-remove', 'Delete');
                deleteImage.attr('alt', 'Remove');
                deleteImage.addClass('close');
                deleteImage.attr('href', '#');
                deleteImage.click(function () {
                    removeQueueItem(job.nzo_id);
                });
                row.append($('<td>').html(deleteImage));

                $('#active_table_body').append(row);
            });
        }
    });
}

function loadWarnings() {
    $.ajax({
        url: WEBDIR + 'sabnzbd/GetWarnings',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            if (data.warnings === 0) {
                var row = $('<tr>');
                row.append($('<td>').html('No warnings'));
                $('#warning_table_body').append(row);
            }
            $.each(data.warnings, function (i, warning) {
                var row = $('<tr>');
                row.append($('<td>').html(warning));
                $('#warning_table_body').append(row);
            });
        }
    });
}

function setCategories(selector, select) {
    $.ajax({
        url: WEBDIR + 'sabnzbd/GetCategories',
        type: 'post',
        dataType: 'json',
        success: function (data) {
            $.each(data.categories, function (i, cat) {
                var option = $('<option>');
                if (select == cat) {
                    option.attr('selected', true);
                }
                option.attr('value', cat);
                option.html(cat);
                $(selector).append(option);
            });
        }
    });
}

function sabnzbdStatusLabel(text) {
    var statusOK = ['Completed'];
    var statusInfo = ['Extracting', 'Running'];
    var statusError = ['Failed'];
    var statusWarning = ['Verifying', 'Repairing'];

    var label = $('<span>').addClass('label').text(text);

    if (statusOK.indexOf(text) != -1) {
        label.addClass('label-success');
    } else if (statusInfo.indexOf(text) != -1) {
        label.addClass('label-info');
    } else if (statusError.indexOf(text) != -1) {
        label.addClass('label-important');
    } else if (statusWarning.indexOf(text) != -1) {
        label.addClass('label-warning');
    }

    var icon = sabnzbdStatusIcon(text, true);
    if (icon !== '') {
        label.prepend(' ').prepend(icon);
    }
    return label;
}

function sabnzbdStatusIcon(iconText, white) {
    var text = [
        'Completed',
        'Extracting',
        'Running',
        'Verifying',
        'Failed',
        'Repairing'];
    var icons = [
        'icon-ok',
        'icon-share',
        'icon-play-circle',
        'icon-exchange',
        'icon-remove',
        'icon-wrench'];

    if (text.indexOf(iconText) != -1) {
        var icon = $('<i>').addClass(icons[text.indexOf(iconText)]);
        if (white === true) {
            icon.addClass('icon-white');
        }
        return icon;
    }
    return '';
}
