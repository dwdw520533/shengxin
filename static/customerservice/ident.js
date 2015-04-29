/*
 Highcharts JS v2.3.3 (2012-10-04)
 Exporting module

 (c) 2010-2011 Torstein

 License: www.highcharts.com/license
*/
function get_url(ident_url, recharge_url)
{
    var type=document.getElementById("s_type");
    var s_text=document.getElementById("s_ident");
    var button=document.getElementById("ident_submit");
    var url= ident_url + "&type="+type.value+"&id="+s_text.value;
    button.rel="ident";
    button.target="navTab";
    if (type.value >= 2) {
        button.rel="rellist";
        var url= recharge_url + "&type="+type.value+"&id="+s_text.value;
        button.title="用户识别列表";
        button.target="dialog";
    }
    button.href=url
}

