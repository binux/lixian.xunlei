// ==UserScript==
// @name       cross-cookie
// @namespace  http://loli.lu/
// @version    0.11111
// @resource   version 0.11111
// @description  enter something useful
// @include    *
// @copyright  2011+, Binux<17175297.hk@gmail.com>
// @run-at     document-end
// ==/UserScript==

var _gc = function(name) {
    return document.getElementsByClassName(name);
};

if ('loading' != document.readyState) {
    var cookies = _gc("cross-cookie");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].getAttribute("data-version") == GM_getResourceText("version")) {
            cookies[i].setAttribute("style", "display: none;");
            document.cookie = "cross-cookie="+GM_getResourceText("version");
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
