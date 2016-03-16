# this is made to be sure that captcha image will not be cached
container.REQUEST.RESPONSE.setHeader('Pragma', 'no-cache')

request = context.REQUEST
now = DateTime()
expire_timeout_days = 90
session_id = request.get('erp5_captcha_session_id', None)
if session_id is None:
  ## first call so generate session_id and send back via cookie
  session_id = context.browser_id_manager.getBrowserId(create=1) # generate it yourself
  request.RESPONSE.setCookie('erp5_captcha_session_id', session_id, expires=(now +expire_timeout_days).fCommon(), path='/') 

# get session
session = context.portal_sessions[session_id]

captcha_file_path = context.getTempFileName()
bg_file = context.generateBgFile(120, 40)
captcha_text = context.getRandomText()
image_data = context.makeCaptcha(text=captcha_text, bg_file=bg_file,
            captcha_file_path=captcha_file_path)

session['captcha_text']=captcha_text
session['captcha_image_path']=captcha_file_path

return image_data
