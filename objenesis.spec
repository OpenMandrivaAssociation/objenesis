Name:		objenesis
Version:	3.6
Release:	1
Summary:	Instantiates Java objects without calling a constructor
Group:		Development/Java
License:	ASL 2.0
URL:		https://objenesis.org/
Source0:	https://github.com/easymock/objenesis/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:	noarch
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven

%description
Objenesis instantiates a Java object without calling its constructor.
3.6 builds on Java 26 and fixes the cache used when Objenesis is
loaded from a parent class loader. The main jar and the exotic jar
are shipped. Tests are skipped.

%prep
%setup -q -n %{name}-%{version}
# The TCK shades a second copy of the library. The benchmark needs
# JMH and Byte Buddy. module-test turns on for every current JDK and
# only runs a test.
python - <<'PY'
from pathlib import Path
path = Path("pom.xml")
text = path.read_text()
old_modules = """  <modules>
    <module>test</module>
    <module>main</module>
    <module>exotic</module>
    <module>tck</module>
  </modules>
"""
new_modules = """  <modules>
    <module>main</module>
    <module>exotic</module>
  </modules>
"""
profile = """    <profile>
      <id>module-test</id>
      <activation>
        <jdk>[9,</jdk>
      </activation>
      <modules>
        <module>module-test</module>
      </modules>
    </profile>
"""
if old_modules not in text:
    raise SystemExit("module list not found")
if profile not in text:
    raise SystemExit("module-test profile not found")
text = text.replace(old_modules, new_modules, 1).replace(profile, "", 1)
if "<module>tck</module>" in text or "<module>module-test</module>" in text:
    raise SystemExit("dropped module still listed")
path.write_text(text)
PY

%files -f .mfiles
%doc LICENSE.txt README.md
