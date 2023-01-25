if active_process_path is not None:

  failed_line_count = len(context.Base_getReportFailedResultList(
                                       active_process_path=active_process_path))
  if failed_line_count > 0:
    return 'Import Report: %s line(s) failed over %s' % \
              (len(context.Base_getReportFailedResultList(active_process_path=active_process_path)),
               len(context.Base_getReportResultList(active_process_path=active_process_path)))
  else:
    return '%s lines imported sucessfully' % \
                      len(context.Base_getReportResultList(active_process_path=active_process_path))

raise AttributeError('Unable to get the active process')
