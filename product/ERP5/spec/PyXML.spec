%{expand: %%define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%define name	PyXML
%define version	0.8.2
%define release	3mdk

Name:		%{name}
Version:	%{version}
Release:	%{release}
URL:		http://pyxml.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/pyxml/PyXML-%{version}.tar.bz2
License:	Apacheish License
Group:		System/Libraries
Summary:	XML libraries for python
Requires:	python
BuildRequires:	python
BuildRequires:	python-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot
Distribution:	Mandrake Linux

%description
An XML package for Python. The distribution contains a validating XML parser,
an implementation of the SAX and DOM programming interfaces and an interface
to the Expat parser.

%prep
%setup -q

%build
CFLAGS="$RPM_OPT_FLAGS" python setup.py build --without-xpath --without-xslt

%install
rm -fr $RPM_BUILD_ROOT
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES \
--without-xpath --without-xslt

python -O %{_libdir}/python%{pyver}/compileall.py \
$RPM_BUILD_ROOT%{_libdir}/python%{pyver}/site-packages

# expat support is broken in 0.7.1 and 0.8.0 - removing for now
find $RPM_BUILD_ROOT%{_libdir}/python%{pyver} -name "*pyo" | \
sed "s|$RPM_BUILD_ROOT||" >> INSTALLED_FILES
grep -v %{_docdir} INSTALLED_FILES |grep -v LC_MESSAGES > installed_files

%clean
rm -rf $RPM_BUILD_ROOT

%files -f installed_files 
%defattr(-,root,root)
%doc LICENCE ANNOUNCE CREDITS README README.dom README.pyexpat README.sgmlop TODO doc/*
%lang(de) %{_libdir}/python%{pyver}/site-packages/*/dom/de/LC_MESSAGES/4Suite.mo
%lang(en_US) %{_libdir}/python%{pyver}/site-packages/*/dom/en_US/LC_MESSAGES/4Suite.mo
%lang(fr_FR) %{_libdir}/python%{pyver}/site-packages/*/dom/fr_FR/LC_MESSAGES/4Suite.mo

%changelog
* Tue Feb 17 2004 Sebastien Robin <seb@nexedi.com> 0.8.2-3mdk
- change to mandrake extension

* Tue Mar 25 2003 David Walluck <david@anti-microsoft.org> 0.8.2-2plf
- spec file cleanups

* Sun Jan 26 2003 David Walluck <david@anti-microsoft.org> 0.8.2-1plf
- release

