question = request.get('field_my_default_credential_question_question', request.get('my_default_credential_question_question')) or \
        request.get('field_your_default_credential_question_question', request.get('your_default_credential_question_question'))
question_free_text = request.get('field_my_default_credential_question_question_free_text',
                       request.get('my_default_credential_question_question_free_text')) or \
                         request.get('field_your_default_credential_question_question_free_text',
                           request.get('your_default_credential_question_question_free_text'))
if question and question_free_text:
  return 0
return 1
