#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-6

# 程序运行的基本操作

# 后端服务程序：python3 manage.py runserver

# 前端进入front目录: live-server

# 异步执行，celery_tasks同级目录：celery -A celery_tasks.main worker -l info

# 开启nginx：nginx

# 创建开启fastdfs：
        # docker run -dti --network=host --name tracker -v /var/fdfs/tracker:/var/fdfs delron/fastdfs tracker
        # docker run -dti --network=host --name storage -e TRACKER_SERVER=192.168.229.133:22122 -v /var/fdfs/storage:/var/fdfs delron/fastdfs storage
        # docker container start tracker
        # docker container start storage


# 开启静态页面定时执行：
        # python manage.py crontab add
        # python manage.py crontab show
        # python manage.py crontab remove

# 创建搜索引擎
        # docker run -dti --network=host --name=elasticsearch -v /var/elasticsearch-2.4.6/config:/usr/share/elasticsearch/config delron/elasticsearch-ik:2.4.6-1.0
