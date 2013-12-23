%_javapackages_macros
# Copyright (c) 2000-2009, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

Summary:        A library for instantiating Java objects
Name:           objenesis
Version:        1.2
Release:        16.0%{?dist}

License:        ASL 2.0
URL:            http://objenesis.org/
# svn export http://objenesis.googlecode.com/svn/tags/1_2/ objenesis-1.2
# tar cfJ objenesis-1.2.tar.xz objenesis-1.2
Source0:        %{name}-%{version}.tar.xz

# Skipping website (requires xsite), this patch is unused atm
#Patch0:         objenesis-website-pom.patch

# Remove deps for test scope (unavailable); fix
# maven-license-plugin groupID to latest version available.
Patch1:         001-objenesis-fix-build.patch
Patch2:         JRockitInstantntiatorCharacters.patch

BuildRequires:  jpackage-utils
BuildRequires:  java-devel
BuildRequires:  junit
BuildRequires:  maven-local
BuildRequires:  maven-shade-plugin
BuildRequires:  maven-license-plugin
BuildRequires:  maven-timestamp-plugin
BuildRequires:  xpp3-minimal
BuildRequires:  objectweb-asm
BuildRequires:  apache-resource-bundles

BuildArch:      noarch

%description
Objenesis is a small Java library that serves one purpose: to instantiate 
a new object of a particular class.
Java supports dynamic instantiation of classes using Class.newInstance(); 
however, this only works if the class has an appropriate constructor. There 
are many times when a class cannot be instantiated this way, such as when 
the class contains constructors that require arguments, that have side effects,
and/or that throw exceptions. As a result, it is common to see restrictions 
in libraries stating that classes must require a default constructor. 
Objenesis aims to overcome these restrictions by bypassing the constructor 
on object instantiation. Needing to instantiate an object without calling 
the constructor is a fairly specialized task, however there are certain cases 
when this is useful:
* Serialization, Remoting and Persistence - Objects need to be instantiated 
  and restored to a specific state, without invoking code.
* Proxies, AOP Libraries and Mock Objects - Classes can be sub-classed without 
  needing to worry about the super() constructor.
* Container Frameworks - Objects can be dynamically instantiated in 
  non-standard ways.


%package javadoc

Summary:        Javadoc for %{name}
BuildArch:      noarch

%description javadoc
This package contains the API documentation for %{name}.


# Skipped till xsite avilable in fedora
#%%package manual

#Summary:        Documents for %%{name}
#
#%%description manual
#This package contains the %%{name} manual.


%prep
%setup -q 
#%%patch0 -b .sav0
%patch1 -p1
%patch2 -p2

# Enable generation of pom.properties (rhbz#1017850)
%pom_xpath_remove pom:addMavenDescriptor


%build
# tests are skipped because of missing dependency spring-osgi-test
%mvn_build -- -Dyear=2009 -Dmaven.test.skip=true

# Below is for manual (requires xsite), skipped
#pushd website
#mvn-jpp -e \
#        -s ${M2SETTINGS} \
#        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
#        -Dmaven2.jpp.depmap.file=%%{SOURCE1} \
#        antrun:run 
#popd


%install
%mvn_install


%files -f .mfiles
%dir %{_javadir}/%{name}
%doc LICENSE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt


%changelog
* Thu Oct 10 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.2-16
- Enable generation of pom.properties
- Resolves: rhbz#1017850

* Sun Sep 08 2013 Mat Booth <fedora@matbooth.co.uk> - 1.2-15
- Update for latest guidelines, rhbz #992389

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1.2-12
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon May 14 2012 Guido Grazioli <guido.grazioli@gmail.com> 1.2-10
- Update to current Java packaging guidelines
- Remove maven-eclipse-plugin BR

* Mon Feb 20 2012 Jiri Vanek <jvanek@redhat.com> 1.2-9
- Added patch2 - JRockitInstantntiatorCharacters.patch to fix unmappable characters
- Added build requires  apache-resource-bundles and  maven-remote-resources-plugin

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon May 09 2011 Guido Grazioli <guido.grazioli@gmail.com> 1.2-7
- Improve project description

* Thu Feb 24 2011 Guido Grazioli <guido.grazioli@gmail.com> 1.2-6
- Build with mvn-rpmbuild
- Fix License
- Comment on skipped tests

* Fri Feb 04 2011 Guido Grazioli <guido.grazioli@gmail.com> 1.2-5
- Build with maven 3

* Sun Jan 23 2011 Guido Grazioli <guido.grazioli@gmail.com> 1.2-4
- Drop buildroot and %%clean section
- Drop use of maven2-settings.xml and jpp-depmap.xml
- Install unversioned jars
- Clean up of needed patch and mvn-jpp execution

* Tue Jan 18 2011 Guido Grazioli <guido.grazioli@gmail.com> 1.2-3
- Fix build in rawhide

* Sat Dec 04 2010 Guido Grazioli <guido.grazioli@gmail.com> 1.2-2
- Fix build in rawhide
- Update to new Java Packaging Guidelines

* Mon May 10 2010 Guido Grazioli <guido.grazioli@gmail.com> 1.2-1
- Update to 1.2

* Thu May 06 2010 Guido Grazioli <guido.grazioli@gmail.com> 1.0-1
- Import from JPackage 

* Fri Feb 27 2009 Ralph Apel <r.apel at r-apel.de> 0:1.0-2.jpp5
- BR xpp3-minimal and fix depmap accordingly
- Disown poms and fragments dirs

* Wed Jun 18 2008 Ralph Apel <r.apel at r-apel.de> 0:1.0-1.jpp5
- First release
