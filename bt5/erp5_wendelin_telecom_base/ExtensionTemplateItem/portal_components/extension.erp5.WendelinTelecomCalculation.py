import io
import json
import six
from zLOG import LOG, WARNING
from xlte.amari import kpi as amari_kpi
from xlte import kpi

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
        t = calc.τ_hi
        yield calc
  except IndexError:
    # No data to read: exit
    return

def processEnbXLogData(self, data, t_period, progress_indicator=None):
  fxlog = io.StringIO(data)

  rrc_data = []
  ue_data = []
  rms_rx_data = []
  is_config_updated = False
  if progress_indicator is not None:
    last_config_dict = json.loads(progress_indicator.getLastXLogConfig('{}'))
  else:
    last_config_dict = {}
  rms_rx_index = last_config_dict.get('rms_rx_index', [])
  for xlog_line in fxlog:
    try:
      xlog_line_dict = json.loads(xlog_line)
    except json.JSONDecodeError:
      continue

    timestamp = xlog_line_dict.get("utc", None)  # UTC timestamp
    if timestamp is None:
      continue

    if xlog_line_dict.get("message", None) == 'config_get' and "cells" in xlog_line_dict:
      rms_rx_index = []
      for cell_id, cell_data in six.iteritems(xlog_line_dict["cells"]):
        rms_rx_index.extend([(cell_id, ant_id+1) for ant_id in range(0, cell_data.get("n_antenna_ul", 0))])
      is_config_updated = True

    if xlog_line_dict.get("message", None) == 'stats' and "cells" in xlog_line_dict:
      for cell_id, cell_data in six.iteritems(xlog_line_dict["cells"]):

        ue_count_max = cell_data.get("ue_count_max", None)
        ue_count_min = cell_data.get("ue_count_min", None)
        ue_count_avg = cell_data.get("ue_count_avg", None)

        if ue_count_max is not None:
          assert ue_count_min is not None
          assert ue_count_avg is not None

          ue_data.append(
            (timestamp, int(cell_id), ue_count_max, ue_count_min, ue_count_avg))

        # XXX REVIEW: I am not sure this will always be true.
        cell_message = cell_data.get("counters", {})\
                               .get("messages", None)

        if cell_message is not None:
          rrc_con_req = cell_message.get("rrc_connection_request", 0)
          rrc_paging = cell_message.get("rrc_paging", 0)
          rrc_sec_complete = cell_message.get("rrc_security_mode_complete", 0)
          rrc_sec_command = cell_message.get("rrc_security_mode_command", 0)
          rrc_recon_com = cell_message.get(
            "rrc_connection_reconfiguration_complete", 0)

          rrc_data.append((timestamp, int(cell_id), rrc_con_req, rrc_paging,
                           rrc_recon_com, rrc_sec_command, rrc_sec_complete))

      cell_samples_rx_list = xlog_line_dict.get("samples", {}).get("rx", [])
      if len(rms_rx_index) == len(cell_samples_rx_list):
        for pos, sample_rx in enumerate(cell_samples_rx_list):
          rms_rx_data.append((
            timestamp,
            int(rms_rx_index[pos][0]),  # Cell ID
            rms_rx_index[pos][1],       # Antenna ID
            sample_rx['count'],
            sample_rx['max'],
             sample_rx['rms'],
            sample_rx['rms_dbm']
          ))
      #else:
       # raise ValueError("len(rms_rx_index) %s != len(cell_samples_rx_list) %s" % (
       #   len(rms_rx_index), len(cell_samples_rx_list)))
       # XXX REVIEW: Until here.

  # Seek is faster them recreate fxlog with same data. Optionally this the block
  # below should be re-implemented inside xlte in future.
  fxlog.seek(0)

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
    vt.append(calc.τ_lo)
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
    evt.append(calc.τ_lo)
    v_ip_throughput_qci.append(period_qci_data)


  enb_xlog_data_dict = dict(
    e_rab_accessibility=(vt, v_initial_epsb_estab_sr, v_added_epsb_estab_sr),
    e_utran_ip_throughput=(evt, v_ip_throughput_qci),
    ue_count=ue_data,
    rrc=rrc_data,
    rms={'rx': rms_rx_data},
    last_rms_rx_index=rms_rx_index
  )
  if is_config_updated and progress_indicator is not None:
    progress_indicator.setLastXLogConfig(
      json.dumps({
        'utc': timestamp,
        'rms_rx_index': rms_rx_index
      }))

  return enb_xlog_data_dict
