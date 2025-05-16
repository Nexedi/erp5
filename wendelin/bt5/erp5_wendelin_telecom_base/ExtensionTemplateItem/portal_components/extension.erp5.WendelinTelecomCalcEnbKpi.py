from xlte.amari import kpi as amari_kpi
from xlte import kpi
from zLOG import LOG, WARNING
import io

def load_measurements(alogm):
  mlog = kpi.MeasurementLog()
  try:
    measurement = alogm.read()
    while measurement is not None:
      try:
        mlog.append(measurement)
      except Exception as e:
        # Invalid measurement: simply skip it
        LOG('WendelinTelecomCalcOrsKpi.loadMeasurements', WARNING, "Skipped data during KPI calculation: %s" % str(e))
      measurement = alogm.read()
  except amari_kpi.LogError as e:
    # Invalid measurement: simply skip it
    LOG('WendelinTelecomCalcOrsKpi.loadMeasurements', WARNING, "Skipped data during KPI calculation: %s" % str(e))
  finally:
    alogm.close()
  return mlog

def calc_periods(mlog, tperiod):
  try:
    t = mlog.data()[0]['X.Tstart']
    for measurement in mlog.data()[1:]:
      t_ = measurement['X.Tstart']
      if (t_ - t) >= tperiod:
        calc = kpi.Calc(mlog, t, t + tperiod)
        t = calc.tau_hi
        yield calc
  except IndexError:
    # No data to read: exit
    return

def calcEnbKpi(data, t_period):
  fxlog = io.StringIO(data)
  alogm = amari_kpi.LogMeasure(fxlog, open('/dev/null', 'r'))
  mlog = load_measurements(alogm)

  # E-RAB Accessibility KPI
  vt = []
  v_initial_epsb_estab_sr = []
  v_added_epsb_estab_sr = []

  for calc in calc_periods(mlog, t_period):
    try:
      erab_accessibility = calc.erab_accessibility()
    except AssertionError as e:
      LOG('WendelinTelecomCalcOrsKpi.calcEnbKpi', WARNING, "Skipped data during KPI calculation: %s" % str(e))
      continue
    vt.append(calc.tau_lo)
    v_initial_epsb_estab_sr.append((erab_accessibility[0]['lo'], erab_accessibility[0]['hi']))
    v_added_epsb_estab_sr.append((erab_accessibility[1]['lo'], erab_accessibility[1]['hi']))

  # E-UTRAN IP Throughput KPI
  evt = []
  v_ip_throughput_qci = []

  for calc in calc_periods(mlog, t_period):
    try:
      eutran_ip_throughput = calc.eutran_ip_throughput()
    except AssertionError as e:
      LOG('WendelinTelecomCalcOrsKpi.calcEnbKpi', WARNING, "Skipped data during KPI calculation: %s" % str(e))
      continue
    period_qci_data = []
    for qci_measurement in eutran_ip_throughput:
      period_qci_data.append((
        qci_measurement['dl']['lo'],
        qci_measurement['dl']['hi'],
        qci_measurement['ul']['lo'],
        qci_measurement['ul']['hi']
       ))
    evt.append(calc.tau_lo)
    v_ip_throughput_qci.append(period_qci_data)

  kpi_data_dict = dict(
    e_rab_accessibility=(vt, v_initial_epsb_estab_sr, v_added_epsb_estab_sr),
    e_utran_ip_throughput=(evt, v_ip_throughput_qci)
  )
  return kpi_data_dict