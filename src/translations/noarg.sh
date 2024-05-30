#!/bin/sh
files=`ls *.ts`
tmp_file=/tmp/noarg.sh.txt
for file in $files; do
  cat $file | sed 's/%1/{0}/g' | sed 's/%2/{1}/g' | sed 's/%3/{2}/g' > $tmp_file
  mv $tmp_file $file
done
