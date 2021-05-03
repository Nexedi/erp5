from Products.CMFCore.CachingPolicyManager import CachingPolicy, \
    CachingPolicyManager, createCPContext
from App.special_dtml import DTMLFile
from Products.CMFCore.Expression import Expression
from App.Common import rfc1123_date
from DateTime.DateTime import DateTime
from Products.ERP5Type import _dtmldir

# Path CachingPolicy to add stale-if-error & stale-while-revalidate
# from RFC 5861


def __init__( self
            , policy_id
            , predicate=''
            , mtime_func=''
            , max_age_secs=None
            , stale_revalidate_secs=None
            , stale_error_secs=None
            , no_cache=0
            , no_store=0
            , must_revalidate=0
            , vary=''
            , etag_func=''
            , s_max_age_secs=None
            , proxy_revalidate=0
            , public=0
            , private=0
            , no_transform=0
            , enable_304s=0
            , last_modified=1
            , pre_check=None
            , post_check=None
            ):

    if not predicate:
        predicate = 'python:1'

    if not mtime_func:
        mtime_func = 'object/modified'

    if max_age_secs is not None:
        if str(max_age_secs).strip() == '':
            max_age_secs = None
        else:
            max_age_secs = int( max_age_secs )

    if s_max_age_secs is not None:
        if str(s_max_age_secs).strip() == '':
            s_max_age_secs = None
        else:
            s_max_age_secs = int( s_max_age_secs )

    if pre_check is not None:
        if str(pre_check).strip() == '':
            pre_check = None
        else:
            pre_check = int(pre_check)

    if post_check is not None:
        if str(post_check).strip() == '':
            post_check = None
        else:
            post_check = int(post_check)

    self._policy_id = policy_id
    self._predicate = Expression( text=predicate )
    self._mtime_func = Expression( text=mtime_func )
    self._max_age_secs = max_age_secs
    self._s_max_age_secs = s_max_age_secs
    self._no_cache = int( no_cache )
    self._no_store = int( no_store )
    self._must_revalidate = int( must_revalidate )
    self._proxy_revalidate = int( proxy_revalidate )
    self._public = int( public )
    self._private = int( private )
    self._no_transform = int( no_transform )
    self._vary = vary
    self._etag_func = Expression( text=etag_func )
    self._enable_304s = int ( enable_304s )
    self._last_modified = int( last_modified )
    self._pre_check = pre_check
    self._post_check = post_check
    self._stale_if_error_secs = int( stale_error_secs )
    self._stale_while_revalidate_secs = int( stale_revalidate_secs )

def getStaleIfErrorSecs( self ):
    """
    """
    return getattr(self, '_stale_if_error_secs', 0)

def getStaleWhileRevalidateSecs( self ):
    """
    """
    return getattr(self, '_stale_while_revalidate_secs', 0)

def getHeaders( self, expr_context ):
    """
        Does this request match our predicate?  If so, return a
        sequence of caching headers as ( key, value ) tuples.
        Otherwise, return an empty sequence.
    """
    headers = []

    if self.testPredicate( expr_context ):

        if self.getLastModified():
            mtime = self._mtime_func( expr_context )
            if type( mtime ) is type( '' ):
                mtime = DateTime( mtime )
            if mtime is not None:
                mtime_str = rfc1123_date(mtime.timeTime())
                headers.append( ( 'Last-modified', mtime_str ) )

        control = []

        if self.getMaxAgeSecs() is not None:
            now = expr_context.vars[ 'time' ]
            exp_time_str = rfc1123_date(now.timeTime() + self._max_age_secs)
            headers.append( ( 'Expires', exp_time_str ) )
            control.append( 'max-age=%d' % (self._max_age_secs,))
            if self.getStaleWhileRevalidateSecs():
                control.append( 'stale-while-revalidate=%d' % (
                        self.getStaleWhileRevalidateSecs(),))
            if self.getStaleIfErrorSecs():
                control.append( 'stale-if-error=%d' % (
                        self.getStaleIfErrorSecs(),))

        if self.getSMaxAgeSecs() is not None:
            control.append( 's-maxage=%d' % self._s_max_age_secs )

        if self.getNoCache():
            control.append( 'no-cache' )
            # The following is for HTTP 1.0 clients
            headers.append(('Pragma', 'no-cache'))

        if self.getNoStore():
            control.append( 'no-store' )

        if self.getPublic():
            control.append( 'public' )

        if self.getPrivate():
            control.append( 'private' )

        if self.getMustRevalidate():
            control.append( 'must-revalidate' )

        if self.getProxyRevalidate():
            control.append( 'proxy-revalidate' )

        if self.getNoTransform():
            control.append( 'no-transform' )

        pre_check = self.getPreCheck()
        if pre_check is not None:
            control.append('pre-check=%d' % pre_check)

        post_check = self.getPostCheck()
        if post_check is not None:
            control.append('post-check=%d' % post_check)

        if control:
            headers.append( ( 'Cache-control', ', '.join( control ) ) )

        if self.getVary():
            headers.append( ( 'Vary', self._vary ) )

        if self.getETagFunc():
            headers.append( ( 'ETag', self._etag_func( expr_context ) ) )

    return headers

def getModTimeAndETag( self, content, view_method, keywords, time=None):
    """
        Return the modification time and ETag for the content object,
        view method, and keywords as the tuple (modification_time, etag,
        set_last_modified_header), where modification_time is a DateTime,
        or None.
    """
    # XXX: this method violates the rules for tools/utilities:
    # createCPContext depends on a non-utility tool
    context = createCPContext( content, view_method, keywords, time=time )
    for policy_id, policy in self.listPolicies():
        if policy.testPredicate(context):
            if not policy.getEnable304s():
                return None
            last_modified = policy._mtime_func(context)
            if type(last_modified) is type(''):
                last_modified = DateTime(last_modified)

            content_etag = None
            if policy.getETagFunc():
                content_etag = policy._etag_func(context)

            return (last_modified, content_etag, policy.getLastModified())
    return None




def updatePolicy( self
                , policy_id
                , predicate           # TALES expr (def. 'python:1')
                , mtime_func          # TALES expr (def. 'object/modified')
                , max_age_secs        # integer, seconds (def. 0)
                , stale_revalidate_secs # integer, seconds (def, 0)
                , stale_error_secs    # integer, seconds (def, 0)
                , no_cache            # boolean (def. 0)
                , no_store            # boolean (def. 0)
                , must_revalidate     # boolean (def. 0)
                , vary                # string value
                , etag_func           # TALES expr (def. '')
                , REQUEST=None
                , s_max_age_secs=None # integer, seconds (def. 0)
                , proxy_revalidate=0  # boolean (def. 0)
                , public=0            # boolean (def. 0)
                , private=0           # boolean (def. 0)
                , no_transform=0      # boolean (def. 0)
                , enable_304s=0       # boolean (def. 0)
                , last_modified=1     # boolean (def. 1)
                , pre_check=0         # integer, default=None
                , post_check=0        # integer, default=None
                ):
    """
        Update a caching policy.
    """
    if max_age_secs is None or str(max_age_secs).strip() == '':
        max_age_secs = None
    else:
        max_age_secs = int(max_age_secs)

    if stale_revalidate_secs is None or str(stale_revalidate_secs).strip() == '':
        stale_revalidate_secs = None
    else:
        stale_revalidate_secs = int(stale_revalidate_secs)

    if stale_error_secs is None or str(stale_error_secs).strip() == '':
        stale_error_secs = None
    else:
        stale_error_secs = int(stale_error_secs)

    if s_max_age_secs is None or str(s_max_age_secs).strip() == '':
        s_max_age_secs = None
    else:
        s_max_age_secs = int(s_max_age_secs)

    if pre_check is None or str(pre_check).strip() == '':
        pre_check = None
    else:
        pre_check = int(pre_check)

    if post_check is None or str(post_check).strip() == '':
        post_check = None
    else:
        post_check = int(post_check)

    self._updatePolicy( policy_id
                      , predicate
                      , mtime_func
                      , max_age_secs
                      , stale_revalidate_secs
                      , stale_error_secs
                      , no_cache
                      , no_store
                      , must_revalidate
                      , vary
                      , etag_func
                      , s_max_age_secs
                      , proxy_revalidate
                      , public
                      , private
                      , no_transform
                      , enable_304s
                      , last_modified
                      , pre_check
                      , post_check
                      )
    if REQUEST is not None:
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                                      + '/manage_cachingPolicies'
                                      + '?manage_tabs_message='
                                      + 'Policy+updated.'
                                      )


def _updatePolicy( self
                 , policy_id
                 , predicate
                 , mtime_func
                 , max_age_secs
                 , stale_revalidate_secs
                 , stale_error_secs
                 , no_cache
                 , no_store
                 , must_revalidate
                 , vary
                 , etag_func
                 , s_max_age_secs=None
                 , proxy_revalidate=0
                 , public=0
                 , private=0
                 , no_transform=0
                 , enable_304s=0
                 , last_modified=1
                 , pre_check=None
                 , post_check=None
                 ):
    """
        Update a policy in our registry.
    """
    if policy_id not in self._policy_ids:
        raise KeyError("Policy %s does not exist!" % policy_id)

    self._policies[ policy_id ] = CachingPolicy( policy_id
                                               , predicate
                                               , mtime_func
                                               , max_age_secs
                                               , stale_revalidate_secs
                                               , stale_error_secs
                                               , no_cache
                                               , no_store
                                               , must_revalidate
                                               , vary
                                               , etag_func
                                               , s_max_age_secs
                                               , proxy_revalidate
                                               , public
                                               , private
                                               , no_transform
                                               , enable_304s
                                               , last_modified
                                               , pre_check
                                               , post_check
                                               )

def addPolicy( self
             , policy_id
             , predicate           # TALES expr (def. 'python:1')
             , mtime_func          # TALES expr (def. 'object/modified')
             , max_age_secs        # integer, seconds (def. 0)
             , stale_revalidate_secs # integer, seconds (def, 0)
             , stale_error_secs    # integer, seconds (def, 0)
             , no_cache            # boolean (def. 0)
             , no_store            # boolean (def. 0)
             , must_revalidate     # boolean (def. 0)
             , vary                # string value
             , etag_func           # TALES expr (def. '')
             , REQUEST=None
             , s_max_age_secs=None # integer, seconds (def. None)
             , proxy_revalidate=0  # boolean (def. 0)
             , public=0            # boolean (def. 0)
             , private=0           # boolean (def. 0)
             , no_transform=0      # boolean (def. 0)
             , enable_304s=0       # boolean (def. 0)
             , last_modified=1     # boolean (def. 1)
             , pre_check=None      # integer, default None
             , post_check=None     # integer, default None
             ):
    """
        Add a caching policy.
    """
    if max_age_secs is None or str(max_age_secs).strip() == '':
        max_age_secs = None
    else:
        max_age_secs = int(max_age_secs)

    if stale_revalidate_secs is None or str(stale_revalidate_secs).strip() == '':
        stale_revalidate_secs = None
    else:
        stale_revalidate_secs = int(stale_revalidate_secs)

    if stale_error_secs is None or str(stale_error_secs).strip() == '':
        stale_error_secs = None
    else:
        stale_error_secs = int(stale_error_secs)

    if s_max_age_secs is None or str(s_max_age_secs).strip() == '':
        s_max_age_secs = None
    else:
        s_max_age_secs = int(s_max_age_secs)

    if pre_check is None or str(pre_check).strip() == '':
        pre_check = None
    else:
        pre_check = int(pre_check)

    if post_check is None or str(post_check).strip() == '':
        post_check = None
    else:
        post_check = int(post_check)

    self._addPolicy( policy_id
                   , predicate
                   , mtime_func
                   , max_age_secs
                   , stale_revalidate_secs
                   , stale_error_secs
                   , no_cache
                   , no_store
                   , must_revalidate
                   , vary
                   , etag_func
                   , s_max_age_secs
                   , proxy_revalidate
                   , public
                   , private
                   , no_transform
                   , enable_304s
                   , last_modified
                   , pre_check
                   , post_check
                   )
    if REQUEST is not None:
        REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                                      + '/manage_cachingPolicies'
                                      + '?manage_tabs_message='
                                      + 'Policy+added.'
                                      )

def _addPolicy( self
              , policy_id
              , predicate
              , mtime_func
              , max_age_secs
              , stale_revalidate_secs
              , stale_error_secs
              , no_cache
              , no_store
              , must_revalidate
              , vary
              , etag_func
              , s_max_age_secs=None
              , proxy_revalidate=0
              , public=0
              , private=0
              , no_transform=0
              , enable_304s=0
              , last_modified=1
              , pre_check=None
              , post_check=None
              ):
    """
        Add a policy to our registry.
    """
    policy_id = str( policy_id ).strip()

    if not policy_id:
        raise ValueError("Policy ID is required!")

    if policy_id in self._policy_ids:
        raise KeyError("Policy %s already exists!" % policy_id)

    self._policies[ policy_id ] = CachingPolicy( policy_id
                                               , predicate
                                               , mtime_func
                                               , max_age_secs
                                               , stale_revalidate_secs
                                               , stale_error_secs
                                               , no_cache
                                               , no_store
                                               , must_revalidate
                                               , vary
                                               , etag_func
                                               , s_max_age_secs
                                               , proxy_revalidate
                                               , public
                                               , private
                                               , no_transform
                                               , enable_304s
                                               , last_modified
                                               , pre_check
                                               , post_check
                                               )
    idlist = list( self._policy_ids )
    idlist.append( policy_id )
    self._policy_ids = tuple( idlist )


CachingPolicy.__init__ = __init__
CachingPolicy.getStaleIfErrorSecs = getStaleIfErrorSecs
CachingPolicy.getStaleWhileRevalidateSecs = getStaleWhileRevalidateSecs
CachingPolicy.getHeaders = getHeaders
CachingPolicyManager.updatePolicy = updatePolicy
CachingPolicyManager._updatePolicy = _updatePolicy
CachingPolicyManager.addPolicy = addPolicy
CachingPolicyManager._addPolicy = _addPolicy
CachingPolicyManager.manage_cachingPolicies = DTMLFile( 'cachingPolicies', _dtmldir )
CachingPolicyManager.getModTimeAndETag = getModTimeAndETag
