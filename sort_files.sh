#!/bin/bash
find $1 -name "*.encrypted"  -printf "%T@ %p\n" | sort -n


