var sepia = function (dataI,width,height){

    var imagedata = dataI;  
    var data = imagedata.data;
    var w = width;
    var h = height;
    var w4 = w*4;
    var y = h;
    var mode = 1;


    /*for(i=0;i<10000000000;i++){
      5555*55555554;
      i++
    };*/ 

    do {
      var offsetY = (y-1)*w4;
      var x = w;

      do {
        var offset = offsetY + (x-1)*4;

        if (mode) {

          // a bit faster, but not as good

          var d = data[offset] * 0.299 + data[offset+1] * 0.587 + data[offset+2] * 0.114;
          var r = (d + 39);
          var g = (d + 14);
          var b = (d - 36);
        } else {
          // Microsoft
          var or = data[offset];
          var og = data[offset+1];
          var ob = data[offset+2];
          var r = (or * 0.393 + og * 0.769 + ob * 0.189);
          var g = (or * 0.349 + og * 0.686 + ob * 0.168);
          var b = (or * 0.272 + og * 0.534 + ob * 0.131);
      }

      if (r < 0) r = 0; if (r > 255) r = 255;
      if (g < 0) g = 0; if (g > 255) g = 255;
      if (b < 0) b = 0; if (b > 255) b = 255;

      data[offset] = r;
      data[offset+1] = g;
      data[offset+2] = b;

    } while (--x);
  } while (--y);
  imagedata.data = data;
  return imagedata;
};


var lighten = function(dataI,width,height,param) {
    var imagedata = dataI;
    var data = imagedata.data;
    var w = width;
    var h = height;
    var amount = parseFloat(param) || 0;
    var mode = 1;
		amount = Math.max(-1, Math.min(1, amount));

		if (mode) {

			var p = w * h;

			var pix = p*4, pix1 = pix + 1, pix2 = pix + 2;
			var mul = amount + 1;

			while (p--) {
				if ((data[pix-=4] = data[pix] * mul) > 255)
					data[pix] = 255;

				if ((data[pix1-=4] = data[pix1] * mul) > 255)
					data[pix1] = 255;

				if ((data[pix2-=4] = data[pix2] * mul) > 255)
					data[pix2] = 255;

			}


		} else {
			/*var img = params.image;
			if (amount < 0) {
				img.style.filter += " light()";
				img.filters[img.filters.length-1].addAmbient(
					255,255,255,
					100 * -amount
				);
			} else if (amount > 0) {
				img.style.filter += " light()";
				img.filters[img.filters.length-1].addAmbient(
					255,255,255,
					100
				);
				img.filters[img.filters.length-1].addAmbient(
					255,255,255,
					100 * amount
				);*/
        console.log("Internet Explorer is crap");
			}
		
	
		imagedata.data = data;  
    return imagedata;
	
};


var brightness = function(dataI,width,height,param1,param2) {

    var imagedata = dataI;
    var data = imagedata.data;
    var w = width;
    var h = height;
    var brightness = parseInt(param1,10) || 0;
		var contrast = parseFloat(param2)||0;
		//var legacy = !!(params.options.legacy && params.options.legacy != "false");
    var mode = 1;
  	brightness = Math.min(150,Math.max(-150,brightness));
		
		//var brightMul = 1 + Math.min(150,Math.max(-150,brightness)) / 150;
	  contrast = Math.max(0,contrast+1);

		if (mode) {
			var p = w*h;
			var pix = p*4, pix1, pix2;

			var mul, add;
			if (contrast != 1) {
					mul = contrast;
					add = (brightness - 128) * contrast + 128;
			} else {  // this if-then is not necessary anymore, is it?
					mul = 1;
					add = brightness;
			}
			var r, g, b;
			while (p--) {
				if ((r = data[pix-=4] * mul + add) > 255 )
					data[pix] = 255;
				else if (r < 0)
					data[pix] = 0;
				else
 					data[pix] = r;

				if ((g = data[pix1=pix+1] * mul + add) > 255 ) 
					data[pix1] = 255;
				else if (g < 0)
					data[pix1] = 0;
				else
					data[pix1] = g;

				if ((b = data[pix2=pix+2] * mul + add) > 255 ) 
					data[pix2] = 255;
				else if (b < 0)
					data[pix2] = 0;
				else
					data[pix2] = b;
			}
		}
	
  imagedata.data = data;
  return imagedata;
	
};


var posterize = function(dataI,width,height,param1) {

    var imagedata = dataI;
    var data = imagedata.data;
    var w = width;
    var h = height;
		var numLevels = 256;
    var mode = 1;
    var aux = param1;
    
		if (typeof aux != "undefined")
			numLevels = parseInt(aux,10)||1;

		if (mode) {

			numLevels = Math.max(2,Math.min(256,numLevels));
	
			var numAreas = 256 / numLevels;
			var numValues = 256 / (numLevels-1);

			var w4 = w*4;
			var y = h;
			do {
				var offsetY = (y-1)*w4;
				var x = w;
				do {
					var offset = offsetY + (x-1)*4;

					var r = numValues * ((data[offset] / numAreas)>>0);
					var g = numValues * ((data[offset+1] / numAreas)>>0);
					var b = numValues * ((data[offset+2] / numAreas)>>0);

					if (r > 255) r = 255;
					if (g > 255) g = 255;
					if (b > 255) b = 255;

					data[offset] = r;
					data[offset+1] = g;
					data[offset+2] = b;

				} while (--x);
			} while (--y);
		}
	  imagedata.data;
  	return imagedata;
};


var noise = function(dataI,width,height) {

    var imagedata = dataI;
    var data = imagedata.data;
    var w = width;
    var h = height;
    var mode = 1;
		var w4 = w*4;
		var y = h;


			do {
				var offsetY = (y-1)*w4;

				var nextY = (y == h) ? y - 1 : y;
				var prevY = (y == 1) ? 0 : y-2;

				var offsetYPrev = prevY*w*4;
				var offsetYNext = nextY*w*4;

				var x = w;
				do {
					var offset = offsetY + (x*4-4);

					var offsetPrev = offsetYPrev + ((x == 1) ? 0 : x-2) * 4;
					var offsetNext = offsetYNext + ((x == w) ? x-1 : x) * 4;

					var minR, maxR, minG, maxG, minB, maxB;

					minR = maxR = data[offsetPrev];
					var r1 = data[offset-4], r2 = data[offset+4], r3 = data[offsetNext];
					if (r1 < minR) minR = r1;
					if (r2 < minR) minR = r2;
					if (r3 < minR) minR = r3;
					if (r1 > maxR) maxR = r1;
					if (r2 > maxR) maxR = r2;
					if (r3 > maxR) maxR = r3;

					minG = maxG = data[offsetPrev+1];
					var g1 = data[offset-3], g2 = data[offset+5], g3 = data[offsetNext+1];
					if (g1 < minG) minG = g1;
					if (g2 < minG) minG = g2;
					if (g3 < minG) minG = g3;
					if (g1 > maxG) maxG = g1;
					if (g2 > maxG) maxG = g2;
					if (g3 > maxG) maxG = g3;

					minB = maxB = data[offsetPrev+2];
					var b1 = data[offset-2], b2 = data[offset+6], b3 = data[offsetNext+2];
					if (b1 < minB) minB = b1;
					if (b2 < minB) minB = b2;
					if (b3 < minB) minB = b3;
					if (b1 > maxB) maxB = b1;
					if (b2 > maxB) maxB = b2;
					if (b3 > maxB) maxB = b3;

					if (data[offset] > maxR) {
						data[offset] = maxR;
					} else if (data[offset] < minR) {
						data[offset] = minR;
					}
					if (data[offset+1] > maxG) {
						data[offset+1] = maxG;
					} else if (data[offset+1] < minG) {
						data[offset+1] = minG;
					}
					if (data[offset+2] > maxB) {
						data[offset+2] = maxB;
					} else if (data[offset+2] < minB) {
						data[offset+2] = minB;
					}

				} while (--x);
			} while (--y);

    imagedata.data = data;
		return imagedata;

}

var edges = function(dataI,width,height) {
    var imagedata = dataI;
    var data = imagedata.data;
    var dataCopy = data;
    var w = width;
    var h = height;
    var mono = false;
    var invert = false;
    var mode = 1;

		var c = -1/8;
		var kernel = [
				[c, 	c, 	c],
				[c, 	1, 	c],
				[c, 	c, 	c]
		];

		weight = 1/c;

		var w4 = w*4;
		var y = h;
			do {
				var offsetY = (y-1)*w4;

				var nextY = (y == h) ? y - 1 : y;
				var prevY = (y == 1) ? 0 : y-2;

				var offsetYPrev = prevY*w*4;
				var offsetYNext = nextY*w*4;

				var x = w;
				do {
					var offset = offsetY + (x*4-4);

					var offsetPrev = offsetYPrev + ((x == 1) ? 0 : x-2) * 4;
					var offsetNext = offsetYNext + ((x == w) ? x-1 : x) * 4;
	
					var r = ((dataCopy[offsetPrev-4]
						+ dataCopy[offsetPrev]
						+ dataCopy[offsetPrev+4]
						+ dataCopy[offset-4]
						+ dataCopy[offset+4]
						+ dataCopy[offsetNext-4]
						+ dataCopy[offsetNext]
						+ dataCopy[offsetNext+4]) * c
						+ dataCopy[offset]
						) 
						* weight;
	
					var g = ((dataCopy[offsetPrev-3]
						+ dataCopy[offsetPrev+1]
						+ dataCopy[offsetPrev+5]
						+ dataCopy[offset-3]
						+ dataCopy[offset+5]
						+ dataCopy[offsetNext-3]
						+ dataCopy[offsetNext+1]
						+ dataCopy[offsetNext+5]) * c
						+ dataCopy[offset+1])
						* weight;
	
					var b = ((dataCopy[offsetPrev-2]
						+ dataCopy[offsetPrev+2]
						+ dataCopy[offsetPrev+6]
						+ dataCopy[offset-2]
						+ dataCopy[offset+6]
						+ dataCopy[offsetNext-2]
						+ dataCopy[offsetNext+2]
						+ dataCopy[offsetNext+6]) * c
						+ dataCopy[offset+2])
						* weight;

					if (mono) {
						var brightness = (r*0.3 + g*0.59 + b*0.11)||0;
						if (invert) brightness = 255 - brightness;
						if (brightness < 0 ) brightness = 0;
						if (brightness > 255 ) brightness = 255;
						r = g = b = brightness;
					} else {
						if (invert) {
							r = 255 - r;
							g = 255 - g;
							b = 255 - b;
						}
						if (r < 0 ) r = 0;
						if (g < 0 ) g = 0;
						if (b < 0 ) b = 0;
						if (r > 255 ) r = 255;
						if (g > 255 ) g = 255;
						if (b > 255 ) b = 255;
					}

					data[offset] = r;
					data[offset+1] = g;
					data[offset+2] = b;

				} while (--x);
			} while (--y);
    imagedata.data = data;
		return imagedata;
};


self.addEventListener("message", function(e){
    var data = e.data;
    var result = edges(data.image,data.width,data.height);
    self.postMessage(result);
},false);

  
