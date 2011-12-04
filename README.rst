LiXian.XunLei: api of lixian.xunlei.com in python
=================================================

LiXian.XunLei is a python api base on http://lixian.xunlei.com/ , and a web project using this api.

迅雷离线API是基于迅雷离线网页版开发的python接口，并在这个接口基础上实现一套离线资源分享网站。


Features
--------
Api for lixian.xunlei.com.
 - Including add/fetch/delete/delay tasks or files.
 - Normal/bt/thunder/magnet url support and automatically distinguish.
 - Ulimit offline space.
 - task will never expired.

A website
 - Multi-user with permission control support.
 - Async
 - Search
 - Tags
 - Share
 - Download with wget/aria2

A plugin for flexget
 - add task with flexget

Usage
-----
Just ::

    python main.py --username=<xunlei_vip_username> --password=<your_password>

or you can using a config file ::

    username = "<your_username>"
    password = "<your_password>"

and start with command ::

    python main.py --f=<config>

Getting help ::

    python main.py --help

FlexGet Plugin
--------------
::

    cp libs/jsfunctionParser.py libs/lixian_api.py libs/plugin_lixian_xunlei.py ~/.flexget/plugins/

and add config ::

    xunlei_lixian:
        username: "<your username>"
        password: "<your password>"

presets<http://flexget.com/wiki/Plugins/preset> may help if you want to add it to all feeds.

Requires
--------
::

    easy_install requests
    easy_install pyparsing
    easy_install beautifulsoup
    easy_install sqlalchemy

if using mysql ::

    easy_install mysql-python

if mysql_config is not found ::

    apt-get install mysqlclient-dev

else ::

    apt-get install sqlite


