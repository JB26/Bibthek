function new_graph(type){
  opt = window.location.pathname.split("/statistics/")
  $.getJSON( "/json_statistic/" + opt[1], {_type:type}, function(data) {
    var barChartData = {
      labels : data["labels"],
      datasets : [
        {
          fillColor : "rgba(151,187,205,0.5)",
          strokeColor : "rgba(151,187,205,0.8)",
          highlightFill : "rgba(151,187,205,0.75)",
          highlightStroke : "rgba(151,187,205,1)",
          data : data["data"]
        }
      ]
    };
    var ctx = $("#" + data["canvas_id"]).get(0).getContext("2d");
    window[data["canvas_id"]] = new Chart(ctx).Bar(barChartData, {
      responsive : true,
      animation: false
    });
  });
};

window.onload = function(){
  new_graph("release_date");
  new_graph("start_date");
  new_graph("finish_date");
  new_graph("add_date");
  new_graph("pages_read");
  new_graph("pages_book");
}

$('.chart').click(function(event) {
  var chart_name = $( this ).attr('id'),
    field_name = chart_name.split("_chart")[0]
    activeBars = window[chart_name].getBarsAtEvent(event);
  window[chart_name].destroy();
  if (activeBars[0]["label"].length == 4) {
    new_graph(field_name + "#" + activeBars[0]["label"]);
  } else {
    new_graph(field_name);
  };
});
