$(document).ready(function () {
    var showid = $('div.page-title').attr('data-showid');
    loadShowData(showid);

    $('#banner').css('background-image', 'url(' + WEBDIR + 'sickrage/GetBanner/' + showid + ')');

    $("#ckbCheckAll").click(function () {
        $(".checkBoxClass").prop('checked', $(this).prop('checked'));
    });
    $("form").submit(function (e) {
        e.preventDefault();
        //var data = $("#statusform").serialize();
        alert($("form").serialize());
    });
});

function loadShowData(showid){
  $.ajax({
    url: WEBDIR + 'sickrage/GetShow?indexerid=' + showid,
    type: 'get',
    dataType: 'json',
    success: function(data){
      if (data.result != 'success') {
        notify('Error', 'Show not found: ' + showid, 'error');
        return;
      }
      data = data.data;
      $('.sickrage_showname').text(data.show_name);
      $('.sickrage_status').append(sickrageStatusLabel(data.status));
      $('.sickrage_network').text(data.network);
      $('.sickrage_location').text(data.location);
      $('.sickrage_airs').text(data.airs);
      if (data.next_ep_airdate != '') {
        $('.sickrage_next_air').text(data.next_ep_airdate);
      }

      var menu = $('.show-options-menu')
      $('.rescan-files', menu).click(function(evt) {
        evt.preventDefault();
        rescanFiles(showid, data.show_name);
      });

      $('.full-update', menu).click(function(evt) {
        evt.preventDefault();
        forceFullUpdate(showid, data.show_name);
      });

      $('.remove-show', menu).click(function(evt) {
        evt.preventDefault();
        removeShow(showid, data.show_name);
      });

      renderSeasonTabs(showid, data.season_list);
    },
    error: function(){
        notify('Error', 'Error while loading show.', 'error');
    }
  });
}

function renderSeasonTabs(showid, seasons){
  list = $('#season-list');
  list.html('');

  $.each(seasons, function(index, seasonNr){
    var label = seasonNr;

    // Specials are marked as season 0
    if (label == 0) {
      label = 'Specials';
    }
    var pill = $('<li>').append(
      $('<a>')
        .text(label)
        .attr('href', '#'+seasonNr)
        .attr('data-season', seasonNr)
        .attr('data-showid', showid)
    );

    list.append(pill);
  });
  list.find('a').on('click', renderSeason);

  // Trigger latest season
 list.find('li:first-child a').trigger('click');
}


function renderSeason(){
  $('.spinner').show();
  $('#season-list li').removeClass('active');
  $(this).parent().addClass("active");

  showid = $(this).attr('data-showid');
  season = $(this).attr('data-season');

  $.ajax({
    url: WEBDIR + 'sickrage/GetSeason?indexerid=' + showid + '&season=' + season,
    type: 'get',
    dataType: 'json',
    success: function(data){
      $("#ckbCheckAll").prop('checked', false);
      var seasonContent = $('#season-content');
      seasonContent.html(''); // Clear table contents before inserting new rows

      // If result is not 'succes' it must be a failure
      if (data.result != 'success') {
        notifyError('Error', 'This is not a valid season for this show');
        return;
      }

      // Loop through data
      $.each(data.data, function(index, value){
        var row = $('<tr>');

        var search_link = $('<a>').addClass('btn btn-mini').attr('title', 'Search new download').append($('<i>').addClass('icon-search')).on('click', function(){
          searchEpisode(showid, season, index, value.name);
        });

        var checkbox = $('<input>').addClass('checkBoxClass').attr('type', 'checkbox').attr('name', 'changestatus').attr('value', showid +'|' + season + '|' + index);

        row.append(
          $('<td>').html(checkbox),
          $('<td>').text(index),
          $('<td>').text(value.name),
          $('<td>').text(value.airdate),
          $('<td>').append(sickrageStatusLabel(value.status)),
          $('<td>').text(value.quality),
          $('<td>').append(search_link)
        );
        seasonContent.append(row);
      }); // end loop

      // Trigger tableSort update
      seasonContent.parent().trigger("update");
      seasonContent.parent().trigger("sorton",[[[0,1]]]);
    },
    error: function(){
        notify('Error', 'Error while loading season.', 'error');
    }
  });
  $('.spinner').hide();
}

function sickrageStatusLabel(text){
  var statusOK = ['Continuing', 'Downloaded', 'HD'];
  var statusInfo = ['Snatched', 'Unaired'];
  var statusError = ['Ended'];
  var statusWarning = ['Skipped'];

  var label = $('<span>').addClass('label').text(text);

  if (statusOK.indexOf(text) != -1) {
    label.addClass('label-success');
  }
  else if (statusInfo.indexOf(text) != -1) {
    label.addClass('label-info');
  }
  else if (statusError.indexOf(text) != -1) {
    label.addClass('label-important');
  }
  else if (statusWarning.indexOf(text) != -1) {
    label.addClass('label-warning');
  }

  var icon = sickrageStatusIcon(text, true);
  if (icon != '') {
    label.prepend(' ').prepend(icon);
  }
  return label;
}

function sickrageStatusIcon(iconText, white){
  var text =[
    'Downloaded',
    'Continuing',
    'Snatched',
    'Unaired',
    'Archived',
    'Skipped'
  ];
  var icons = [
    'icon-download-alt',
    'icon-repeat',
    'icon-share-alt',
    'icon-time',
    'icon-lock',
    'icon-fast-forward'
  ];

  if (text.indexOf(iconText) != -1) {
    var icon = $('<i>').addClass(icons[text.indexOf(iconText)]);
    if (white == true) {
      icon.addClass('icon-white');
    }
    return icon;
  }
  return '';
}

function forceFullUpdate(indexerid, name) {
  var modalcontent = $('<div>');
  modalcontent.append($('<p>').html('Queueing &quot;' + name +' &quot; for full TVDB information update..'));
  modalcontent.append($('<div>').html('<div class="progress progress-striped active"><div class="bar" style="width: 100%;"></div></div>'));
  showModal('Queueing...', modalcontent, {});

  $.ajax({
    url: WEBDIR + 'sickrage/ForceFullUpdate?indexerid=' + indexerid,
    type: 'get',
    dataType: 'json',
    timeout: 15000,
    success: function (data) {
      // If result is not 'succes' it must be a failure
      if (data.result != 'success') {
        notify('Error', data.message, 'error');
        return;
      } else {
        notify('OK', data.message, 'success');
        return;
      }
    },
    error: function (data) {
      notify('Error', 'Unable to queue tv show for full update.', 'error', 1);
    },
    complete: function (data) {
      hideModal();
    }
  });
}

function removeShow(indexerid, name) {
    if (confirm('Are you sure you want to delete ')) {
            $.ajax({
                url: WEBDIR + 'sickrage/RemoveShow?indexerid=' + indexerid,
                type: 'get',
                dataType: 'json',
                timeout: 15000,
                success: function (data) {
                    if (data.result == 'success') {
                        notify('OK', data.message, 'success');
                        return;
                    } else {
                        notify('Error', data.message, 'error');
                        return;
                    }
                },
                error: function (data) {
                    notify('Error', 'Unable to queue tv show for full update.', 'error', 1);
                }
            });

        }
}

function rescanFiles(indexerid, name) {
  var modalcontent = $('<div>');
  modalcontent.append($('<p>').html('Queueing &quot;' + name +' &quot; for files rescan..'));
  modalcontent.append($('<div>').html('<div class="progress progress-striped active"><div class="bar" style="width: 100%;"></div></div>'));
  showModal('Queueing...', modalcontent, {});

  $.ajax({
    url: WEBDIR + 'sickrage/RescanFiles?indexerid=' + indexerid,
    type: 'get',
    dataType: 'json',
    timeout: 15000,
    success: function (data) {
      // If result is not 'succes' it must be a failure
      if (data.result != 'success') {
        notify('Error', data.message, 'error');
        return;
      } else {
        notify('OK', data.message, 'success');
        return;
      }
    },
    error: function (data) {
      notify('Error', 'Unable to queue tv show for files rescan.', 'error', 1);
    },
    complete: function (data) {
      hideModal();
    }
  });
}

function searchEpisode(indexerid, season, episode, name) {
  var modalcontent = $('<div>');
  modalcontent.append($('<p>').html('Looking for episode &quot;'+ name +'&quot;.'));
  modalcontent.append($('<div>').html('<div class="progress progress-striped active"><div class="bar" style="width: 100%;"></div></div>'));
  showModal('Searching episode '+season + 'x'+episode, modalcontent, {});

  $.ajax({
    url: WEBDIR + 'sickrage/SearchEpisodeDownload?indexerid=' + indexerid +'&season=' + season +'&episode='+episode,
    type: 'get',
    dataType: 'json',
    timeout: 40000,
    success: function (data) {
      // If result is not 'succes' it must be a failure
      if (data.result != 'success') {
        notify('Error', data.message, 'error');
        return;
      } else {
        notify('OK', name+ ' ' + season + 'x'+episode+' found. ' + data.message, 'success');
        return;
      }
    },
    error: function (data) {
      notify('Error', 'Episode not found.', 'error', 1);
    },
    complete: function (data) {
      hideModal();
      // Trigger latest season
      $('#season-list li.active a').trigger('click');
    }
  });
}
