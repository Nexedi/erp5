var SafeImage = (function() {

  var that = {};

  that.loadOpenLayerZoomedImage= function(zoomify_width,
                                    zoomify_height, zoomify_url,data){
    if (that.map !== undefined){
        that.map.destroy();
    }
    /* First we initialize the zoomify pyramid (to get number of tiers) */
    that.zoomify = new OpenLayers.Layer.Zoomify( "Zoomify", zoomify_url,data,
      new OpenLayers.Size(zoomify_width, zoomify_height ) );

    /* Map with raster coordinates (pixels) from Zoomify image */
    var options = {
        maxExtent: new OpenLayers.Bounds(0, 0, zoomify_width, zoomify_height),
        maxResolution: Math.pow(2, that.zoomify.numberOfTiers-1 ),
        numZoomLevels: that.zoomify.numberOfTiers,
        units: 'pixels',
        size: new OpenLayers.Size(3000,2000)
    };

    that.map = new OpenLayers.Map("map", options);
    that.map.addLayer(that.zoomify);
    that.map.setBaseLayer(that.zoomify);
    that.map.zoomToMaxExtent();
  };
  return that
}());
