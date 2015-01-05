#!/bin/bash
set -e
# mono environment variables
. ${IROOT}/mono.installed

sed -i 's|localhost|'"$DBHOST"'|g' src/Web.config
# extra cleaning
rm -rf src/bin src/obj

xbuild src/ServiceStackBenchmark.csproj /t:Clean
xbuild src/ServiceStackBenchmark.csproj /t:Build

# xsp
MONO_OPTIONS=--gc=sgen xsp4 --port 8080 --nonstop &