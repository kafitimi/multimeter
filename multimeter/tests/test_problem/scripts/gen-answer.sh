#!/usr/bin/env bash
if [ "$#" -ne "4" ]; then
    read
fi
if [ "$1" = "" ]; then
    read
fi
if [ "$2" = "" ]; then
    read
fi
if [ ! -f "$1" ]; then
    read
fi
cp "$1" fire.in
echo "Running solution solution.cpp"
wine solutions/solution.exe
if [ "$?" -ne "0" ]; then
    echo "Solution returned non-zero exit code"
    read
fi
rm -f fire.in
if [ ! -f "fire.out" ]; then
    echo "Solution didn't produced output [fire.out]"
    read
fi
mv "fire.out" "$2"
echo "Running checker"
wine check.exe "$1" "$2" "$2"
if [ "$?" -ne "0" ] && [ "$?" -ne "7" ]; then
    echo "Checker exit code is not equal to 0 and 7"
    read
fi
