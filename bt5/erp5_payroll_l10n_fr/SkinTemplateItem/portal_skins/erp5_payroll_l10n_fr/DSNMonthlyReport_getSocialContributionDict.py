from erp5.component.module.DateUtils import addToDate

portal = context.getPortalObject()

# record base and rate for each ctp for an Establishment
fee_per_ctp_dict = {}
# record bases for each contribution for each employee
individual_fee_dict = {}
# list all ctps for which the firm contributes
done_ctp_set = set()
# for bloc S21.G00.81, only type '266' for the moment
transport_individual_fee = {}
# store the relative minimum salary for each employee for thecice contribution
cice_relative_min_salary = {}
# store the relative minimum salary for each employee for the "Fillon" reduction
fillon_relative_min_salary = {}
fillon_individual_reduction = {}
# Social Entity corporate registration code
SOCIAL_ENTITY = ''
# establishment paysheets belong to
current_establishement_code = portal.accounting_module[paysheet_list[0]].getDestinationSectionValue().getCorporateRegistrationCode()[-5:]

# Rate to apply to bases to calculate the final amount of fees
standard_rate_mapping = {'012D': 0.28, '027D': 0.00016, '100D': 0.1954, '100P': 0.1545,
                         '260D': 0.08, '332P': 0.001, '343D': 0.024, '400D': 0., '430D': 0.018,
                         '479D': 0.08, '671P': 1., '772D': 0.064, '863D': 0.2134,
                         '863P': 0.1545, '937D': 0.0025}

################################################################################
def printAsPositiveRate(number):
  "Print a float as a percentage"
  return abs(100.*float(number))


def getINSEECode(zip_code):
  insee_code_list = str(context.INSEECodeList).split('\n')
  for code in insee_code_list:
    insee_record = code.split(';')
    if zip_code == insee_record[1]:
      return insee_record[0]
  return None


def updateIndividualFeeDict(paysheet_id, temp_individual_fee_dict):
  individual_fee_dict[paysheet_id] = {}
  individual_base_code_list =(('02', '100P'),
                              ('02', '863P'),
                              ('03', '100D'),
                              ('03', '863D'),
                              ('04', '260D'),
                              ('04', '012D'),
                              ('04', '0000'),
                              ('07', '772D'),
                              ('07', '343D'),
                              ('10', '260D'), # "Base brute fiscale" is the same as "base CSG"
                              ('10', '012D'),
                              ('10', '0000'),
                              ('12', '400D'),
                              ('13', '479D'),
                              ('14', '012D'))
  for base_code, ctp_code in individual_base_code_list:
    if ctp_code in temp_individual_fee_dict:
      individual_fee_dict[paysheet_id][base_code] = individual_fee_dict[paysheet_id].get(base_code, 0.) + temp_individual_fee_dict[ctp_code]
    # Every employee doesn't contribute to every fee
    else:
      pass

################################################################################

# Paysheets are grouped by establishment, so they have a common zip code
ZIP_CODE = portal.accounting_module[paysheet_list[0]] \
            .getDestinationSectionValue().getDefaultAddressZipCode()
INSEE_CODE = getINSEECode(ZIP_CODE)


# Let's fill the dicts "fee_per_ctp_dict" and "individual_fee_dict"
for paysheet_id in paysheet_list:
  # For each paysheet, we only update once each type of "fee_per_ctp_dict"
  current_ctp_set = set()
  temp_individual_fee_dict = {}
  paysheet = portal.accounting_module[paysheet_id]
  paysheet_line_list = paysheet.PaySheetTransaction_getMovementList()
  employee = paysheet.getSourceSectionValue()
  establishment = paysheet.getDestinationSectionValue()
  enrollment_record = employee.Person_getPayrollEnrollmentRecord(establishment)

  # Trainees don't contribute to aggregated fees
  if enrollment_record.getContractType() == '29':
    individual_fee_dict[paysheet_id] = {'02': 0., '03': 0.}
    continue

  # First we need to store the legal minimun salary, proportionally to the worked time
  minimum_salary = float(paysheet.getRatioQuantityFromReference('salaire_minimum_mensuel'))
  worked_time = float(enrollment_record.getWorkingUnitQuantity())
  normal_working_time = float(enrollment_record.getStandardWorkingUnit())
  relative_minimum_salary = minimum_salary * (worked_time / normal_working_time)
  gross_salary = paysheet.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution="base_contribution/base_amount/payroll/report/salary/gross")

  for paysheet_line in paysheet_line_list:
    # we only want paysheet lines contributing to a social service related to DSN
    social_contribution_set = set(paysheet_line.getResourceValue().getUseValueList()) \
      .intersection(set(portal.portal_categories.use.social_declaration.l10n.fr.ctp.getCategoryChildValueList()))
    if len(social_contribution_set) == 0:
      continue
    # A paysheet line only contributes to only 1 social service
    social_contribution = social_contribution_set.pop()
    # if a CTP appears more than once, we only want to sum once the base
    if social_contribution.getTitle() in current_ctp_set:
      continue
    ctp = social_contribution.getTitle()
    base = getattr(paysheet_line, 'base', 0.0)
    rate = getattr(paysheet_line, 'employer_price', 0.0)
    temp_individual_fee_dict[ctp] = temp_individual_fee_dict.get(ctp, 0.) + base
    fee_per_ctp_dict[ctp] =  fee_per_ctp_dict.get(ctp, 0.) + base
    if ctp[-1] not in ('P', 'D'):
      standard_rate_mapping[ctp] = rate
    current_ctp_set.add(ctp) # Employee already contributed to this category
    if not SOCIAL_ENTITY:
      SOCIAL_ENTITY = paysheet_line.getSourceSectionValue().getCorporateRegistrationCode()
    # For transport fee
    if ctp == '900T':
      transport_individual_fee[paysheet_id] = (float(base), SOCIAL_ENTITY, abs(float(base)*float(rate)), INSEE_CODE)
    # For "Fillon" reduction fee
    if ctp == '671P':
      fillon_relative_min_salary[paysheet_id] = relative_minimum_salary
      fillon_individual_reduction[paysheet_id] = base

  # Let's compute CTP 400D, which doesn't appear on paysheet
  # 400D only applies if gross salary is lower than a maximum
  other_information_dict = paysheet.PaySheetTransaction_getOtherInformationsDataDict()
  year_to_date_gross_salary = float(other_information_dict['year_to_date_gross_salary'])
  if year_to_date_gross_salary < 2.5 * relative_minimum_salary * int(context.getEffectiveDate().month()):
    ctp = '400D'
    cice_relative_min_salary[paysheet_id] = relative_minimum_salary
    temp_individual_fee_dict[ctp] = temp_individual_fee_dict.get(ctp, 0.) + gross_salary
    fee_per_ctp_dict[ctp] = fee_per_ctp_dict.get(ctp, 0.) + year_to_date_gross_salary
    current_ctp_set.add('400D')
  updateIndividualFeeDict(paysheet_id, temp_individual_fee_dict)
  done_ctp_set.update(current_ctp_set)


def getFeeFromDate(ctp_code, date):
  '''
  Return a list of the previous contributions for
  a specific CTP code in the older DSN
  '''
  amount_list = []
  aggregated_fee_list = context.DSNReport_getGroupedOlderValues(searched_bloc='S21.G00.23',
                                                                grouping_rubric='S21.G00.11.001',
                                                                from_date=date)
  for dsn_record in aggregated_fee_list:
    for establishment in aggregated_fee_list[dsn_record].keys():
      if establishment != current_establishement_code:
        continue
      for bloc in aggregated_fee_list[dsn_record][establishment]:
        bloc_found = 0
        for rubric, value in bloc:
          value = value.strip('\'')
          if rubric == 'S21.G00.23.001' and value == ctp_code:
            bloc_found = 1
          if rubric == 'S21.G00.23.001' and value != ctp_code:
            bloc_found = 0
          if bloc_found and rubric == 'S21.G00.23.004':
            amount_list.append(float(value))
  return (amount_list if len(amount_list) > 0 else [0])


def getFeeBlocAsDict(ctp, ctp_dict):
  """"
  Write a S21.G00.23 bloc for each ctp, helped by a record from the dict "fee_per_ctp_dict"
  """
  ctp_code = ctp[:3]
  ctp_category = ctp[-1]
  bloc = {}
  bloc["S21.G00.23.001"] = ctp_code
  bloc["S21.G00.23.002"] = ('921' if ctp_category=='P' else '920')
  # Rate is defined only for special CTPs
  if ctp_category not in ('P', 'D'):
    bloc["S21.G00.23.003"] = '%.2f'%(printAsPositiveRate(standard_rate_mapping[ctp]))
  # If CTP is Fillon deduction
  if ctp == '671P':
    bloc["S21.G00.23.005"] = "%.02f" % round(ctp_dict[ctp])
  # For 260D we need to add other "forfait social" bases too
  elif ctp == '260D':
    bloc["S21.G00.23.004"] = "%.02f" % round(ctp_dict[ctp] + ctp_dict.get('012D', 0.) + ctp_dict.get('0000', 0.))
  # All standard cases
  else:
    bloc["S21.G00.23.004"] = "%.02f" % round(ctp_dict[ctp])

  # The CTP 900T needs this specific rubric
  if ctp == '900T':
    bloc["S21.G00.23.006"] = INSEE_CODE
  return bloc

fee_total_sum = 0.0
aggregated_fee_list = []

# Write all the S21.G00.23 blocs needed
# And compute the total to pay
for ctp in sorted(done_ctp_set):
  if ctp == '0000': # for special services, we need to add the base to CSG (=260D)
    fee_total_sum += abs(fee_per_ctp_dict[ctp] * standard_rate_mapping['260D'])
    continue
  if ctp in ('100D', '863D'):
    fee_total_sum += abs(fee_per_ctp_dict[ctp] * standard_rate_mapping[ctp])
    # blocs 100D and 863D do not appear in a social declaration
    continue
  aggregated_fee_list.append(getFeeBlocAsDict(ctp, fee_per_ctp_dict))
  if ctp == '671P':
    fee_total_sum -= abs(fee_per_ctp_dict[ctp] * standard_rate_mapping[ctp])
  else:
    fee_total_sum += abs(fee_per_ctp_dict[ctp] * standard_rate_mapping[ctp])

total_payment_slip = []
total_payment_slip.append(("S21.G00.22.001", SOCIAL_ENTITY))
total_payment_slip.append(("S21.G00.22.005", "%.02f" % round(fee_total_sum)))

payment = []
payment.append(("S21.G00.20.001", SOCIAL_ENTITY))
payment.append(("S21.G00.20.005", "%.02f" % round(fee_total_sum)))

result_dict = {'total_payment_slip': total_payment_slip,
               'aggregated_fee_list': aggregated_fee_list,
               'individual_fee_dict': individual_fee_dict,
               'payment': payment,
               'transport_individual_fee': transport_individual_fee,
               'cice_relative_min_salary': cice_relative_min_salary,
               'fillon_relative_min_salary': fillon_relative_min_salary,
               'fillon_individual_reduction': fillon_individual_reduction}

return result_dict
