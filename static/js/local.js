function load_book(book_id){
  var view_user = window.location.pathname.split("/")[2]
  $.getJSON( "/json_book/" + view_user, {book_id:book_id}, function(data) {
    $.each(data, function(input_id, input_value){
      if ($.isArray(input_value)) {
        $('#' + input_id).val(input_value.join(" & "));
      } else if (input_id == 'form') {
        $('#' + input_value).prop("checked", true);
      } else {
        $('#' + input_id).val(input_value);
      };
    });
    $('#cover').attr('src', '/' + data.front);
    $('#book_form').attr('action', '/save/?book_id=' + data._id);
    $('#delete').attr('href', '/delete/?book_id=' + data._id);
    $('#delete').show();
    $('#isbn_search').hide();
    $('#reading_stats > tbody tr').remove();
    if (data.reading_stats != null) {
      for (i = 0; i < data.reading_stats.length; i++) {
      build_reading_stats({start: data.reading_stats[i]['start_date'], finish: data.reading_stats[i]['finish_date'], abdoned : data.reading_stats[i]['abdoned']}, i+1);
      }
    }
    if (data.type == 'comic') {
      $('.comic').show()} else {$('.comic').hide()
    };
    search_links(data.isbn);
  })
  .fail(function() {
    window.location.href = '/';
  });
};

function build_reading_stats(data, i) {
  var status = '';
  data.start = data.start.replace(/"/g, '&quot;');
  data.finish = data.finish.replace(/"/g, '&quot;');
  if (data.abdoned == true) { status = 'checked' };
  $('#reading_stats > tbody:last').append(
    '<tr>\
     <th scope="row">' + i + '</th>\
     <td>\
       <div class="form-group">\
         <label for="start_' + i + '" class="col-sm-4 control-label date_js" id="start_' + i + '-label">Started</label>\
         <div class="col-sm-8">\
           <input class="form-control" type="text" name="start_date" id="start_' + i + '" value="' + data.start + '">\
         </div>\
       </div>\
       <div class="form-group">\
         <label for="finish_' + i + '" class="col-sm-4 control-label date_js" id="finish_' + i + '-label">Finished</label>\
         <div class="col-sm-8">\
           <input class="form-control" type="text" name="finish_date" id="finish_' + i + '" value="' + data.finish + '">\
         </div>\
       </div>\
     </td>\
     <td>\
       <div class="checkbox">\
         <label>\
         <input type="checkbox" name="abdoned" value="' + (i-1) + '" ' + status + '> Abdoned\
         </label>\
       </div>\
     </td>\
   </tr>'
  );
}

function empty_book(){
  $('#delete').hide();
  $.getJSON( "/json_book", {book_id:'new_book'},function(data) {
    $.each(data,function(input_id, input_value){
      $('#' + input_id).val(input_value)
    });
    $('#cover').attr('src', '/static/icons/circle-x.svg');
    $('#book_form').attr('action', '/save/?book_id=new_book');
    $('#isbn_search').show();
    $('#reading_stats > tbody tr').remove();
  })
  .fail(function() {
    window.location.href = '/';
  });
};

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

function menu_reload(){
  shelf = window.location.pathname.split("/")
  shelf = shelf[shelf.length - 1]
  if (shelf === undefined) {shelf = ""} else {shelf = "?shelf=" + shelf}
  $.get( "menu" + shelf, function( data ) {
    $( "#menu" ).html( data );
  });
};

function search_links(isbn){
  var send = "?isbn=" + isbn;
  $('#isbn_image').attr('href','https://www.google.de/search?q=' + isbn + '&tbm=isch');
  $('#goodreads').attr('href','https://www.goodreads.com/search?utf8=%E2%9C%93&query=' + isbn);
  $('#amazon').attr('href','https://www.amazon.de/gp/search?keywords=' + isbn);
};

$( '#book_form' ).submit(function( event ) {
  $.localStorage.set({"scroll_book" : $(window).scrollTop(), "scroll_navmenu" : $('.navmenu').scrollTop()});
});

$('.series_pencil').click(function(event) {
  if (window.location.pathname.split('/')[5] == 'series') {
    var edit = 'series'; 
  } else if (window.location.pathname.split('/')[5] == 'author') {
    var edit = 'authors';
  } else {
    return
  };
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

$('.sidebar').on( "click", ".batch_edit", function() {
  $.localStorage.set({"scroll_book" : $(window).scrollTop(), "scroll_navmenu" : $('.navmenu').scrollTop()});
});

$('.show-toggle').click(function(event) {
  event.preventDefault();
  var idx = $( this ).attr('id').split("_")[0];
  $('#' + idx + '_ul').toggle();
  var name_key = $('#' + idx + '_ul').data('name')
  if ( $('#' + idx + '_ul').is(":visible") ) {
    $.localStorage.set(name_key, 'true');
  } else {
    $.localStorage.remove(name_key);
  };
});

$('#delete').click(function(event) {
  event.preventDefault();
  var book_id = $(' body ').attr('id');
  warning("danger", 'Do you really want to delete this book? <a href="/delete?book_id=' + book_id + '" class="alert-link" id="delete_now">YES!</a> ');
});

$( '.book_title' ).click(function( event ) {
  event.preventDefault();
  var book_id = $(this).attr('id');
  history.pushState(book_id, '', window.location.pathname + '?book_id=' + book_id);
  load_book(book_id, '_id');
});

/*
$('#link_new_book').click(function( event ) {
  event.preventDefault();
  empty_book();
  history.pushState('new_book', '', '/');
});
*/

window.addEventListener('popstate', function(event){
  var book_id = event.state;
  if (book_id == 'new_book') {
    empty_book();
  } else {
    load_book(book_id)};
});



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
