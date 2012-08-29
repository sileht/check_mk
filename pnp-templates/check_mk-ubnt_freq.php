<?php
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mehdi Abaakouk 2012             sileht@sileht.net      |
# +------------------------------------------------------------------+
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

$opt[1] = "--vertical-label \"MHz\"  -l 4800 -u 6000 --title \"Frequency\" ";

$def[1] = "DEF:var1=$RRDFILE[1]:$DS[1]:MAX ";
$def[1] .= "AREA:var1#800040:\"Frequency\:\" ";
$def[1] .= "GPRINT:var1:LAST:\"%2.0lfMHz\" ";
$def[1] .= "LINE1:var1#800040:\"\" ";
$def[1] .= "GPRINT:var1:MAX:\"(Max\: %2.0lfMHz,\" ";
$def[1] .= "GPRINT:var1:MIN:\"Min\: %2.0lfMHz,\" ";
$def[1] .= "GPRINT:var1:AVERAGE:\"Avg\: %2.0lfMHz)\" ";


?>
