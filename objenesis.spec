Name:		objenesis
Version:	3.6
Release:	2
Summary:	Instantiates Java objects without calling a constructor
Group:		Development/Java
License:	ASL 2.0
URL:		https://objenesis.org/
Source0:	https://github.com/easymock/objenesis/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Gradle 9.9.1 strictly pins 2.6. The 3.6 jar stays the default file.
# The wrapper jar is not in this archive.
Source1:	https://github.com/easymock/objenesis/archive/refs/tags/2.6.tar.gz#/objenesis-2.6.tar.gz
Patch0:		objenesis-2.6-jdk27-defineclass.patch

BuildArch:	noarch
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven

%description
Objenesis instantiates a Java object without calling its constructor.
3.6 builds on Java 26 and fixes the cache used when Objenesis is
loaded from a parent class loader. The main jar and the exotic jar
are shipped. Tests are skipped. Gradle 9.9.1 also strictly pins
2.6, so that jar is installed beside 3.6 under a different file name.

%prep
%setup -q -n %{name}-%{version}
%setup -q -T -D -a 1 -n %{name}-%{version}
find objenesis-2.6 -name '*.jar' -delete
patch -p1 < %{PATCH0}
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
# maven-bundle-plugin 5.1.9 is a build extension. Sysjar keeps that
# versionless use because the parent only pins the version, and Maven
# resolves the extension before the build. The jar plugin points at the
# manifest that plugin would have written. The other three plugins are
# the same kind of pin and are not packaged.
python - <<'PY'
import xml.etree.ElementTree as ET
from pathlib import Path

ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
drop = {
    "maven-bundle-plugin",
    "license-maven-plugin",
    "maven-remote-resources-plugin",
    "maven-timestamp-plugin",
}

def local(tag):
    return tag.rsplit("}", 1)[-1]

for name in ("main/pom.xml", "exotic/pom.xml"):
    path = Path(name)
    tree = ET.parse(path)
    root = tree.getroot()
    removed = []
    manifests = 0
    for parent in root.iter():
        for child in list(parent):
            if local(child.tag) == "manifestFile":
                parent.remove(child)
                manifests += 1
                continue
            if local(child.tag) != "plugin":
                continue
            artifact = ""
            for item in child:
                if local(item.tag) == "artifactId":
                    artifact = (item.text or "").strip()
            if artifact in drop:
                parent.remove(child)
                removed.append(artifact)
    missing = sorted(drop - set(removed))
    if missing:
        raise SystemExit(f"{name} still expected {missing}")
    if manifests != 1:
        raise SystemExit(f"{name} removed {manifests} manifestFile entries")
    tree.write(path, encoding="ISO-8859-1", xml_declaration=True)
PY

%build -a
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
mkdir -p obj26/classes
find objenesis-2.6/main/src/main -name '*.java' > obj26/sources.list
test -s obj26/sources.list
"$JAVA_HOME/bin/javac" -source 8 -target 9 -encoding UTF-8 -Xlint:-options \
	--add-exports jdk.unsupported/sun.misc=ALL-UNNAMED \
	-d obj26/classes @obj26/sources.list
"$JAVA_HOME/bin/jar" cf obj26/objenesis.jar -C obj26/classes .
cat > obj26/objenesis.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.objenesis</groupId>
  <artifactId>objenesis</artifactId>
  <version>2.6</version>
  <name>Objenesis</name>
  <description>Instantiate Java objects without calling a constructor.</description>
  <url>https://objenesis.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
</project>
EOF

%install -p
sysjar install --buildroot %{buildroot} \
	--artifact obj26/objenesis.pom:obj26/objenesis.jar \
	--file-name objenesis-2.6 \
	--filelist .mfiles26
# The 3.6 install owns objenesis.sysjar. Keep 2.6 on its own index
# file so both mvn() versions are provided.
/bin/mv %{buildroot}/usr/share/sysjar/index/org.objenesis/objenesis.sysjar \
	%{buildroot}/usr/share/sysjar/index/org.objenesis/objenesis-2.6.sysjar
sed -i 's|/usr/share/sysjar/index/org.objenesis/objenesis\.sysjar|/usr/share/sysjar/index/org.objenesis/objenesis-2.6.sysjar|' .mfiles26

%install -a
while IFS= read -r line; do
	grep -qxF -- "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
done < .mfiles26

%check -a
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
cat > ObSmoke.java << 'EOF'
public class ObSmoke {
	public static void main(String[] args) throws Exception {
		String expect = args[0];
		org.objenesis.Objenesis obj = new org.objenesis.ObjenesisStd();
		Object value = obj.newInstance(java.util.ArrayList.class);
		if (!(value instanceof java.util.ArrayList)) {
			throw new AssertionError(value);
		}
		System.out.println(expect + " " + value.getClass().getSimpleName());
	}
}
EOF
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{buildroot}%{_javadir}/objenesis.jar ObSmoke.java
"$JAVA_HOME/bin/java" -cp "%{buildroot}%{_javadir}/objenesis.jar:." ObSmoke objenesis36_ok | tee check36.log
grep -F -q 'objenesis36_ok ArrayList' check36.log
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{buildroot}%{_javadir}/objenesis-2.6.jar ObSmoke.java
"$JAVA_HOME/bin/java" --add-exports jdk.unsupported/sun.misc=ALL-UNNAMED \
	-cp "%{buildroot}%{_javadir}/objenesis-2.6.jar:." ObSmoke objenesis26_ok | tee check26.log
grep -F -q 'objenesis26_ok ArrayList' check26.log

%files -f .mfiles
%doc LICENSE.txt README.md
