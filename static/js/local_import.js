$( '#import_form' ).submit(function( event ) {
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
      warning(data['type'], data['error']);
    }
  });
});

$('#delete_all_warn').click(function(event) {
  event.preventDefault();
  warning("danger", 'Do you really want to delete all books? <a href="/delete_all" class="alert-link" id="delete_all">YES!</a> ');
});

$('#alert_placeholder').on( "click", "#delete_all", function(event) {
  event.preventDefault();
  $.getJSON( "/delete_all", function(data) {
    warning(data['type'], data['error']);
  });
});
