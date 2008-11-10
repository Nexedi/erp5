##############################################################################
# Contributors :
#                    Nando Quintana <email@nandoquintana.com>
#                    Fabien Morin <fabien@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from PIL import ImageFont, Image, ImageDraw, ImageFilter
from random import randrange, uniform
from string import zfill
from md5 import md5
from tempfile import NamedTemporaryFile
import sys, os
import commands
from zLOG import LOG, TRACE, WARNING, ERROR, INFO

FONT_FILE = '/usr/share/fonts/TTF/dejavu/DejaVuSansMono.ttf'
INITIAL_FONT_SIZE = 250
MARGIN_TOP = 5
MARGIN_BOTTOM = 5
MARGIN_LEFT = 5
MARGIN_RIGHT = 5
MAX_BG = 5

def generateBgFile(size_x, size_y):
  """
    generate a randomize background image and return the filename of the
    generated file
  """
  tmp_file = NamedTemporaryFile()
  tmp_file_name = tmp_file.name
  tmp_file.close()

  if not os.path.exists('/usr/bin/convert'):
    raise ValueError, "convert command is not installed"
  convert_options = 'plasma:fractal -blur 0x5 -shade 120x45 -normalize'
  #convert_options = 'plasma:fractal'
  cmd = '/usr/bin/convert -size %sx%s %s jpg:%s' % (size_x, size_y, 
                                            convert_options, tmp_file_name)
  result = commands.getstatusoutput(cmd)
  if result[0] !=0:
    LOG('generateBgFile :', ERROR, 'convert command'\
        'failed with the following error message : \n%s' % result[1]) 
  return tmp_file_name

def getRandomText():
  """
    return a 7 random caracters string
  """
  text_seed = md5()
  text_seed.update(str(uniform(1, 10000000000000000)))
  text = text_seed.hexdigest()
  return text[-7:]

def generateCaptcha():
  """
    used for local tests
  """
  captcha_file = NamedTemporaryFile()
  captcha_file_path = captcha_file.name
  captcha_file.close()

  bg_file = generateBgFile(300, 100)
  makeCaptcha(text=getRandomText(), bg_file=bg_file,
      captcha_file_path=captcha_file_path)

def getTempFileName():
  """
    return a tempory filename
  """
  tmp_file = NamedTemporaryFile()
  tmp_file_name = tmp_file.name
  tmp_file.close()
  return tmp_file_name


def makeCaptcha(text, bg_file, captcha_file_path):
  """ 
    generate a captcha with the text and the bg_file
    The new captcha file will be save in captcha_file_path
  """ 

  image = Image.open(bg_file)
  draw = ImageDraw.Draw(image)
  image_width = image.size[0]
  image_height = image.size[1]
  viewport_width = image_width - (MARGIN_LEFT + MARGIN_RIGHT)
  viewport_height = image_height - (MARGIN_TOP + MARGIN_BOTTOM)

  length = len(text)
   
  size = INITIAL_FONT_SIZE
  font = ImageFont.truetype(FONT_FILE, size)
  text_width = font.getsize(text)[0]
  text_height = font.getsize(text)[1]
   
  # set the good font size for this image
  while text_width > viewport_width or text_height > viewport_height :
    size -= 1
    font = ImageFont.truetype(FONT_FILE, size)
    text_width = font.getsize(text)[0]
    text_height = font.getsize(text)[1]

  font = ImageFont.truetype(FONT_FILE, size)
  text_width = font.getsize(text)[0]
  text_height = font.getsize(text)[1]
  
  l = int((viewport_width-text_width)/2)+MARGIN_LEFT
  t = int((viewport_height-text_height)/2)+MARGIN_TOP
  draw.text((l,t), text, font=font, fill='black')
           
  image.save(captcha_file_path,'PNG')
  image_data = open(captcha_file_path).read()

  # delete temp files
  os.remove(captcha_file_path)
  os.remove(bg_file)

  return image_data


if __name__ == "__main__":
  generateCaptcha()
