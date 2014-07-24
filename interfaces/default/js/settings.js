$(document).ready(function () {
    var fileBrowserDialog, currentBrowserPath, currentRequest = null;
    loadClients();
    $(window).trigger('hashchange');
    $('.btn-test').click(function (e) {
        e.preventDefault();
        var btn = $(this).button('loading');
        var action = btn.attr('data-target');
        var data = btn.parents('form:first').serialize();
        $.post(action, data, function (data) {
            btn.button('reset');
            if ($('#couchpotato_name').is(":visible")) {
                    if (data.success) {
                        $('#couchpotato_apikey').val(data.api_key);
                    } else {
                        notify('Settings', 'Failed to get couchpotato apikey', 'error');
                        btn.addClass('btn-danger').append(' ').append($('<i>').addClass('icon-white icon-exclamation-sign'));
                    }
            }
            if (data !== null) {
                btn.addClass('btn-success').append(' ').append($('<i>').addClass('icon-white icon-ok'));
                if (data['Network.MacAddress'] && data['Network.MacAddress'] != 'Busy') {
                    $('#xbmc_server_mac:visible').val(data['Network.MacAddress']);
                }
            } else {
                btn.addClass('btn-danger').append(' ').append($('<i>').addClass('icon-white icon-exclamation-sign'));
            }
        }).error(function () {
            btn.button('reset');
            btn.addClass('btn-danger').append(' ').append($('<i>').addClass('icon-white icon-exclamation-sign'));
        });
    });
    $('input, radio, select, button').bind('change input', function (e) {
        $('.btn-test').button('reset').removeClass('btn-success btn-danger');
    });
    $('.fileBrowser').click(function (e) {
        //if (!fileBrowserDialog) {
        var initialDir = document.getElementById($(this).attr('data-target')).value;
        //var initialDir = 'BIG TEST';
        fileBrowserDialog = $('<div id="fileBrowserDialog" style="display:hidden"></div>').appendTo('body').dialog({
            dialogClass: 'browserDialog',
            title: 'Select ' + $(this).attr('title'),
            position: ['center', 40],
            minWidth: Math.min($(document).width() - 80, 650),
            height: Math.min($(document).height() - 80, $(window).height() - 80),
            maxHeight: Math.min($(document).height() - 80, $(window).height() - 80),
            maxWidth: $(document).width() - 80,
            modal: true,
            autoOpen: true
        });
        //}

        fileBrowserDialog.dialog('option', 'buttons', [{
            text: "Ok",
                "class": "btn btn-primary",
            click: function () {
                // store the browsed path to the associated text field
                callback(currentBrowserPath, options);
                $(this).dialog("close");
            }
        }, {
            text: "Cancel",
                "class": "btn",
            click: function () {
                $(this).dialog("close");
            }
        }]);
        $('<h2>').text(initialDir).appendTo(fileBrowserDialog);
        link = $("<a href='javascript:void(0)' />").click(function () {
            browse(entry.path, endpoint);
        }).html('<big> ..</big>');
        $('<span class="icon icon-folder-close-alt icon-large"></span>').prependTo(link);
        link.hover(

        function () {
            $("span", this).addClass("icon-folder-open-alt");
        },

        function () {
            $("span", this).removeClass("icon-folder-open-alt");
        });
        link.appendTo(fileBrowserDialog);
    });


    $('form').submit(function (e) {
        e.preventDefault();
        var action = $(this).attr('action');
        if (action === undefined) action = '';
        var data = $(this).serialize();
        $(this).find("input:checkbox:not(:checked)").each(function (e) {
            data += '&' + $(this).attr('name') + '=0';
        });
        $.post(action, data, function (data) {
            msg = data ? 'Save successful' : 'Save failed';
            notify('Settings', msg, 'info');
            if ($('#xbmc_server_id').is(":visible")) {
                xbmc_update_servers(0);
                this.reset();
            }
            if ($('#newznab_server_id').is(":visible")) {
                newznab_update_servers(0);
                this.reset();
            }
        });
    });
    $('input.enable-module').change(function () {
        var disabled = !$(this).is(':checked');
        $(this).parents('fieldset:first').find('input, radio, select').not(this)
            .attr('readonly', disabled).attr('disabled', disabled);
    });
    $('input.enable-module').trigger('change');
    $('#xbmc_server_id').change(function () {
        $('button:reset:visible').html('Clear').removeClass('btn-danger').unbind();
        var item = $(this);
        var id = item.val();
        if (id === 0) $('button:reset:visible').trigger('click');
        $.get(WEBDIR + 'settings/getxbmcserver?id=' + id, function (data) {
            if (data === null) return;
            $('#xbmc_server_name').val(data.name);
            $('#xbmc_server_host').val(data.host);
            $('#xbmc_server_port').val(data.port);
            $('#xbmc_server_username').val(data.username);
            $('#xbmc_server_password').val(data.password);
            $('#xbmc_server_mac').val(data.mac);
            $("button:reset:visible").html('Delete').addClass('btn-danger').click(function (e) {
                var name = item.find('option:selected').text();
                if (!confirm('Delete ' + name)) return;
                $.get(WEBDIR + 'settings/delxbmcserver?id=' + id, function (data) {
                    notify('Settings', 'Server deleted', 'info');

                    $(this).val(0);
                    item.find('option[value=' + id + ']').remove();
                    $('button:reset:visible').html('Clear').removeClass('btn-danger').unbind();
                });
            });
        });
    });
    $('#newznab_server_id').change(function () {
        $('button:reset:visible').html('Clear').removeClass('btn-danger').unbind();
        var item = $(this);
        var id = item.val();
        if (id === 0) $('button:reset:visible').trigger('click');
        $.get(WEBDIR + 'settings/getnewzserver?id=' + id, function (data) {
            if (data === null) return;
            $('#newznab_server_name').val(data.name);
            $('#newznab_server_host').val(data.host);
            $('#newznab_server_apikey').val(data.apikey);
            $('#newznab_server_username').val(data.username);
            $('#newznab_server_password').val(data.password);
            $('#newznab_server_ssl').val(data.ssl);
            $("button:reset:visible").html('Delete').addClass('btn-danger').click(function (e) {
                var name = item.find('option:selected').text();
                if (!confirm('Delete ' + name)) return;
                $.get(WEBDIR + 'settings/delnewzserver?id=' + id, function (data) {
                    notify('Settings', 'Server deleted', 'info');

                    $(this).val(0);
                    item.find('option[value=' + id + ']').remove();
                    $('button:reset:visible').html('Clear').removeClass('btn-danger').unbind();
                });
            });
        });
    });
    xbmc_update_servers(0);
    loadNzbServers();
});

function loadClients() {
    $.ajax({
        url: WEBDIR + 'torrents/GetClients',
        type: 'get',
        dataType: 'text',
        success: function (data) {
            if (data === null) return errorHandler();
            $('#default_torr_id').append(data);
        }
    });
    //For the future
    //$.ajax({
    //    url: WEBDIR + 'newznab/GetClients',
    //    type: 'get',
    //    dataType: 'text',
    //    success: function (data) {
    //        if (data === null) return errorHandler();
    //        $('#default_nzb_id').append(data);
    //    }
    //});
}

function xbmc_update_servers(id) {
    $.get(WEBDIR + 'settings/getxbmcserver', function (data) {
        if (data === null) return;
        var servers = $('#xbmc_server_id').empty().append($('<option>').text('New').val(0));
        $.each(data.servers, function (i, item) {
            var option = $('<option>').text(item.name).val(item.id);
            if (id == item.id) option.attr('selected', 'selected');
            servers.append(option);
        });
    }, 'json');
}

function loadNzbServers() {
    $.ajax({
        url: WEBDIR + 'settings/GetNewzServers',
        type: 'get',
        dataType: 'text',
        success: function (data) {
            if (data === null) return errorHandler();
            $('#newznab_server_id').append(data);
        }
    });
}


$(document).on('click', '.delete_cache', function(e){
    $.ajax({
        'url': WEBDIR + 'settings/delete_cache',
        'dataType': 'json',
        'success': function(response) {
            if (response.success) {
                $('.delete_cache').addClass('btn-success').removeClass('btn-danger');
                notify('Info', 'Cache folder was deleted', 'success', 5);

            } else {
                $('.delete_cache').addClass('btn-danger').removeClass('btn-success');
                notify('Error', 'Failed to delete cache folder', 'error', 5);
            }
        }
    });
});


