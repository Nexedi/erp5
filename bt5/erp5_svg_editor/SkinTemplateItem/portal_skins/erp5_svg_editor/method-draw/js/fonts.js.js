
function populateFonts(fonts){
  let options = "";
  let fontLinks = "";
  const formats = {
    ttf: "truetype",
    otf: "opentype",
    svg: "svg",
    woff: "woff",
    woff2: "woff2",
  };
  for (fontName in fonts) {
    const font_text = fonts[fontName].text;
    options += `
      <option value="${fontName}">${font_text}</option>
    `;
  }

  $("#font_family_dropdown").append(options);
};

const fonts = {

  "sans-serif": {
    "text": "sans-serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "serif": {
    "text": "serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "monospace": {
    "text": "monospace",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Arvo": {
    "text": "Arvo, sans-serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Courier": {
    "text": "'Courier New', Courier, monospace",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Euphoria": {
    "text": "Euphoria, sans-serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Georgia": {
    "text": "Georgia, Times, 'Times New Roman', serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Helvetica": {
    "text": "Helvetica, Arial, sans-serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Junction": {
    "text": "Junction, sans-serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "League Gothic": {
    "text": "'League Gothic', sans-serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Open Sans": {
    "text": "'Open Sans', sans-serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Oswald": {
    "text": "Oswald, sans-serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Palatino": {
    "text": "'Palatino Linotype', 'Book Antiqua', Palatino, serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Trebuchet": {
    "text": "'Trebuchet MS', Gadget, sans-serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Shadows Into Light": {
    "text": "'Shadows Into Light', serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Simonetta": {
    "text": "'Simonetta', serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  },

  "Times": {
    "text": "'Times New Roman', Times, serif",
    "axes": {
      "wght": {
        name: "Weight",
        range: [400, 900],
        value: 400
      }
    }
  }
};

populateFonts(fonts);