Name:               CPS
Summary:            internal or external web content strategy in a collaborative approach
Version:            3.0b3
Release:            1mdk
Group:              Development/Python
Requires:           zope BTreeFolder2 Localizer TranslationService
License:            GPL
URL:                http://www.cps-project.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
Collaborative Portal Server (CPS), Nuxeo's flagship solution, empowers 
your internal or external web content strategy in a collaborative 
approach. CPS is the ideal solution to create, share and turn the 
information of your organisation into value.

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore
install %{name}-%{version}/CPSCore/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore
install %{name}-%{version}/CPSCore/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore
install %{name}-%{version}/CPSCore/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/doc
install %{name}-%{version}/CPSCore/doc/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/doc
install %{name}-%{version}/CPSCore/doc/*.html $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/doc
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/zmi
install %{name}-%{version}/CPSCore/zmi/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/zmi
install %{name}-%{version}/CPSCore/zmi/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/zmi
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/drafts
install %{name}-%{version}/CPSCore/drafts/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/drafts
install %{name}-%{version}/CPSCore/drafts/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/drafts
install %{name}-%{version}/CPSCore/drafts/*.css $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/drafts
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/tests
install %{name}-%{version}/CPSCore/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSCore/tests
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault
install %{name}-%{version}/CPSDefault/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault
install %{name}-%{version}/CPSDefault/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault
install %{name}-%{version}/CPSDefault/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/Extensions
install %{name}-%{version}/CPSDefault/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/Extensions
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/doc
install %{name}-%{version}/CPSDefault/doc/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/doc
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/doc/__internal__
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/i18n
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_default
install %{name}-%{version}/CPSDefault/skins/cps_default/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_default
install %{name}-%{version}/CPSDefault/skins/cps_default/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_default
install %{name}-%{version}/CPSDefault/skins/cps_default/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_default
install %{name}-%{version}/CPSDefault/skins/cps_default/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_default
install %{name}-%{version}/CPSDefault/skins/cps_default/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_default
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_devel
install %{name}-%{version}/CPSDefault/skins/cps_devel/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_devel
install %{name}-%{version}/CPSDefault/skins/cps_devel/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_devel
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_images
install %{name}-%{version}/CPSDefault/skins/cps_images/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_images
install %{name}-%{version}/CPSDefault/skins/cps_images/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_images
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_javascript
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_styles
install %{name}-%{version}/CPSDefault/skins/cps_styles/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_styles
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_styles/nuxeo
install %{name}-%{version}/CPSDefault/skins/cps_styles/nuxeo/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_styles/nuxeo
install %{name}-%{version}/CPSDefault/skins/cps_styles/nuxeo/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_styles/nuxeo
install %{name}-%{version}/CPSDefault/skins/cps_styles/nuxeo/*.props $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_styles/nuxeo
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_styles/nuxeo_ns4
install %{name}-%{version}/CPSDefault/skins/cps_styles/nuxeo_ns4/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/skins/cps_styles/nuxeo_ns4
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/tests
install %{name}-%{version}/CPSDefault/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/tests
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/tests/puffin
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/zmi
install %{name}-%{version}/CPSDefault/zmi/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDefault/zmi
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument
install %{name}-%{version}/CPSDocument/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument
install %{name}-%{version}/CPSDocument/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument
install %{name}-%{version}/CPSDocument/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/Extensions
install %{name}-%{version}/CPSDocument/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/Extensions
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/doc
install %{name}-%{version}/CPSDocument/doc/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/doc
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/i18n
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/skins/cps_document
install %{name}-%{version}/CPSDocument/skins/cps_document/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/skins/cps_document
install %{name}-%{version}/CPSDocument/skins/cps_document/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/skins/cps_document
install %{name}-%{version}/CPSDocument/skins/cps_document/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/skins/cps_document
install %{name}-%{version}/CPSDocument/skins/cps_document/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/skins/cps_document
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/tests
install %{name}-%{version}/CPSDocument/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/tests
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/zmi
install %{name}-%{version}/CPSDocument/zmi/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSDocument/zmi
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas
install %{name}-%{version}/CPSSchemas/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas
install %{name}-%{version}/CPSSchemas/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas
install %{name}-%{version}/CPSSchemas/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/Extensions
install %{name}-%{version}/CPSSchemas/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/Extensions
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/doc
install %{name}-%{version}/CPSSchemas/doc/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/doc
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/i18n
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/skins/cps_jscalendar
install %{name}-%{version}/CPSSchemas/skins/cps_jscalendar/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/skins/cps_jscalendar
install %{name}-%{version}/CPSSchemas/skins/cps_jscalendar/*.css $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/skins/cps_jscalendar
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/skins/cps_jscalendar/lang
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/skins/cps_schemas
install %{name}-%{version}/CPSSchemas/skins/cps_schemas/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/skins/cps_schemas
install %{name}-%{version}/CPSSchemas/skins/cps_schemas/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/skins/cps_schemas
install %{name}-%{version}/CPSSchemas/skins/cps_schemas/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/skins/cps_schemas
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/tests
install %{name}-%{version}/CPSSchemas/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/tests
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/zmi
install %{name}-%{version}/CPSSchemas/zmi/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/CPSSchemas/zmi
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz
install %{name}-%{version}/Epoz/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz
install %{name}-%{version}/Epoz/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz/skins/epoz
install %{name}-%{version}/Epoz/skins/epoz/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz/skins/epoz
install %{name}-%{version}/Epoz/skins/epoz/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz/skins/epoz
install %{name}-%{version}/Epoz/skins/epoz/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz/skins/epoz
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz/Extensions
install %{name}-%{version}/Epoz/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/Epoz/Extensions
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories
install %{name}-%{version}/NuxMetaDirectories/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories
install %{name}-%{version}/NuxMetaDirectories/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories
install %{name}-%{version}/NuxMetaDirectories/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/i18n
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/zmi
install %{name}-%{version}/NuxMetaDirectories/zmi/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/zmi
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/import
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/skins
install %{name}-%{version}/NuxMetaDirectories/skins/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/skins
install %{name}-%{version}/NuxMetaDirectories/skins/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/skins/cps_nuxmetadirectories
install %{name}-%{version}/NuxMetaDirectories/skins/cps_nuxmetadirectories/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/skins/cps_nuxmetadirectories
install %{name}-%{version}/NuxMetaDirectories/skins/cps_nuxmetadirectories/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/skins/cps_nuxmetadirectories
install %{name}-%{version}/NuxMetaDirectories/skins/cps_nuxmetadirectories/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/skins/cps_nuxmetadirectories
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxUserGroups
install %{name}-%{version}/NuxUserGroups/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxUserGroups
install %{name}-%{version}/NuxUserGroups/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxUserGroups
install %{name}-%{version}/NuxUserGroups/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxUserGroups
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxUserGroups/zmi
install %{name}-%{version}/NuxUserGroups/zmi/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/NuxUserGroups/zmi
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/OrderedFolderSupportPatch
install %{name}-%{version}/OrderedFolderSupportPatch/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/OrderedFolderSupportPatch
install %{name}-%{version}/OrderedFolderSupportPatch/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/OrderedFolderSupportPatch
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms
install %{name}-%{version}/PortalTransforms/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms
install %{name}-%{version}/PortalTransforms/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms
install %{name}-%{version}/PortalTransforms/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/CVS/Base
install %{name}-%{version}/PortalTransforms/CVS/Base/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/CVS/Base
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/bin
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/www
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/www/CVS/Base
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/docs
install %{name}-%{version}/PortalTransforms/docs/*.html $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/docs
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/docs/CVS/Base
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/zope
install %{name}-%{version}/PortalTransforms/zope/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/zope
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/zope/CVS/Base
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/transforms
install %{name}-%{version}/PortalTransforms/transforms/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/transforms
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/transforms/CVS/Base
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/skins/mimetypes_icons
install %{name}-%{version}/PortalTransforms/skins/mimetypes_icons/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/skins/mimetypes_icons
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/tests
install %{name}-%{version}/PortalTransforms/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/tests
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/tests/CVS/Base
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/tests/input
install %{name}-%{version}/PortalTransforms/tests/input/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/tests/input
install %{name}-%{version}/PortalTransforms/tests/input/*.html $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/tests/input
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/tests/output
install %{name}-%{version}/PortalTransforms/tests/output/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/tests/output
install %{name}-%{version}/PortalTransforms/tests/output/*.html $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/tests/output
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/libtransforms
install %{name}-%{version}/PortalTransforms/libtransforms/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/libtransforms
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/Extensions
install %{name}-%{version}/PortalTransforms/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/Extensions
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/mime_types
install %{name}-%{version}/PortalTransforms/mime_types/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/mime_types
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/mime_types/CVS/Base
install %{name}-%{version}/PortalTransforms/mime_types/CVS/Base/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/mime_types/CVS/Base
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/unsafe_transforms
install %{name}-%{version}/PortalTransforms/unsafe_transforms/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/unsafe_transforms
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/PortalTransforms/unsafe_transforms/CVS/Base
%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,zope,zope,0755)
%doc INSTALL.txt UPGRADE.txt COPYRIGHT.txt COPYING.txt CHANGES
%{_libdir}/zope/lib/python/Products/CPSCore/
%{_libdir}/zope/lib/python/Products/CPSDefault/
%{_libdir}/zope/lib/python/Products/CPSDocument/
%{_libdir}/zope/lib/python/Products/CPSSchemas/
%{_libdir}/zope/lib/python/Products/Epoz/
%{_libdir}/zope/lib/python/Products/NuxMetaDirectories/
%{_libdir}/zope/lib/python/Products/NuxUserGroups/
%{_libdir}/zope/lib/python/Products/OrderedFolderSupportPatch/
%{_libdir}/zope/lib/python/Products/PortalTransforms/
#----------------------------------------------------------------------
%changelog
* Tue Feb 06 2004 Sebastien Robin <seb@nexedi.com> 3.0b3-1mdk
- Initial Release

