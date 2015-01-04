function load_book(book_id){
  $.getJSON( "/book", {book_id:book_id, json_data:"True"},function(data) {
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
  });
  goodreads_id(book_id, '_id');
};

function empty_book(){
  $('#goodreads').hide();
  $('#delete').hide();
  $.getJSON( "/book", {json_data:"True"},function(data) {
    $.each(data,function(input_id, input_value){
      $('#' + input_id).val(input_value)
    });
    $('#cover').attr('src', '/static/icons/circle-x.svg');
    $('#book_form').attr('action', '/save/?book_id=new_book');
    $('#isbn_search').show();
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

function goodreads_id(book_i, type){
  if (book_i != 'new_book') {
    if (type == '_id') {var send = "?book_id=" + book_i} else if (type == 'isbn') {var send = "?isbn=" + book_i};
    $('#goodreads').attr('href','/gr_id' + send);
    $('#goodreads').show();
  };
};

$( '.drop_down' ).click(function () {
  var series_hash = $(this).attr('id');
  $('#show_' + series_hash).toggle();
});

$( '#book_form' ).submit(function( event ) {
  event.preventDefault();
  var $form = $( this ),
  url = $form.attr( "action" ),
  term = $form.serializeArray();
  $.post( url, term );
});

$( '.book_title' ).click(function( event ) {
  event.preventDefault();
  var book_id = $(this).attr('id');
  history.pushState(book_id, '', '/book?book_id=' + book_id);
  load_book(book_id, '_id');
});

$('#link_new_book').click(function( event ) {
  event.preventDefault();
  empty_book();
  history.pushState('new_book', '', '/');
});

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
    history.replaceState(book_id, '', window.location);
  } else {
    history.replaceState(book_id, '', '/book?book_id=' + book_id)};
  goodreads_id(book_id, '_id');
};

$('#isbn_search').click(function(event) {
  event.preventDefault();
  isbn_book($('#isbn').val());  
});
