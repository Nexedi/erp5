portal = context.getPortalObject()

def getSubstitutionMappingDict():
  destination = event_value.getDestinationValue()
  kw['event_value_source_title'] = event_value.getSourceTitle()

  if destination is not None:
    kw['third_party_reference'] = destination.getDestinationReference()
    kw['address'] = (destination.getDefaultAddressText() or '').upper()
    kw['email'] = destination.getDefaultEmailText() or ''
    kw['telephone'] = destination.getDefaultTelephoneText() or ''
    kw['mobile'] = destination.getMobileTelephoneText() or ''
    kw['creation_date'] = destination.getCreationDate()

    if destination.getPortalType() == 'Person':
      kw['first_name'] = destination.getFirstName()
      kw['last_name'] = destination.getLastName()
      kw['social_title'] = destination.getSocialTitleTranslatedTitle("")
      kw['third_party_name'] = destination.getTitle()
      if destination.getSocialTitle():
        kw['third_party_name'] = "%s %s" % (destination.getSocialTitleTranslatedTitle() or '',
                                                    destination.getTitle())
    elif destination.getPortalType() == 'Organisation':
      kw['social_title'] = str(portal.Base_translateString("Participant"))
      kw['third_party_name'] = destination.getCorporateName() or destination.getTitle()


    # Backward compatibility
    kw["destination_title"] = destination.getTitle()
    kw["destination_portal_type"] = destination.getTranslatedPortalType()
    kw["destination_social_title"] = destination.getProperty('social_title_translated_title')
    kw["destination_reference"] = destination.getReference()
  else:
    kw["destination_title"] = ""
    kw["destination_portal_type"] = ""
    kw["destination_social_title"] = ""
    kw["destination_reference"] = ""

  kw['event_value_start_date'] = event_value.getStartDate()
  kw['event_value_nature'] = event_value.getResourceReference()
  kw['event_value_reference'] = event_value.getReference()
  kw['ticket_reference'] = event_value.getDefaultFollowUpReference()
  hmac = portal.Base_getHMACHexdigest(key=portal.Base_getEventHMACKey(), message=event_value.getId())
  kw["image_parameters"] = "/Base_openEvent?id=%s&hash=%s" %(event_value.getId(), hmac)
  kw["newsletter_parameters"] = "/Base_readEvent?id=%s&hash=%s" %(event_value.getId(), hmac)
  kw["unsubscribe_parameters"] = "/Base_unsubscribeFromEvent?id=%s&hash=%s" %(event_value.getId(), hmac)

  # Backward compatibility
  kw["source_title"] = event_value.getSourceTitle() or '',
  kw["document_parameters"] = "/Base_readEvent?id=%s&hash=%s" %(event_value.getId(), hmac),


  return kw

if context.hasLanguage():
  with context.getPortalObject().Localizer.translationContext(context.getLanguage()):
    return getSubstitutionMappingDict()
return getSubstitutionMappingDict()
