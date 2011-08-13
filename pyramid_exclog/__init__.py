import logging

from pyramid.tweens import EXCVIEW
from pyramid.settings import aslist
from pyramid.util import DottedNameResolver
from pyramid.httpexceptions import WSGIHTTPException

resolver = DottedNameResolver(None)

import __builtin__

def as_globals_list(value):
    L = []
    value = aslist(value)
    for dottedname in value:
        if dottedname in __builtin__.__dict__:
            dottedname = '__builtin__.%s' % dottedname
        obj = resolver.resolve(dottedname)
        L.append(obj)
    return L

def exclog_tween_factory(handler, registry):

    get = registry.settings.get

    ignored = get('exclog.ignore', (WSGIHTTPException,))

    def exclog_tween(request, getLogger=logging.getLogger):
        # getLogger injected for testing purposes
        try:
            return handler(request)
        except ignored:
            raise
        except:
            logger = getLogger('exc_logger')
            logger.exception(request.url)
            raise

    return exclog_tween

def includeme(config):
    """
    Set up am implicit :term:`tween` to log exception information that is
    generated by your Pyramid application.  The logging data will be sent to
    the Python logger named ``exc_logger``.

    This tween configured to be placed 'below' the exception view tween.  It
    will log all exceptions (even those eventually caught by a Pyramid
    exception view) except 'http exceptions' (any exception that derives from
    ``pyramid.httpexceptions.WSGIHTTPException`` such as ``HTTPFound``).  You
    can instruct ``pyramid_exclog`` to ignore custom exception types by using
    the ``excview.ignore`` configuration setting.
    """
    get = config.registry.settings.get
    ignored = as_globals_list(get('exclog.ignore',
                                  'pyramid.httpexceptions.WSGIHTTPException'))
    config.registry.settings['exclog.ignore'] = tuple(ignored)
    config.add_tween('pyramid_exclog.exclog_tween_factory',
                     alias='exclog', under=EXCVIEW)
