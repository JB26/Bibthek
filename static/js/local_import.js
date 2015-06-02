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
    dataType: 'json',
    success: function(json_data){
      var data = json_data;
      warning(data['type'], data['error']);
    }
  })
  .fail(function() {
    window.location.href = '/';
  });
});

$('#alert_placeholder').on( "click", "#delete_all", function(event) {
  event.preventDefault();
  $.getJSON( "/delete_all", function(data) {
    warning(data['type'], data['error']);
  });
});
