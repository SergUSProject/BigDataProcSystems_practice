#!/bin/bash

case "$1" in
    master)
        echo "Stopping Master..."
	# TODO
        ;;
    worker)
        echo "Stopping Worker..."
	# TODO
        ;;
    *)
        echo $"Usage: $0 {master|worker}" 1>&2
        exit 1
esac 
