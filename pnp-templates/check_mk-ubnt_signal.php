<?php
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2012             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
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

$opt[1] = "--vertical-label \"dBm\"  -l -100 -u -30 --title \"Signal\" ";

$color = sprintf("ff%02x80", $ACT[1] * -3 , $ACT[1] * -2);

$def[1] = "DEF:var1=$RRDFILE[1]:$DS[1]:MAX ";
$def[1] .= "AREA:var1#$color:\"Signal\:\" ";
$def[1] .= "GPRINT:var1:LAST:\"%2.0lfC\" ";
$def[1] .= "LINE1:var1#800040:\"\" ";
$def[1] .= "GPRINT:var1:MAX:\"(Max\: %2.0lfC,\" ";
$def[1] .= "GPRINT:var1:AVERAGE:\"Avg\: %2.0lfC)\" ";
$def[1] .= "HRULE:$WARN[1]#FFFF00:\"Warning\: $WARN[1]dBm\" ";
$def[1] .= "HRULE:$CRIT[1]#FF0000:\"Critical\: $CRIT[1]dBm\" ";

$opt[2] = "--vertical-label \"mbps\" -l 0 -u 100 --title \"RX\" ";
$def[2] = "DEF:var2=$RRDFILE[2]:$DS[2]:MIN ";
$def[2] .= "AREA:var2#80e0c0:\"RX\:\" ";
$def[2] .= "GPRINT:var2:LAST:\"%2.0lfmbps\" ";
$def[2] .= "LINE1:var2#008040:\"\" ";
$def[2] .= "GPRINT:var2:MIN:\"(Min\: %2.0lfmbps,\" ";
$def[2] .= "GPRINT:var2:AVERAGE:\"Avg\: %2.0lfmbps,\" ";
$def[2] .= "GPRINT:var2:MAX:\"Max\: %2.0lfmbps)\" ";
#$def[2] .= "HRULE:$CRIT[1]#FF0000:\"Critical\: $CRIT[1]%\" ";

$opt[3] = "--vertical-label \"mbps\" -l 0 -u 100 --title \"TX\" ";
$def[3] = "DEF:var3=$RRDFILE[3]:$DS[3]:MIN ";
$def[3] .= "AREA:var3#2389C6:\"TX\:\" ";
$def[3] .= "GPRINT:var3:LAST:\"%2.0lfmbps\" ";
$def[3] .= "LINE1:var3#013482:\"\" ";
$def[3] .= "GPRINT:var3:MIN:\"(Min\: %2.0lfmbps,\" ";
$def[3] .= "GPRINT:var3:AVERAGE:\"Avg\: %2.0lfmbps,\" ";
$def[3] .= "GPRINT:var3:MAX:\"Max\: %2.0lfmbps)\" ";
#$def[3] .= "HRULE:$CRIT[1]#FF0000:\"Critical\: $CRIT[1]%\" ";

?>
