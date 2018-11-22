#!/bin/bash

direction="$1"
distance="$2"
angle="$3"
deviation="$4"

DISTANCE_THRESHOLD=100

if (( distance >= DISTANCE_THRESHOLD )); then
    case "$direction" in
        "left")
            /usr/bin/i3-msg workspace next
            ;;
        "right")
            /usr/bin/i3-msg workspace prev
            ;;
    esac
fi