function load_book(book_id){
  $.getJSON( "/book", {book_id:book_id, json_data:"True"},function(data) {
    $.each(data,function(input_id, input_value){
      $('#' + input_id).val(input_value)
    });
    $('#cover').attr('src', '/static/' + data.front);
    $('#book_form').attr('action', '/save/?book_id=' + data._id);
    $('#isbn_search').hide()
  });
};

function empty_book(){
  $.getJSON( "/", {json_data:"True"},function(data) {
    $.each(data,function(input_id, input_value){
      $('#' + input_id).val(input_value)
    });
    $('#cover').attr('src', '/static/icons/circle-x.svg');
    $('#book_form').attr('action', '/save/?book_id=' + data._id);
    $('#isbn_search').show();
  });
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
  load_book(book_id);
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
    history.replaceState(book_id, '', '/');
  } else {
    history.replaceState(book_id, '', '/book?book_id=' + book_id)};
};
