# Author Caozy
import xadmin
from . import models


xadmin.site.register(models.OrderInfo)
xadmin.site.register(models.OrderGoods)