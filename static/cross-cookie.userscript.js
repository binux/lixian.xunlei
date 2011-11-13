// ==UserScript==
// @name       cross-cookie
// @namespace  http://loli.lu/
// @version    0.11
// @description  enter something useful
// @include    http://127.0.0.1:*/*
// @include    http://loli.lu/*
// @include    http://*.vip.xunlei.com/*
// @copyright  2011+, Binux<17175297.hk@gmail.com>
// @run-at     document-end
// ==/UserScript==

var _gc = function(name) {
    return document.getElementsByClassName(name);
};

if ('loading' != document.readyState) {
    var cookies = _gc("cross-cookie");
    for (var i = 0; i < cookies.length; i++) {
        cookies[i].setAttribute("style", "display: none;");

        var site = cookies[i].getAttribute("data-site");
        var cookie = cookies[i].getAttribute("data-cookie");
        if (site == undefined || cookie == undefined)
            continue;

        GM_setValue(site, cookie);
        var iframe = document.createElement("iframe");
        iframe.setAttribute("style", "display: none;");
        iframe.src = site;
        document.body.appendChild(iframe);
    }
    
    if (GM_getValue(location.href) != undefined) {
        var cookie = GM_getValue(location.href);
        document.cookie = cookie;
    }
}

