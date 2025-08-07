#from zLOG import LOG, WARNING
import io
import json
import six

def calcOrsUeCount(data, t_period):
  fxlog = io.StringIO(data)
  ue_count_data_dict = {}
  ue_data = []
  for xlog_line in fxlog:
    try:
      xlog_line_dict = json.loads(xlog_line)
    except json.JSONDecodeError:
      raise ValueError(xlog_line)

    timestamp = xlog_line_dict.get("utc", None)  # UTC timestamp
    if timestamp is None:
      continue

    # Extract max UE count among all cells
    if "cells" in xlog_line_dict:
      for cell_id, cell_data in six.iteritems(xlog_line_dict["cells"]):
        ue_count_max = cell_data.get("ue_count_max", None)
        ue_count_min = cell_data.get("ue_count_min", None)
        ue_count_avg = cell_data.get("ue_count_avg", None)

        # XXX FIXME: I am not sure this will always be true.
        rrc_con_req = cell_data.get("counters", {})\
                               .get("messages", {})\
                               .get("rrc_connection_request", 0)

        rrc_paging = cell_data.get("counters", {})\
                               .get("messages", {})\
                               .get("rrc_paging", 0)

        rrc_recon_com = cell_data.get("counters", {})\
                               .get("messages", {})\
                               .get("rrc_connection_reconfiguration_complete", 0)

        rrc_sec_complete = cell_data.get("counters", {})\
                               .get("messages", {})\
                               .get("rrc_security_mode_complete", 0)

        rrc_sec_command = cell_data.get("counters", {})\
                               .get("messages", {})\
                               .get("rrc_security_mode_command", 0)

        # XXX END OF FIXME
        if ue_count_max is not None:
          assert ue_count_min is not None
          assert ue_count_avg is not None

          ue_data.append((timestamp, int(cell_id), ue_count_max, ue_count_min,
                          ue_count_avg, rrc_con_req, rrc_paging, rrc_recon_com,
                          rrc_sec_command, rrc_sec_complete))

  ue_count_data_dict["cell_info"] = ue_data
  return ue_count_data_dict