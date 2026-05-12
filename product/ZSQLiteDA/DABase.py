import Shared.DC.ZRDB.Connection, sys
from App.special_dtml import HTMLFile
from ExtensionClass import Base
import Acquisition

class Connection(Shared.DC.ZRDB.Connection.Connection):
    _isAnSQLConnection=1

    manage_options=Shared.DC.ZRDB.Connection.Connection.manage_options+(
        {'label': 'Browse', 'action':'manage_browse'},
        # {'label': 'Design', 'action':'manage_tables'},
        )

    manage_tables=HTMLFile('tables',globals())
    manage_browse=HTMLFile('browse',globals())

    info=None

    def tpValues(self):
        #if hasattr(self, '_v_tpValues'): return self._v_tpValues
        r=[]
        # self._v_tables=tables=TableBrowserCollection()
        #tables=tables.__dict__
        c=self._v_database_connection
        try:
            for d in c.tables(rdb=0):
                try:
                    name=d['TABLE_NAME']
                    b=TableBrowser()
                    b.__name__=name
                    b._d=d
                    b._c=c
                    #b._columns=c.columns(name)
                    b.icon=table_icons.get(d['TABLE_TYPE'],'text')
                    r.append(b)
                    # tables[name]=b
                except:
                    # print d['TABLE_NAME'], sys.exc_type, sys.exc_value
                    pass

        finally: pass #print sys.exc_type, sys.exc_value
        #self._v_tpValues=r
        return r

    def __getitem__(self, name):
        if name=='tableNamed':
            if not hasattr(self, '_v_tables'): self.tpValues()
            return self._v_tables.__of__(self)
        raise KeyError(name)

    def manage_join(self, tables, select_cols, join_cols, REQUEST=None):
        """Create an SQL join"""

    def manage_insert(self, table, cols, REQUEST=None):
        """Create an SQL insert"""

    def manage_update(self, table, keys, cols, REQUEST=None):
        """Create an SQL update"""

class TableBrowserCollection(Acquisition.Implicit):
    "Helper class for accessing tables via URLs"

class Browser(Base):
    def __getattr__(self, name):
        try: return self._d[name]
        except KeyError: raise AttributeError(name)

class values:

    def len(self): return 1

    def __getitem__(self, i):
        try: return self._d[i]
        except AttributeError: pass
        self._d=self._f()
        return self._d[i]

class TableBrowser(Browser, Acquisition.Implicit):
    icon='what'
    Description=check=''
    info=HTMLFile('table_info',globals())
    menu=HTMLFile('table_menu',globals())

    def tpValues(self):
        v=values()
        v._f=self.tpValues_
        return v

    def tpValues_(self):
        r=[]
        tname=self.__name__
        for d in self._c.columns(tname):
            b=ColumnBrowser()
            b._d=d
            b.icon=d['Icon']
            b.TABLE_NAME=tname
            r.append(b)
        return r

    def tpId(self): return self._d['TABLE_NAME']
    def tpURL(self): return "Table/%s" % self._d['TABLE_NAME']
    def Name(self): return self._d['TABLE_NAME']
    def Type(self): return self._d['TABLE_TYPE']

    manage_designInput=HTMLFile('designInput',globals())
    def manage_buildInput(self, id, source, default, REQUEST=None):
        "Create a database method for an input form"
        args=[]
        values=[]
        names=[]
        columns=self._columns
        for i in range(len(source)):
            s=source[i]
            if s=='Null': continue
            c=columns[i]
            d=default[i]
            t=c['Type']
            n=c['Name']
            names.append(n)
            if s=='Argument':
                values.append("<!--#sql-value %s type=%s-->'" %
                              (n, vartype(t)))
                a='%s%s' % (n, boboType(t))
                if d: a="%s=%s" % (a,d)
                args.append(a)
            elif s=='Property':
                values.append("<!--#sql-value %s type=%s-->'" %
                              (n, vartype(t)))
            else:
                if isStringType(t):
                    if find(d,"\'") >= 0: d=join(split(d,"\'"),"''")
                    values.append("'%s'" % d)
                elif d:
                    values.append(str(d))
                else:
                    raise ValueError(
                        'no default was given for <em>%s</em>' % n)




class ColumnBrowser(Browser):
    icon='field'

    def check(self):
        return ('\t<input type=checkbox name="%s.%s">' %
                (self.TABLE_NAME, self._d['Name']))
    def tpId(self): return self._d['Name']
    def tpURL(self): return "Column/%s" % self._d['Name']
    def Description(self): return " %s" % self._d['Description']

table_icons={
    'TABLE': 'table',
    'VIEW':'view',
    'SYSTEM_TABLE': 'stable',
    }

