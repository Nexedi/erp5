import logging
logger = logging.getLogger(__name__)

hotfixes = (
    'setHeader',
    'allow_module',
    'get_request_var_or_attr',
    'safe_html', # XXX: must be merged into our PortalTransforms product
    'ftp',
    'atat',
    )

# Apply the fixes
for hotfix in hotfixes:
    try:
        __import__('%s.%s' % (__name__, hotfix))
        logger.info('Applied %s patch', hotfix)
    except Exception:
        logger.warn('Could not apply %s', hotfix)
logger.info('Hotfix installed')
