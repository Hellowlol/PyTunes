$(document).ready(function () {
    var fileBrowserDialog, currentBrowserPath, currentRequest = null;
    $(window).trigger('hashchange')
    $('.btn-test').click(function(e) {
        e.preventDefault();
        var btn = $(this).button('loading');
        var action = btn.attr('data-target');
        var data = btn.parents('form:first').serialize();
        $.post(action, data, function(data) {
            btn.button('reset');
            if (data != null) {
                btn.addClass('btn-success').append(' ').append($('<i>').addClass('icon-white icon-ok'));
                if (data['Network.MacAddress'] && data['Network.MacAddress'] != 'Busy') {
                   $('#xbmc_server_mac:visible').val(data['Network.MacAddress']);
                }
            } else {
                btn.addClass('btn-danger').append(' ').append($('<i>').addClass('icon-white icon-exclamation-sign'));
            }
        }).error(function(){
            btn.button('reset');
            btn.addClass('btn-danger').append(' ').append($('<i>').addClass('icon-white icon-exclamation-sign'));
        });
    });
    $('input, radio, select, button').bind('change input', function(e) {
        $('.btn-test').button('reset').removeClass('btn-success btn-danger');
    });
    $('.fileBrowser').click(function(e) {
        //if (!fileBrowserDialog) {
        var initialDir = document.getElementById($(this).attr('data-target')).value
        //var initialDir = 'BIG TEST';
            fileBrowserDialog = $('<div id="fileBrowserDialog" style="display:hidden"></div>').appendTo('body').dialog({
                dialogClass: 'browserDialog',
                title:       'Select ' + $(this).attr('title'),
                position:    ['center', 40],
                minWidth:    Math.min($(document).width() - 80, 650),
                height:      Math.min($(document).height() - 80, $(window).height() - 80),
                maxHeight:   Math.min($(document).height() - 80, $(window).height() - 80),
                maxWidth:    $(document).width() - 80,
                modal:       true,
                autoOpen:    true
            });
        //}

        fileBrowserDialog.dialog('option', 'buttons', [
                    {
                        text: "Ok",
                        "class": "btn btn-primary",
                        click: function() {
                            // store the browsed path to the associated text field
                            callback(currentBrowserPath, options);
                            $(this).dialog("close");
                        }
                    },
                    {
                        text: "Cancel",
                        "class": "btn",
                        click: function() {
                            $(this).dialog("close");
                        }
                    }
        ]);
        $('<h2>').text(initialDir).appendTo(fileBrowserDialog);
                link = $("<a href='javascript:void(0)' />").click(function () { browse(entry.path, endpoint); }).html('<big> ..</big>');
                $('<span class="icon icon-folder-close-alt icon-large"></span>').prependTo(link);
                link.hover(
                    function () {$("span", this).addClass("icon-folder-open-alt");    },
                    function () {$("span", this).removeClass("icon-folder-open-alt"); }
                );
                link.appendTo(fileBrowserDialog);
    });


    $('form').submit(function(e) {
        e.preventDefault();
        var action = $(this).attr('action')
        if (action === undefined) action = '';
        var data = $(this).serialize();
        $(this).find("input:checkbox:not(:checked)").each(function(e){
            data+='&'+$(this).attr('name')+'=0';
        });
        $.post(action, data, function(data) {
            msg = data ? 'Save successful' : 'Save failed';
            notify('Settings', msg, 'info');
            if ($('#xbmc_server_id').is(":visible")) {
                xbmc_update_servers(0);
                this.reset();
            }
        });
    });
    $('input.enable-module').change(function() {
        var disabled = !$(this).is(':checked');
        $(this).parents('fieldset:first').find('input, radio, select').not(this)
            .attr('readonly', disabled).attr('disabled', disabled);
    });
    $('input.enable-module').trigger('change')
    $('#xbmc_server_id').change(function() {
        $('button:reset:visible').html('Clear').removeClass('btn-danger').unbind();
        var item = $(this)
        var id = item.val()
        if (id == 0) $('button:reset:visible').trigger('click')
        $.get(WEBDIR + 'xbmc/getserver?id='+id, function(data) {
            if (data==null) return
            $('#xbmc_server_name').val(data.name);
            $('#xbmc_server_host').val(data.host);
            $('#xbmc_server_port').val(data.port);
            $('#xbmc_server_username').val(data.username);
            $('#xbmc_server_password').val(data.password);
            $('#xbmc_server_mac').val(data.mac);
            $("button:reset:visible").html('Delete').addClass('btn-danger').click(function(e) {
                var name = item.find('option:selected').text();
                if (!confirm('Delete ' + name)) return;
                $.get(WEBDIR + 'xbmc/delserver?id='+id, function(data) {
                    notify('Settings', 'Server deleted', 'info')
                    $(this).val(0)
                    item.find('option[value='+ id +']').remove()
                    $('button:reset:visible').html('Clear').removeClass('btn-danger').unbind();
                });
            });
        });
    });
    xbmc_update_servers(0);
});

function xbmc_update_servers(id) {
    $.get(WEBDIR + 'xbmc/getserver', function(data) {
        if (data==null) return;
        var servers = $('#xbmc_server_id').empty().append($('<option>').text('New').val(0));
        $.each(data.servers, function(i, item) {
            var option = $('<option>').text(item.name).val(item.id);
            if (id == item.id) option.attr('selected', 'selected');
            servers.append(option);
        });
    }, 'json');
}