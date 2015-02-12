$('.delete_acc_warn').click(function(event) {
  event.preventDefault();
  var username = $( this ).attr('id');
  warning("danger", 'Do you really want to delete the user: "' + username + '"and all his data? <a href="#" class="alert-link delete_acc" id="' + username + '" >YES!</a> ');
});

$('#alert_placeholder').on( "click", ".delete_acc", function(event) {
  event.preventDefault();
  var username = $( this ).attr('id');
  $.getJSON( "/delete_acc", {"username" : username}, function(data) {
    $('#tr_' + username).remove();
    warning(data['type'], data['error']);
  })
  .fail(function() {
    window.location.href = '/';
  });
});

$('.reset_pw').click(function(event) {
  event.preventDefault();
  var username = $( this ).attr('id');
  $.getJSON( "/reset_pw", {"username" : username}, function(data) {
    warning(data['type'], data['error']);
  })
  .fail(function() {
    window.location.href = '/';
  });
});
