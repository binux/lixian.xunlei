// ==UserScript==
// @name       cross-cookie
// @namespace  http://loli.lu/
// @version    0.2
// @description  cross-cookie for lixian.xunlei
// @match http://loli.lu/*
// @match https://loli.lu/*
// @match http://www.loli.lu/*
// @match https://www.loli.lu/*
// @match http://vip.xunlei.com/*
// @copyright  2011-2012, Binux<17175297.hk@gmail.com>
// @run-at     document-end
// ==/UserScript==

var version = "0.2";
var callback = "http://loli.lu/xss?gdriveid="
var _gc = function(name) {
    return document.getElementsByClassName(name);
};

if (typeof(GM_setValue) == "undefined" || typeof(GM_getValue) == "undefined" || typeof(GM_deleteValue) == "undefined") {
    console.log("here");
    alert("Greasemonkey API is not support! Make sure you installed this script with plugin/addon in step 1");
} else if ('loading' != document.readyState) {
    var cookies = _gc("cross-cookie");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].getAttribute("data-version") == version) {
            cookies[i].setAttribute("style", "display: none;");
            document.cookie = "cross-cookie="+version;
        }
        var site = cookies[i].getAttribute("data-site");
        var cookie = cookies[i].getAttribute("data-cookie");
        var gdriveid = cookie.split(";")[0].split("gdriveid=")[1];
        if (site == undefined || cookie == undefined)
            continue;
        if (document.cookie.indexOf("xss="+gdriveid) != -1)
            continue;

        GM_setValue(site, cookie);
        var script = document.createElement("script");
        script.src = "/xss_check.js?gdriveid="+gdriveid;
        document.body.appendChild(script);
        var iframe = document.createElement("iframe");
        iframe.setAttribute("style", "display: none;");
        iframe.src = site;
        document.body.appendChild(iframe);
    };
    
    if (GM_getValue(location.href) != undefined) {
        var cookie = GM_getValue(location.href);
        var gdriveid = cookie.split(";")[0].split("gdriveid=")[1];
        document.cookie = cookie;
        if (gdriveid) {
          var iframe = document.createElement("iframe");
          iframe.setAttribute("style", "display: none;");
          iframe.src = callback+gdriveid;
          document.body.appendChild(iframe);
        };
        GM_deleteValue(location.href);
    };
}
