Name:               CMF
Summary:            A Content Management System based on Zope
Version:            1.3.0
Release:            11mdk
Group:              Development/Python
Requires:           zope
License:            GPL
URL:                http://cmf.zope.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2
Patch1: CMF_local_context_worklist.patch
Patch2: CMF_dcworkflow_high_speed.patch

#----------------------------------------------------------------------
%description
Zope CMF is a content management framework based on the Zope
application server. The Zope CMF rpm package contains a complete Zope
CMF distribution including CMFWiki (a CMF based Wiki) and DCWorkflow
(a CMF based worflow).

http://cmf.zope.org

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
%setup -q
%patch1 -p1
%patch2 -p1

#----------------------------------------------------------------------
#%build

#----------------------------------------------------------------------
%install

#---------------------- CMF Calendar ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar
install CMFCalendar/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar
install CMFCalendar/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar
install CMFCalendar/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/Extensions
install CMFCalendar/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/Extensions

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/help
install CMFCalendar/help/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/skins/calendar
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/skins/zpt_calendar
install CMFCalendar/skins/calendar/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/skins/calendar
install CMFCalendar/skins/calendar/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/skins/calendar
install CMFCalendar/skins/calendar/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/skins/calendar
install CMFCalendar/skins/zpt_calendar/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/skins/zpt_calendar
install CMFCalendar/skins/zpt_calendar/*.css $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/skins/zpt_calendar
install CMFCalendar/skins/zpt_calendar/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/skins/zpt_calendar

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/tests
install CMFCalendar/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/tests

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/www
install CMFCalendar/www/*.zpt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCalendar/www

#---------------------- CMF Collector ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector
install CMFCollector/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector
install CMFCollector/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/dtml
install CMFCollector/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/dtml

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/Extensions
install CMFCalendar/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/Extensions

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/help
install CMFCalendar/help/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/skins/collector
install CMFCollector/skins/collector/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/skins/collector
install CMFCollector/skins/collector/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/skins/collector
install CMFCollector/skins/collector/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/skins/collector

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/tests
install CMFCollector/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCollector/tests

#---------------------- CMF Core ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore
install CMFCore/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore
install CMFCore/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore
install CMFCore/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore/dtml
install CMFCore/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore/dtml

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore/images
install CMFCore/images/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore/images

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore/interfaces
install CMFCore/interfaces/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore/interfaces

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore/tests
install CMFCore/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFCore/tests

#---------------------- CMF Default ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault
install CMFDefault/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault
install CMFDefault/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault
install CMFDefault/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/dtml
install CMFDefault/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/dtml

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/Extensions
install CMFDefault/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/Extensions

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/help
install CMFDefault/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/images
install CMFDefault/images/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/images

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/content
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/control
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/generic
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/Images
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/no_css
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/nouvelle
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_content
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_control
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_generic
install CMFDefault/skins/content/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/content
install CMFDefault/skins/content/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/content
install CMFDefault/skins/content/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/content
install CMFDefault/skins/control/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/control
install CMFDefault/skins/control/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/control
install CMFDefault/skins/generic/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/generic
install CMFDefault/skins/generic/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/generic
install CMFDefault/skins/Images/*.jpg $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/Images
install CMFDefault/skins/Images/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/Images
install CMFDefault/skins/no_css/*.props $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/no_css
install CMFDefault/skins/nouvelle/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/nouvelle
install CMFDefault/skins/nouvelle/*.props $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/nouvelle
install CMFDefault/skins/zpt_content/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_content
install CMFDefault/skins/zpt_content/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_content
install CMFDefault/skins/zpt_generic/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_generic
install CMFDefault/skins/zpt_generic/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_generic
install CMFDefault/skins/zpt_generic/*.css $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_generic
install CMFDefault/skins/zpt_generic/*.html $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_generic
install CMFDefault/skins/zpt_control/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_control
install CMFDefault/skins/zpt_control/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/skins/zpt_control

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/scripts
install CMFDefault/scripts/*.pys $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/scripts

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/interfaces
install CMFDefault/interfaces/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/interfaces

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/tests
install CMFDefault/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/tests
install CMFDefault/tests/*.jpg $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFDefault/tests

#---------------------- CMF Staging ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging
install CMFStaging/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging
install CMFStaging/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging
install CMFStaging/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins/staging
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins/tidy
install CMFStaging/skins/staging/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins/staging
install CMFStaging/skins/staging/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins/staging
install CMFStaging/skins/staging/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins/staging
install CMFStaging/skins/staging/*.gif.properties $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins/staging
install CMFStaging/skins/tidy/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins/tidy
install CMFStaging/skins/tidy/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins/tidy
install CMFStaging/skins/tidy/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/skins/tidy

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/tests
install CMFStaging/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/tests

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/www
install CMFStaging/www/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/www
install CMFStaging/www/*.zpt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFStaging/www

#---------------------- CMF Topic ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic
install CMFTopic/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic
install CMFTopic/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/Extensions
install CMFTopic/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/Extensions

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/help
install CMFTopic/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/interfaces
install CMFTopic/interfaces/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/interfaces

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/skins/topic
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/skins/zpt_topic
install CMFTopic/skins/topic/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/skins/topic
install CMFTopic/skins/topic/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/skins/topic
install CMFTopic/skins/topic/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/skins/topic
install CMFTopic/skins/zpt_topic/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/skins/zpt_topic

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/tests
install CMFTopic/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTopic/tests

#---------------------- CMF Tracker ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTracker
install CMFTracker/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTracker

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTracker/help
install CMFTracker/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTracker/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTracker/interfaces
install CMFTracker/interfaces/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTracker/interfaces

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTracker/tests
install CMFTracker/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFTracker/tests

#---------------------- CMF Wiki ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki
install CMFWiki/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki
install CMFWiki/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/default_wiki_content
install CMFWiki/default_wiki_content/*.wiki $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/default_wiki_content

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/Extensions
install CMFWiki/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/Extensions

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/skins/wiki
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/skins/zpt_wiki
install CMFWiki/skins/wiki/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/skins/wiki
install CMFWiki/skins/wiki/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/skins/wiki
install CMFWiki/skins/wiki/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/skins/wiki
install CMFWiki/skins/wiki/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/skins/wiki
install CMFWiki/skins/zpt_wiki/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/skins/zpt_wiki
install CMFWiki/skins/zpt_wiki/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/skins/zpt_wiki

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/tests
install CMFWiki/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWiki/tests

#---------------------- CMF Workspaces ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces
install CMFWorkspaces/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces
install CMFWorkspaces/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces
install CMFWorkspaces/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/skins/workspaces
install CMFWorkspaces/skins/workspaces/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/skins/workspaces
install CMFWorkspaces/skins/workspaces/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/skins/workspaces
install CMFWorkspaces/skins/workspaces/*.pt.properties $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/skins/workspaces
install CMFWorkspaces/skins/workspaces/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/skins/workspaces

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/tests
install CMFWorkspaces/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/tests

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/www
install CMFWorkspaces/www/*.zpt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/www
install CMFWorkspaces/www/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CMFWorkspaces/www

#---------------------- DCWorkflow ----------------------
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow
install DCWorkflow/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow
install DCWorkflow/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/doc
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/doc/examples
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/doc/examples/staging
install DCWorkflow/doc/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/doc
install DCWorkflow/doc/examples/staging/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/doc/examples/staging

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/dtml
install DCWorkflow/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/dtml

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/help
install DCWorkflow/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/images
install DCWorkflow/images/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/images

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/tests
install DCWorkflow/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/DCWorkflow/tests

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt LICENSE.txt

%{_libdir}/zope/lib/python/Products/CMFCalendar/
%{_libdir}/zope/lib/python/Products/CMFCollector/
%{_libdir}/zope/lib/python/Products/CMFCore/
%{_libdir}/zope/lib/python/Products/CMFDefault/
%{_libdir}/zope/lib/python/Products/CMFStaging/
%{_libdir}/zope/lib/python/Products/CMFTopic/
%{_libdir}/zope/lib/python/Products/CMFTracker/
%{_libdir}/zope/lib/python/Products/CMFWiki/
%{_libdir}/zope/lib/python/Products/CMFWorkspaces/
%{_libdir}/zope/lib/python/Products/DCWorkflow/

#----------------------------------------------------------------------
%changelog
* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 1.3.0-11mdk
- Make now signed rpm

* Thu Sep 04 2003 Sebatien Robin <seb@nexedi.com> 1.3.0-10mdk
- change in the spec file '/usr/lib' by %{_libdir}

* Wed Sep 3 2003 Sebastien Robin <sebnexedi.com> 1.3.0-9mdk
- Update spec in order to follows Mandrake Rules

* Wed Mar 5 2003 Sebastien Robin <sebnexedi.com> 1.3.0-8nxd
- Added a patch made by Jean-Paul Smets <jp@nexedi.com>
  in order to increase the DCWorflow speed

* Wed Mar 5 2003 Jean-Paul Smets <jp@nexedi.com> 1.3.0-7nxd
- Upgraded source code

* Tue Feb 18 2003 Jean-Paul Smets <jp@nexedi.com> 1.3.0-6nxd
- Improved local_roles patch

* Thu Feb 13 2003 Jean-Paul Smets <jp@nexedi.com> 1.3.0-5nxd
- Improved RPM patch handling

* Tue Jan 30 2003 Jean-Paul Smets <jp@nexedi.com> 1.3.0-4nxd
- Added patch to implement local context Role Guards in Action Lists

* Tue Jan 21 2003 Jean-Paul Smets <jp@nexedi.com> 1.3.0-3nxd
- Updated to latest CVS

* Tue Jan 7 2003 Jean-Paul Smets <jp@nexedi.com> 1.3.0-2nxd
- Updated to latest CVS

* Mon Nov 4 2002 Jean-Paul Smets <jp@nexedi.com> 1.3.0-1nxd
- Initial release
