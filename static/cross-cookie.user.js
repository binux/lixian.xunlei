// ==UserScript==
// @name       cross-cookie
// @namespace  http://loli.lu/
// @version    0.11112
// @description  cross-cookie for lixian.xunlei
// @include    http://loli.lu/*
// @include    https://loli.lu/*
// @include    http://www.loli.lu/*
// @include    https://www.loli.lu/*
// @include    http://vip.xunlei.com/*
// @copyright  2011+, Binux<17175297.hk@gmail.com>
// @run-at     document-end
// ==/UserScript==

var version = "0.11112";
var _gc = function(name) {
    return document.getElementsByClassName(name);
};

if ('loading' != document.readyState) {
    var cookies = _gc("cross-cookie");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].getAttribute("data-version") == version) {
            cookies[i].setAttribute("style", "display: none;");
            document.cookie = "cross-cookie="+version;
        }
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
        GM_deleteValue(location.href);
    }
}
