// Autocomplete can't use (local) variables :(
$('#authors').autocomplete({
  //triggerSelectOnValidInput set to false to enable delimter ' & ' (else: Problems with whitespace)
  triggerSelectOnValidInput: false,
  deferRequestBy: 100,
  delimiter: ' & ',
  serviceUrl: '/autocomplete/authors'
});
$('#artist').autocomplete({
  triggerSelectOnValidInput: false,
  deferRequestBy: 100,
  delimiter: ' & ',
  serviceUrl: '/autocomplete/artist'
});
$('#colorist').autocomplete({
  triggerSelectOnValidInput: false,
  deferRequestBy: 100,
  delimiter: ' & ',
  serviceUrl: '/autocomplete/colorist'
});
$('#cover_artist').autocomplete({
  triggerSelectOnValidInput: false,
  deferRequestBy: 100,
  delimiter: ' & ',
  serviceUrl: '/autocomplete/cover_artist'
});
$('#publisher').autocomplete({
  deferRequestBy: 100,
  serviceUrl: '/autocomplete/publisher'
});
$('#series').autocomplete({
  deferRequestBy: 100,
  serviceUrl: '/autocomplete/series'
});
$('#language').autocomplete({
  deferRequestBy: 100,
  serviceUrl: '/autocomplete/language'
});
$('#binding').autocomplete({
  deferRequestBy: 100,
  serviceUrl: '/autocomplete/binding'
});
$('#shelf').autocomplete({
  deferRequestBy: 100,
  triggerSelectOnValidInput: false,
  serviceUrl: '/autocomplete/shelf'
});
$('#genre').autocomplete({
  deferRequestBy: 100,
  triggerSelectOnValidInput: false,
  delimiter: ', ',
  serviceUrl: '/autocomplete/genre'
});
