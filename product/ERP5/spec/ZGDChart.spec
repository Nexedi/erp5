Name:               ZGDChart
Summary:            gdchart-based product to draw charts in zope
Version:            0.6.4
Release:            1mdk
Group:              Development/Python
Requires:           zope
License:            GPL
URL:                http://www.zope.org/Members/teyc/ZGDChart
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
A simple chart class which generates plots dynamically using data from 
DTML or ZSQL. The output image format is PNG. For the SQL case, the 
chart plots the first two columns of a SQL query result.

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.so $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/setup $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.pyd $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.bat $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
install %{name}-%{version}/www/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/test
install %{name}-%{version}/test/*.html $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/test
install %{name}-%{version}/test/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/test

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/temp
install %{name}-%{version}/temp/*.pyd $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/temp
install %{name}-%{version}/temp/*.so $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/temp

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/manage
install %{name}-%{version}/manage/*.js $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/manage
install %{name}-%{version}/manage/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/manage
install %{name}-%{version}/manage/editPie $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/manage

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/import
install %{name}-%{version}/import/*.zexp $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/import
install %{name}-%{version}/import/*.xml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/import

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/solaris
install %{name}-%{version}/solaris/*.so $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/solaris
install %{name}-%{version}/solaris/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/solaris

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help


%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc CHANGES.TXT README.txt version.txt

%{_libdir}/zope/lib/python/Products/%{name}/

#----------------------------------------------------------------------
%changelog
* Tue Feb 10 2004 Sebastien Robin <seb@nexedi.com> 0.6.4-1nxd
- Initial release
