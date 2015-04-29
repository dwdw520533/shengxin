/*
 Highcharts JS v2.3.3 (2012-10-04)
 Exporting module

 (c) 2010-2011 Torstein

 License: www.highcharts.com/license
*/
$(function(){
		$("select[name='recharge_way']").hide();
		$("select[name='recharge_way']").attr("value","0")
		$("select[name='issue_class']").change(function(){
			var ic=$(this).val();
			//当值为40时是充值问题，这时候显示充值方式
		
			if(ic==40)
			{
			$("select[name='recharge_way']").attr("class","combox")
			$("select[name='recharge_way']").attr("value","10")
			$("select[name='recharge_way']").show();
		
			}
			else{
			
			$("select[name='recharge_way']").hide();
			}
	}) 
	})
	function doTest(form)
	{
		var $form = $(form);
		if (!$form.valid()) {
			if(window.event){
				window.event.returnValue = false;
				return;
			} 
			return false;
		}

		$.ajax({
			type: 'POST',
			url:"query/add",
			data:$form.serializeArray(),
			dataType:"json",
			async: false,
			success:function(jsonResult){
			    alertMsg.correct(jsonResult.message);
			  
			},
			error:function(obj){
				alert(obj.responseText);
			}
		});
	  
   		 if (!window.event) { // 标准浏览器  
   	   		return false; 
   		 } else { // IE浏览器  
       		 window.event.returnValue = false;  
    	}  
	  // window.event.returnValue = false;
	}
