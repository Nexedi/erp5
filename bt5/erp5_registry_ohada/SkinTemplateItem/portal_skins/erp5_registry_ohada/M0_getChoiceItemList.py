"""
This script gets the person characteristics and then calls the script that 
finds the most suitable candidate
"""
person_first_name = context.getFirstName()
person_last_name = context.getLastName()
person_start_date = context.getStartDate()
person_birthplace = context.getDefaultBirthplaceAddressCity()
person_title = context.getTitle()

return context.PersonModule_getBestCandidateList(person_first_name,person_last_name,person_title,
                                                 person_start_date,person_birthplace)
