var xss_retry = 3;
var stoped = false;
function xss() {
  if (document.cookie.indexOf("xss={{ gdriveid }}") != -1) {
    $.fancybox.close();
    document.location.reload();
    clearInterval(timer);
    return;
  };
  if (xss_retry <= 0 || stoped) {
    $.fancybox('<div style="width:300px;"><p style="color: red;">Cookie写入失败...</p><p>您可能无法使用浏览器下载功能</p><p><a href="javascript:location.reload();">刷新重试</a>，或向作者回报这个问题：<a href="http://gplus.to/binux">+足兆叉虫</a></p></div>', {padding: 20, onClosed: function () { document.cookie = "xss={{ gdriveid }};"; }});
    clearInterval(timer);
    return;
  };
  xss_retry -= 1;
};

var timer;
$(document).ready(function() {
  if (document.cookie.indexOf("xss={{ gdriveid }}") == -1 && document.cookie.indexOf("cross-cookie=") != -1) {
    $.fancybox('<div style="width:300px">正在尝试写入cookie，请稍候...</div>', {padding: 20});
    timer = setInterval(function() { xss(); }, 3000);
  };
});
