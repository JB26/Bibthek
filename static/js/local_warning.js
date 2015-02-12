function warning(type, message) {
  $('#alert_placeholder').html(
    '<div class="alert alert-'+type+' alert-dismissable">\
      <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button><span>'+message+'</span>\
    </div>'
    )
}
