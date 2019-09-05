from Products.PortalTransforms.interfaces.transform import ITransform

class IChain(ITransform):

    def registerTransform(transform, condition=None):
        """Append a transform to the chain"""
