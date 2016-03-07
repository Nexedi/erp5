return "https://[%s]:8080" % context.getProperty('stdout')[context.getProperty('stdout').index('[')+1:context.getProperty('stdout').index(']')]
