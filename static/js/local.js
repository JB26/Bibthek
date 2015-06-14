function isbn_book(isbn){
  $.getJSON( "/new_isbn", {isbn:isbn}, function(data) {
    $.each(data,function(input_id, input_value){
      $('#' + input_id).val(input_value)
    });
    $('#isbn_search').show();
    search_links(isbn);
    $('#isbn_image').attr('href', 'https://www.google.de/search?q=' + isbn + '&tbm=isch');
    $('#amazon').attr('href', 'https://www.amazon.de/gp/search?keywords=' + isbn);
  })
  .fail(function() {
    window.location.href = '/';
  });
};

function search_links(isbn){
  var send = "?isbn=" + isbn;
  $('#isbn_image').attr('href','https://www.google.de/search?q=' + isbn + '&tbm=isch');
  $('#goodreads').attr('href','https://www.goodreads.com/search?utf8=%E2%9C%93&query=' + isbn);
  $('#amazon').attr('href','https://www.amazon.de/gp/search?keywords=' + isbn);
};

function save_state(){
  $.localStorage.set({"scroll_book" : $(window).scrollTop(), "scroll_navmenu" : $('.navmenu').scrollTop()});
  $('.sub_items').each(function() {
    var name_key = $( this ).data('name')
    if ( $( this ).is(":visible") ) {
      $.localStorage.set(name_key, 'true');
    } else {
      $.localStorage.remove(name_key);
    }
  });
}

$( '#book_form' ).submit(function( event ) {
  save_state();
});

$('.sidebar').on( "click", ".batch_edit", function() {
  save_state();
});

$('#alert_placeholder').on( "click", '#delete_now', function() {
  save_state();
});

$('.series_pencil').click(function(event) {
  var edit = window.location.pathname.split('/')[5]
  var id = $( this ).attr('id'),
  link_number = id.split('_')[0],
  link_text = $('#' + link_number + '_a').text().replace(/"/g, '&quot;');
  $('#' + link_number + '_star-empty').hide()
  $('#' + link_number + '_star').hide()
  $('#' + link_number + '_pencil').hide()
  $('#' + link_number + '_a').replaceWith(
    '<form class="form-inline" action="/batch_edit/' + edit + '" method="post">\
      <input type="hidden" name="old_name" value="' + link_text + '" />\
      <input style="margin-left: 20px;" class="form-control" value="' + link_text  + '" name="new_name">\
      <button type="submit" class="btn btn-sm btn-default batch_edit">OK</button>\
    </form>'
  );
});

$('.show-toggle').click(function(event) {
  event.preventDefault();
  var idx = $( this ).attr('id').split("_")[0];
  $('#' + idx + '_ul').toggle();
});

$( '.book_title' ).click(function( event ) {
  save_state();
  $('.alert').alert('close');
});

function build_reading_stats(data, i) {
  var view_user = window.location.pathname.split("/")[2]
  $.get( "/reading_stats" , {'i' : i, 'start' : data.start, 'finish' : data.finish, 'abdoned' : data.abdoned},  function( data ) {
    $('#reading_stats > tbody:last').append(data);
  });
};

$('#reading_stats').on( "click", ".date_js", function() {
  var d = new Date();
  var time = d.toISOString().split('T')[0];
  var input_id = $( this ).attr('id').split('-')[0]
  $('#' + input_id).val(time);
});

$('#isbn_search').click(function(event) {
  event.preventDefault();
  isbn_book($('#isbn').val());  
});

$('#start_reading').click(function(event) {
  event.preventDefault();
  var rowCount = $('#reading_stats > tbody tr').length;
  build_reading_stats({start: '', finish: '', abdoned: false}, rowCount+1);
});

$('#delete_reading').click(function(event) {
  event.preventDefault();
  $('#reading_stats > tbody tr:last').remove();
});

$('.series_star').click(function(event) {
  var id = $( this ).attr('id'),
  status = id.split('_')[1],
  link_number = id.split('_')[0];
  if ($( this ).css("cursor") == "pointer") {
    $.get( "/star_series?series=" + $('#' + link_number + '_a').text() + "&status=" + status, function( data ) {
      if (data == '0') {
        $('#' + id).toggleClass('glyphicon-star-empty glyphicon-star');
        if (status == 'star') {
          $('#' + id).attr('id', link_number + '_star-empty');
        } else {
          $('#' + id).attr('id', link_number + '_star');
        };
      };
    });
  };
});
