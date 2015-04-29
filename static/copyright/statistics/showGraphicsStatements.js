function initGraphics(url) {
	$.ajax( {
		type : "POST",
		dataType : "json",
		url : url,
		data : jQuery.param( {
			"into_date_begin" : $("#into_date_begin").val(),
			"into_date_end" : $("#into_date_end").val()
		}, true),
		success : function(data) {
			showGraphics(data['book_count_arr'], data['type_arr'])
		},
		error : function(msg) {
			$.alert('加载失败');
		}
	});
}

var options = {
	stacked : false,
	gutter : 20,
	axis : "0 0 1 1", // Where to put the labels (trbl)
	axisystep : 10
// How many x interval labels to render (axisystep does the same for the y axis)
};

function showGraphics(bookCountArr, typeArr) {
	if (bookCountArr.length==0 || typeArr.length==0){
			bookCountArr=[0];
			typeArr=[""]
		}
	// Creates canvas
	var r = Raphael("chartHolderty");
	//	var data = [ 10, 20, 30, 50 ]

	// stacked: false
	var chart1 = r.barchart(100, 10, 700, 220, bookCountArr, options).hover(
			function() {
				this.flag = r.popup(this.bar.x, this.bar.y, this.bar.value)
						.insertBefore(this);
			}, function() {
				this.flag.animate( {
					opacity : 0
				}, 500, ">", function() {
					this.remove();
				});
			});
	chart1.label(typeArr, true);

	// stacked: true
	options.stacked = false;
}