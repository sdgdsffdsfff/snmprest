#coding: utf-8
from restapp import restApp
from .billing import billingView
from .collcetions import collcetionsView
from .devices import devicesView
from .ports import portsView

collcetionsView.register(restApp)
billingView.register(restApp)
devicesView.register(restApp)
portsView.register(restApp)