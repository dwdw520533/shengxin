/*
 Highcharts JS v2.3.3 (2012-10-04)
 Exporting module

 (c) 2010-2011 Torstein

 License: www.highcharts.com/license
*/
<!--用户呼叫中心> <!-->
// *************************************************
// 全局变量定义
// *************************************************
var m_IsDebug = true;

// 座席签入参数
var strAgentID=document.getElementById('login_real_name');

var strAgentID = "3012";
var strAgentName = "王大力";

var strSkillDesc = "test2=1;";
var lAgentType = 1;
var lAutoAnswer = 1;
var lAutoReady = 1;
var strCTIMasterIP = "192.168.6.71";
var strSIPMasterIP ="";
var strCTISlaveIP = "";
var strSIPSlaveIP = "";

// 外呼、咨询、转移、会议参数
var lDestType = 1;
var strDestNo = "3003";
var strCallerID = "";

// 监控数据
var lTopicID = 150;
var strTopicSQL = "Select * from RT_Domain";

// *************************************************
// AgentSoftPhone 方法
// *************************************************
function AgentBar_Start()
{
    var staff_no = document.getElementById('login_staff_no');
    var login_real_name = document.getElementById('login_real_name');
    AgentBar.strAgentID = staff_no.value;
    AgentBar.strAgentName = login_real_name.value;

	AgentBar.lAgentType = lAgentType;
	AgentBar.lAutoAnswer = lAutoAnswer;
	AgentBar.lAutoReady = lAutoReady;
	AgentBar.strCTIMasterIP = strCTIMasterIP;
	AgentBar.strSIPMasterIP = strSIPMasterIP;
	AgentBar.strCTISlaveIP = strCTISlaveIP;
	AgentBar.strSIPSlaveIP = strSIPSlaveIP;

	AgentBar.strACDAgentID = "";
	AgentBar.strACDPassword = "";
	AgentBar.strACDGroup = "";
	
	AgentBar.Start();
	
}	

function AgentBar_Quit()
{
	AgentBar.Quit();
}

function AgentBar_Login()
{
	AgentBar_Start();
	var button=document.getElementById('agent_btnLogin');
	
	if(button.value=="签入"){
		var login_status=AgentBar.AgentLogin();
		if(login_status==1){
			login_status=AgentBar.AgentLogin();
		}
		if(login_status==0){
			button.value="签出"
		}
	}
	else{
	var	logout_status=AgentBar.AgentLogout();
	if(logout_status==1){
		logout_status=AgentBar.AgentLogout();
		
	}
	if(logout_status==0){
		button.value="签入"
	}
	}
	
	
	
}	

function AgentBar_Ready()
{
	AgentBar_Start();
	var button=document.getElementById('agent_Ready');
	
	
	if(button.value=="置闲"){
		
		var	logout_status=AgentBar.AgentReady();
		if(logout_status==1){
			logout_status=AgentBar.AgentReady();
		}
	}
	if(button.value=="置忙"){
		var login_status=AgentBar.AgentNotReady();
		if(login_status==1){
			login_status=AgentBar.AgentNotReady();
		}
	}
if(button.value=="结束整理"){
		
		var	logout_status=AgentBar.AgentReady();
		if(logout_status==1){
			logout_status=AgentBar.AgentReady();
		}
	}
}
function AgentBar_Logout()
{
	AgentBar.AgentLogout();
}

function AgentBar_AnswerCall()
{
	AgentBar.AnswerCall();
}

function AgentBar_HangupCall()
{
	AgentBar.HangupCall();
}

function AgentBar_HoldCall()
{
	AgentBar.HoldCall();
}

function AgentBar_RetrieveCall()
{
	AgentBar.RetrieveCall();
}

function AgentBar_MakeCall()
{
	lDestType = edtDestType.value;
  strDestNo = edtDestNo.value;
	AgentBar.MakeCall(lDestType, strDestNo, strCallerID);
}

function AgentBar_ConsultCall()
{
	lDestType = edtDestType.value;
  strDestNo = edtDestNo.value;
	AgentBar.ConsultCall(lDestType, strDestNo, strCallerID);
}


function AgentBar_ForwardCall()
{
	AgentBar.ForwardCall();
}

function AgentBar_JoinCall()
{
	AgentBar.JoinCall();
}

function AgentBar_ReconnectCall()
{
	AgentBar.ReconnectCall();
}

function AgentBar_TransferCall()
{
	lDestType = edtDestType.value;
  strDestNo = edtDestNo.value;
	AgentBar.TransferCall(lDestType, strDestNo, strCallerID);
}

function AgentBar_HelpCallMonitor()
{
	AgentBar.HelpCallMonitor();
}

function AgentBar_ConferenceCall()
{
	lDestType = edtDestType.value;
  strDestNo = edtDestNo.value;
	AgentBar.ConferenceCall(lDestType, strDestNo, strCallerID);
}

function AgentBar_SetCallData()
{
	var strDataKey;
	var strDataValue;
	
	strDataKey = edtDataKey.value;
	strDataValue = edtDataValue.value;
	
	AgentBar.SetCallData( strDataKey, strDataValue );
}

function AgentBar_GetCallData()
{
	var strOriANI;
	var strOriDNIS;
	
	strOriANI = AgentBar.GetCallData("Key_IContact_ANI"); 
	strOriDNIS = AgentBar.GetCallData("Key_IContact_DNIS");
	
	DebugAlert( "ANI=" + strOriANI + ";DNIS=" + strOriDNIS );
}

function AgentBar_GetAgentState()
{
	var strAgentID;
	var nRet;
	
	strAgentID = edtDestNo.value;
	
	nRet = AgentBar.GetAgentState( strAgentID ); 
	
	DebugAlert( "AgentID=" + strAgentID + ";State=" + nRet );
}

function AgentBar_SendTextMessage()
{
	var strAgentID;
	var strMessage;
	
	strAgentID = edtDestNo.value;
	strMessage = "你好，Hello!"
	
	AgentBar.SendTextMessage( strAgentID, strMessage ); 
}		

function AgentBar_ListenCall()
{
}

function AgentBar_InsertCall()
{
}

function AgentBar_ForceHangupCall()
{
	var strAgentID;
		
	strAgentID = edtDestNo.value;
	
	AgentBar.ForceHangupCall( strAgentID ); 
}		

function AgentBar_InterceptCall()
{
	var strAgentID;
	
	strAgentID = edtDestNo.value;
	
	AgentBar.InterceptCall( strAgentID ); 
}		


function AgentBar_SubscribeData( )
{
	AgentBar.SubscribeData( lTopicID );
}


function AgentBar_UnSubscribeData( )
{
	AgentBar.UnSubscribeData( lTopicID );
}

function AgentBar_OpenDataSet()
{
	AgentBar.OpenDataSet( 0, "", strTopicSQL );
}

function AgentBar_CloseDataSet()
{
	AgentBar.CloseDataSet();
}

function AgentBar_GetFieldData()
{
	var strTemp;
	
	strTemp = AgentBar.GetFieldData(1,1);

	DebugAlert( strTemp );
}

function AgentBar_RouteSelect()
{
	var strContactID;
	
	strContactID = edtContactID.value;
	lDestType = edtDestType.value;
  strDestNo = edtDestNo.value;

	AgentBar.RouteSelect(strContactID, lDestType, strDestNo);
}

// *************************************************
// AgentSoftPhone 事件
// *************************************************
function AgentBar_OnEvtOffering(strContactID,lCurrStatus,strOriANI,strOriDNIS,lCallDirection,lCallType,lCallID,strOtherParty,strCallingParty,strCalledParty,lResonCode )
{	
	var strTemp;
	strTemp = "OnEvtOffering::ContactID: " + strContactID + "; OriANI: " + strOriANI;
 	var type=document.getElementById("s_type");
    var s_text=document.getElementById("s_text");
    type.value=0;
    s_text.value=strOriANI;
    var url= "query/ident?type=0&id="+strOriANI;
    var button=document.getElementById("ident_submit");
    button.href=url;
    button.click(); 
}

function AgentBar_OnEvtDialing(strContactID,lCurrStatus,strOriANI,strOriDNIS,lCallDirection,lCallType,lCallID,strOtherParty,strCallingParty,strCalledParty,lResonCode )
{	
	var strTemp;
	
	strTemp = "OnEvtDialing::ContactID: " + strContactID + "; OriANI: " + strOriANI;

	DebugAlert( strTemp );
	
}

function AgentBar_OnEvtRecordEnd(strContactID,strOriANI,strOriDNIS,lCallID,strOtherParty,strCallingParty,strCalledParty,strFileName,lTimeLen,lResonCode )
{	
	//var strTemp;
	
	//strTemp = "OnEvtRecordEnd::ContactID: " + strContactID + "; OriANI: " + strOriANI + "; FileName: " + strFileName;

	//DebugAlert( strTemp );
}


function AgentBar_OnEvtStatusChanged(lEventType,lCurrStatus,lEventReason,strUserData)
{
	var strTemp;
	var button_ready=document.getElementById('agent_Ready');
	var status=document.getElementById('agent_status');
	
	if(lEventType==1){
		if(lCurrStatus==1){
			status.value="签入";
		}
		if(lCurrStatus==2){
			button_ready.value="置闲";
			status.value="置忙";
		}
		if(lCurrStatus==3){
			button_ready.value="置忙";
			status.value="空闲";
		}
		if(lCurrStatus==8){
			button_ready.value="置闲";
				status.value="签出";
		}
		if(lCurrStatus==6){
			button_ready.value="结束整理";
				status.value="事后整理";
		}
		
	}
	strTemp = "UserData: " + strUserData;
	if( (lEventType == 2)  && (strUserData != "") )
		DebugAlert( strTemp );
}

function AgentBar_OnEvtTextMessage(strAgentID,strAgentName,strMessage)
{
	var strTemp;
	
	strTemp = "SrcAgentID:" + strAgentID +"; Message:" + strMessage;

	DebugAlert( strTemp );
}

function AgentBar_OnEvtDataSet(lTopicID,strTopicName,strTopicSQL)
{
	var strTemp;
	
	strTemp = "TopicID:" + lTopicID +"; TopicSQL:" + strTopicSQL;

	DebugAlert( strTemp );
}


// *************************************************
// 共用的方法
// *************************************************
function DebugAlert( message )
{
	if( m_IsDebug == true)
		alert( message );
}

// *************************************************
// 页面调用的方法
// *************************************************
function OnLoad()
{
}

function OnUnload()
{
	AgentBar_Quit();
}




