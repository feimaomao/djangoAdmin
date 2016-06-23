$(function () {//文档解析完后执行
    $("body ").prepend('<div id="shadowDiv" class="hideDiv"></div><div id="tishi" class="hideDiv"><p align="center"><img src="/static/mana1/images/loading.gif"></img></p>系统正在操作!请稍后...</div>');
});
function turn_off_light(){
    $("#shadowDiv").attr("class", "showDiv");
    $("#tishi").attr("class", "showTishi");
}
function turn_on_light(){
    $("#shadowDiv").attr("class", "hideDiv");
    $("#tishi").attr("class", "hideDiv");
}

