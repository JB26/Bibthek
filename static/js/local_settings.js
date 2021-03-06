$( '.change_mail_pw' ).submit(function( event ) {
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
      if (data.hasOwnProperty('email')) {
        $('#email').html("Your current Email adress: " + data['email'])
      }
      warning(data['type'], data['error']);
      $( this ).find("input[type=password]").val("");
    }
  })
  .fail(function() {
    window.location.href = '/';
  });
});

$('#alert_placeholder').on( "click", "#delete_acc", function(event) {
  event.preventDefault();
  var password = $('#password_del_acc').val();
  $.getJSON( "/delete_acc", {"password" : password, "_json" : 'true'}, function(data) {
    warning(data['type'], data['error']);
  });
});
