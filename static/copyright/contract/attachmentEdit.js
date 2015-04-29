//新增
function addContractAtta() {
	var tab = $("#contract_atta_tab");
	addAtta1(tab);

}


//修改
function addContractAtta2() {
	var tab = $("#contract_atta_tab2");
	addAtta1(tab);

}

//新增
function addAtta1(tab) {
	$str = "";
	$str += "<tr align='center'>";
	$str += "<td><input type='file' class='required' name='tmpfile'/><a href='#' onClick='getDel(this)'>&nbsp;&nbsp;删除</a></td>";
	//$str += "<td onClick='getDel(this)'><a href='#'>删除</a></td>";
	$str += "</tr>";
	tab.append($str);
}




//删除附件
function getDel(k) {
	$(k).parent().remove();
}



function deleteExist2(k) {
	if (confirm("确定要删除已经保存的附件么？")) {
		$(k).parent().parent().remove();
		return true;
	} else {
		return false;
	}

}


function deleteExist(k) {
	if (confirm("确定要删除已经保存的附件么？")) {
		$(k).parent().remove();
		return true;
	} else {
		return false;
	}

}
