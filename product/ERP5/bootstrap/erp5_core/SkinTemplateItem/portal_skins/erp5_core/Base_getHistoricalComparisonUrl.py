serial = getattr(brain, 'serial', '0.0.0.0')
next_serial = getattr(brain, 'next_serial', '0.0.0.0')

if serial != '0.0.0.0':
  return 'Base_viewHistoricalComparison?serial=%s&amp;next_serial=%s&amp;time=%s'\
      % ( serial, next_serial, brain.time )
