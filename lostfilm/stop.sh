#!/bin/bash

for process in firefox Xvfb
do
	for pid in `ps -A | grep $process`
	do
		kill $pid;
	done
done