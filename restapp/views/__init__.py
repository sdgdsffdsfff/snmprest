#coding: utf-8
from restapp import restApp
from .billing import billingView
from .collcetions import collcetionsView

collcetionsView.register(restApp)
billingView.register(restApp)