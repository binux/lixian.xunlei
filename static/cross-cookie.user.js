// ==UserScript==
// @name       cross-cookie
// @namespace  http://loli.lu/
// @version    0.3
// @description  cross-cookie for lixian.xunlei
// @match http://127.0.0.1:8880/*
// @match http://loli.lu/*
// @match https://loli.lu/*
// @match http://www.loli.lu/*
// @match https://www.loli.lu/*
// @match http://vip.xunlei.com/*
// @copyright  2011-2012, Binux<17175297.hk@gmail.com>
// @run-at     document-end
// ==/UserScript==

var version = "0.3";
var _gc = function(name) {
    return document.getElementsByClassName(name);
};

if ('loading' != document.readyState) {
    var cookies = _gc("cross-cookie");
    if (cookies.length) {
        for (var i=0, len=cookies.length; i<len; i++) {
            if (cookies[i].getAttribute("data-version") == version) {
                cookies[i].setAttribute("style", "display: none;");
            }
            if (cookies[i].getAttribute("data-src")) {
                var iframe = document.createElement("iframe");
                iframe.src = cookies[i].getAttribute("data-src");
                iframe.setAttribute("style", "display: none;");
                document.body.appendChild(iframe);
                if (cookies[i].getAttribute("data-check")) {
                    var script = document.createElement('script');
                    script.src = cookies[i].getAttribute("data-check");
                    document.body.appendChild(script);
                };
            };
        };
        document.cookie = "cross-cookie="+version+"; path=/";
    };
    
    var hash = location.hash;
    if (hash.indexOf("#cross-cookie|") == 0) {
        var src = hash.split("|")[1];
        var script = document.createElement('script');
        script.src = src;
        document.write("cross-cookie is running..<br />inject script.src = "+src+"");
        document.body.appendChild(script);
    };
}
