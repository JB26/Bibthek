function load_book(book_id){
  $.getJSON( "/books", {book_id:book_id, json_data:"True"},function(data) {
    $.each(data, function(input_id, input_value){
      if ($.isArray(input_value)) {
        $('#' + input_id).val(input_value.join(" & "));
      } else {
        $('#' + input_id).val(input_value);
      };
    });
    $('#cover').attr('src', '/static/' + data.front);
    $('#book_form').attr('action', '/save/?book_id=' + data._id);
    $('#delete').attr('href', '/delete/?book_id=' + data._id);
    $('#delete').show();
    $('#isbn_search').hide();
    $('#reading_stats > tbody tr').remove();
    for (i = 0; i < data.reading_stats.length; i++) {
      build_reading_stats({start: data.reading_stats[i]['start_date'], finish: data.reading_stats[i]['finish_date'], abdoned : data.reading_stats[i]['abdoned']}, i+1);
    }
    if (data.type == 'comic') {$('.comic').show()} else {$('.comic').hide()};
  });
  goodreads_id(book_id, '_id');
};

function build_reading_stats(data, i) {
  var status = '';
  if (data.abdoned == true) { status = 'checked' };
  $('#reading_stats > tbody:last').append(
    '<tr>\
     <th scope="row">' + i + '</th>\
     <td>\
       <div class="form-group">\
         <label for="start_' + i + '" class="col-sm-4 control-label">Started</label>\
         <div class="col-sm-8">\
           <input class="form-control" type="text" name="start_date" id="start_' + i + '" value="' + data.start + '">\
         </div>\
       </div>\
       <div class="form-group">\
         <label for="finish_' + i + '" class="col-sm-4 control-label">Finished</label>\
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
  $('#goodreads').hide();
  $('#delete').hide();
  $.getJSON( "/books", {json_data:"True"},function(data) {
    $.each(data,function(input_id, input_value){
      $('#' + input_id).val(input_value)
    });
    $('#cover').attr('src', '/static/icons/circle-x.svg');
    $('#book_form').attr('action', '/save/?book_id=new_book');
    $('#isbn_search').show();
    $('#reading_stats > tbody tr').remove();
  });
};

function isbn_book(isbn){
  $.getJSON( "/new_isbn", {isbn:isbn},function(data) {
    $.each(data,function(input_id, input_value){
      $('#' + input_id).val(input_value)
    });
    $('#isbn_search').show();
  });
  goodreads_id(isbn, 'isbn');
  $('#isbn_image').attr('href', 'https://www.google.de/search?q=' + isbn + '&tbm=isch');
  $('#amazon').attr('href', 'https://www.amazon.de/gp/search?keywords=' + isbn);
};

function menu_reload(){
  shelf = window.location.pathname.split("/")
  shelf = shelf[shelf.length - 1]
  if (shelf === undefined) {shelf = ""} else {shelf = "?shelf=" + shelf}
  $.get( "menu" + shelf, function( data ) {
    $( "#menu" ).html( data );
  });
};

function goodreads_id(book_i, type){
  if (book_i != 'new_book') {
    if (type == '_id') {var send = "?book_id=" + book_i} else if (type == 'isbn') {var send = "?isbn=" + book_i};
    $('#goodreads').attr('href','/gr_id' + send);
    $('#goodreads').show();
  };
};

$( '#book_form' ).submit(function( event ) {
  event.preventDefault();
  var $form = $( this ),
  url = $form.attr( "action" ),
  formData = new FormData($(this)[0]);
  $.ajax({
    url: url,
    data: formData,
    cache: false,
    contentType: false,
    processData: false,
    type: 'POST',
    success: function(json_data){
        var data = $.parseJSON(json_data);
        if (data['new'] == true) {window.location.assign(window.location.pathname + "?book_id=" + data['book_id'])
        } else {
        load_book(data['book_id'])};
    }
  });
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

window.onload = function (){
  var book_id = $(' body ').attr('id');
  if (book_id == 'new_book') {
    history.replaceState(book_id, '', window.location.pathname);
  } else {
    history.replaceState(book_id, '', window.location.pathname + '?book_id=' + book_id)};
  goodreads_id(book_id, '_id');
};

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
  id = $( this ).attr('id');
  status = id.split('_')[1]
  link_number = id.split('_')[0]
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
});
