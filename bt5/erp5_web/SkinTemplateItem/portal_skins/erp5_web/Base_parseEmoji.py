"""
Example:
input: 'before emoji1 after after2 emoji2'
return: [
  ("data", 'before '),
  ("emoji", 'emoji1', ["file name1"]),
  ("data", ' after after2'),
  ("emoji", 'emoji2', ["file name2"]),
]
"""
import re

VARIATION_SELECTOR_16 = u"\uFE0F"
ZERO_WIDTH_JOINER = u"\u200D"
COMBINING_ENCLOSING_KEYCAP = u"\u20E3"
REGIONAL_INDICATOR_RANGE = u"\U0001F1E6-\U0001F1FF"
SKIN_TONE_RANGE = u"\U0001F3FB-\U0001F3FF"
TAG_RANGE = u"\U000E0020-\U000E007E"
CANCEL_TAG = u"\U000E007F"
BLACK_FLAG = u"\U0001F3F4"


EMOJI_ELEMENT_RANGE = (
  u"\u00A9\u00AE\u203C\u2049\u2122\u2139\u2194-\u21AA\u231A-\u231B"
  u"\u2328\u23CF\u23E9-\u23FA\u24C2\u25AA-\u25FE\u2600-\u27BF"
  u"\u2934-\u2935\u2B05-\u2B55\u3030\u303D\u3297\u3299"
  u"\U0001F000-\U0001F1E5\U0001F200-\U0001FAFF"
)


TEXT_PRESENTATION_CHARACTER_SET = frozenset(
  u"\u00A9\u00AE\u203C\u2049\u2122\u2139\u2194\u2195\u2196\u2197\u2198"
  u"\u2199\u21A9\u21AA\u2328\u23CF\u23ED\u23EE\u23EF\u23F1\u23F2\u23F8"
  u"\u23F9\u23FA\u24C2\u25AA\u25AB\u25B6\u25C0\u25FB\u25FC\u2934\u2935"
  u"\u2B05\u2B06\u2B07\u3030\u303D\u3297\u3299"
)

EMOJI_ELEMENT = u"[%(element)s]%(vs16)s?[%(skin_tone)s]?" % {
  "element": EMOJI_ELEMENT_RANGE,
  "vs16": VARIATION_SELECTOR_16,
  "skin_tone": SKIN_TONE_RANGE,
}
EMOJI_RE = re.compile(
  u"(?:[%(regional_indicator)s]{2}"                    # flag
  u"|%(black_flag)s[%(tag)s]+%(cancel_tag)s"           # subdivision flag
  u"|[0-9#*]%(vs16)s?%(keycap)s"                       # keycap
  u"|%(element)s(?:%(zwj)s%(element)s)*)"              # element, ZWJ joined
  % {
    "regional_indicator": REGIONAL_INDICATOR_RANGE,
    "black_flag": BLACK_FLAG,
    "tag": TAG_RANGE,
    "cancel_tag": CANCEL_TAG,
    "vs16": VARIATION_SELECTOR_16,
    "keycap": COMBINING_ENCLOSING_KEYCAP,
    "element": EMOJI_ELEMENT,
    "zwj": ZERO_WIDTH_JOINER,
  }
)

def emojiToCodepointStringList(cluster):
  as_is = "-".join("%x" % ord(c) for c in cluster)
  without_vs16 = "-".join(
    "%x" % ord(c) for c in cluster if c != VARIATION_SELECTOR_16)
  if without_vs16 == as_is:
    return [as_is]
  return [as_is, without_vs16]

result = []
position = 0
for match in EMOJI_RE.finditer(text):
  cluster = match.group()
  if len(cluster) == 1 and cluster in TEXT_PRESENTATION_CHARACTER_SET:
    # defaults to text presentation, like @
    continue
  if position < match.start():
    result.append(("data", text[position:match.start()]))
  result.append(("emoji", cluster, emojiToCodepointStringList(cluster)))
  position = match.end()
if position < len(text) or not result:
  result.append(("data", text[position:]))
return result
