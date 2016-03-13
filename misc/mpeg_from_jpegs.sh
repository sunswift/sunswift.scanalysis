#!/bin/sh

mencoder "mf://$1/*.jpg" -o output.avi -mf fps=15 -ovc lavc 

#mencoder mf://$1/*.jpg -mf w=640:h=480:fps=25:type=jpg -ovc lavc \
#       -lavcopts vcodec=mpeg4:mbd=2:trell -oac copy -o output.avi