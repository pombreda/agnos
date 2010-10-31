#!/bin/bash

AGNOS_TOOLCHAIN_VERSION=`python -c "import agnos_compiler;print agnos_compiler.AGNOS_TOOLCHAIN_VERSION"`

if [ "$1" == "upload" ] ; then
	UPLOAD="yes"
else
	UPLOAD="no"
fi

if [ "$UPLOAD" == "yes" ]; then
	pushd tests
	./all.sh
	if [ $? -ne 0 ]; then
		echo "unit test failed"
		exit 1
	fi
	popd
fi

rm -rf release
mkdir release

###############################################################################
# compiler
###############################################################################

pushd agnos_compiler
rm -rf dist
rm setup.py
sed -e "s/__AGNOS_TOOLCHAIN_VERSION__/$AGNOS_TOOLCHAIN_VERSION/" _setup.py > setup.py
python setup.py sdist --formats=gztar,zip
python setup.py bdist --formats=egg,wininst --plat-name="win32"
rm setup.py
rm -rf build
rm -rf *.egg-info
popd
mkdir release/agnos_compiler
cp agnos_compiler/dist/* release/agnos_compiler
rm -rf agnos_compiler/dist

###############################################################################
# python
###############################################################################

pushd libagnos/python
rm -rf dist
rm setup.py
sed -e "s/__AGNOS_TOOLCHAIN_VERSION__/$AGNOS_TOOLCHAIN_VERSION/" _setup.py > setup.py
python setup.py sdist --formats=gztar,zip
python setup.py bdist --formats=egg,wininst --plat-name="win32"
rm setup.py
rm -rf build
rm -rf *.egg-info
cd dist
rename 's/(.+)-[^-]+\.([twz].*)/lib$1-python.$2/' *
rename 's/(.+)-[^-]+\-py(.+)\.egg/lib$1-python-$2.egg/' *.egg
popd

mkdir -p release/libagnos/python
cp libagnos/python/dist/* release/libagnos/python
rm -rf libagnos/python/dist


###############################################################################
# java
###############################################################################
mkdir -p release/agnos-java/src
mkdir -p release/libagnos/java

cp libagnos/java/src/*.java release/agnos-java/src/
cp libagnos/java/SConstruct release/agnos-java/
pushd release
tar -czf libagnos-java.tar.gz agnos-java
zip -r libagnos-java.zip agnos-java
pushd agnos-java
scons
popd

mv libagnos-java.* libagnos/java
mv agnos-java/agnos.jar libagnos/java/agnos.jar
rm -rf agnos-java
popd


###############################################################################
# C#
###############################################################################
mkdir -p release/agnos-csharp/src/Properties
mkdir -p release/libagnos/csharp

cp libagnos/csharp/src/*.cs release/agnos-csharp/src/
cp libagnos/csharp/src/Properties/*.cs release/agnos-csharp/src/Properties/
cp libagnos/csharp/src/*.csproj release/agnos-csharp/src/
cp libagnos/csharp/src/*.sln release/agnos-csharp/src/

pushd release
tar -czf libagnos-csharp.tar.gz agnos-csharp
zip -r libagnos-csharp.zip agnos-csharp
mv libagnos-csharp.* libagnos/csharp/

pushd agnos-csharp/src
xbuild Agnos.sln
popd
mv agnos-csharp/src/bin/*/Agnos.dll libagnos/csharp/
rm -rf agnos-csharp
popd


###############################################################################
# C++
###############################################################################
mkdir -p release/agnos-cpp/src
mkdir -p release/libagnos/cpp

cp libagnos/cpp/*.sln release/agnos-cpp/
cp libagnos/cpp/*.vcxproj release/agnos-cpp/
cp libagnos/cpp/SConstruct release/agnos-cpp/
cp libagnos/cpp/src/*.cpp release/agnos-cpp/src/
cp libagnos/cpp/src/*.hpp release/agnos-cpp/src/

pushd release
tar -czf libagnos-cpp.tar.gz agnos-cpp 
zip -r libagnos-cpp.zip agnos-cpp
mv libagnos-cpp.* libagnos/cpp/

if [ "$UPLOAD" == "yes" ]; then
	pushd agnos-cpp
	scons
	popd
fi

rm -rf agnos-cpp
popd

###############################################################################
# wrap it up
###############################################################################
# pushd release
# 
# mkdir agnos-toolchain
# mkdir agnos-toolchain/cpp
# mkdir agnos-toolchain/csharp
# mkdir agnos-toolchain/java
# mkdir agnos-toolchain/python
# 
# cp *.zip *.exe *.egg agnos-toolchain
# cp cpp/*.zip agnos-toolchain/cpp
# cp csharp/*.zip csharp/*.dll agnos-toolchain/csharp
# cp java/*.zip java/*.jar agnos-toolchain/java
# cp python/*.zip python/*.exe python/*.egg agnos-toolchain/python
# 
# zip -r agnos-toolchain-$AGNOS_TOOLCHAIN_VERSION-win32.zip agnos-toolchain
# rm -rf agnos-toolchain
# 
# mkdir agnos-toolchain
# mkdir agnos-toolchain/cpp
# mkdir agnos-toolchain/csharp
# mkdir agnos-toolchain/java
# mkdir agnos-toolchain/python
# 
# cp *.tar.gz *.egg agnos-toolchain
# cp cpp/*.tar.gz agnos-toolchain/cpp
# cp csharp/*.tar.gz csharp/*.dll agnos-toolchain/csharp
# cp java/*.tar.gz java/*.jar agnos-toolchain/java
# cp python/*.tar.gz python/*.egg agnos-toolchain/python
# 
# tar -czf agnos-toolchain-$AGNOS_TOOLCHAIN_VERSION-posix.tar.gz agnos-toolchain
# rm -rf agnos-toolchain
# 
# mkdir libagnos
# mkdir libagnos/cpp
# mkdir libagnos/csharp
# mkdir libagnos/java
# mkdir libagnos/python
# 
# cp cpp/*.zip libagnos/cpp
# cp csharp/*.zip csharp/*.dll libagnos/csharp
# cp java/*.zip java/*.jar libagnos/java
# cp python/*.zip python/*.exe python/*.egg libagnos/python
# 
# zip -r libagnos-$AGNOS_TOOLCHAIN_VERSION-win32.zip libagnos
# rm -rf libagnos
# 
# mkdir libagnos
# mkdir libagnos/cpp
# mkdir libagnos/csharp
# mkdir libagnos/java
# mkdir libagnos/python
# 
# cp cpp/*.tar.gz libagnos/cpp
# cp csharp/*.tar.gz csharp/*.dll libagnos/csharp
# cp java/*.tar.gz java/*.jar libagnos/java
# cp python/*.tar.gz python/*.egg libagnos/python
# 
# tar -czf libagnos-$AGNOS_TOOLCHAIN_VERSION-posix.tar.gz libagnos
# rm -rf libagnos
# 
# rm agnos_compiler*
# rm -rf cpp
# rm -rf csharp
# rm -rf java
# rm -rf python
# 
# popd

###############################################################################
# upload
###############################################################################

if [ "$UPLOAD" != "yes" ]; then
	exit
fi

echo "=========================================================================="
echo "uploading to sourceforge. ENTER to continue, CTRL+C to skip"
read

rsync -v release/ gangesmaster,agnos@frs.sourceforge.net:/home/frs/project/a/ag/agnos/$AGNOS_TOOLCHAIN_VERSION/


