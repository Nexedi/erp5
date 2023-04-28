context.activate(
  activity='SQLDict',
  tag='after_amortisation_build',
  after_tag=('build_amortisation_transaction',
             'disconnect_amortisation_transaction')
).AmortisationTransaction_afterBuild(**kw)
