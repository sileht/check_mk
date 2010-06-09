#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2010             mk@mathias-kettner.de |
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

# =================================================================== #
#        _    ____ ___      ____                                      #
#       / \  |  _ \_ _|    |  _ \  ___   ___ _   _                    #
#      / _ \ | |_) | |_____| | | |/ _ \ / __| | | |                   #
#     / ___ \|  __/| |_____| |_| | (_) | (__| |_| |                   #
#    /_/   \_\_|  |___|    |____/ \___/ \___|\__,_|                   #
#                                                                     #
# =================================================================== #
# 
# A painter computes from information from a data row HTML output and
# a CSS class for one display column. Please note, that there is no
# 1:1 relation between data columns and display columns. A painter can
# make use of more than one data columns. One example is the current
# service state. It uses the columns "service_state" and "has_been_checked".
#
# A painter is a python dictionary with the following keys:
#
# "title":   Title of the column to be displayed in the view editor
#            *and* in views as column header
# "short":   If the key is defined, it is used as column header in views
#            instead of the the title
# "columns": Livestatus columns this painter need. Multisite retrieves
#            only data columns declared in the painters, so make sure
#            you do not leave out something here.
# "paint":   The actual paint function 
#
# The paint function gets one argument: A data row, which is a python
# dictionary representing one data object (host, service, ...). Its
# keys are the column names, its values the actual values from livestatus
# (typed: numbers are float or int, not string)
#
# The paint function must return a pair of two strings: The HTML code
# for painting the column and a CSS class for the TD of the column.
# That class is optional and set to "" in most cases. Currently CSS
# styles are not modular and all defined in check_mk.css. This will
# change in future.
# =================================================================== #

#    ___                    
#   |_ _|___ ___  _ __  ___ 
#    | |/ __/ _ \| '_ \/ __|
#    | | (_| (_) | | | \__ \
#   |___\___\___/|_| |_|___/
#                           


icon_columns = [ "acknowledged", "scheduled_downtime_depth", "downtimes_with_info", "comments_with_info",
	         "notifications_enabled", "is_flapping", "modified_attributes_list", "active_checks_enabled",
		 "accept_passive_checks", "action_url_expanded", "notes_url_expanded", "in_notification_period" ]

def paint_icons(what, row): # what is "host" or "service"
    output = ""
    if what == "host":
	prefix = "host_"
    else:
	 prefix = "service_"

    # action_url
    if row[prefix + "action_url_expanded"]:
	output += "<a href='%s'><img class=icon src=\"images/icon_action.gif\"></a>" % row[prefix + "action_url_expanded"]

    # notes_url
    if row[prefix + "notes_url_expanded"]:
	output += "<a href='%s'><img class=icon src=\"images/icon_notes.gif\"></a>" % row[prefix + "notes_url_expanded"]

    # Problem has been acknowledged
    if row[prefix + "acknowledged"]:
	output += '<img class=icon title="this problem has been acknowledged" src="images/icon_ack.gif">'

    # Currently we are in a downtime + link to list of downtimes for this host / service
    if row[prefix + "scheduled_downtime_depth"] > 0:
       output += link_to_view('<img class=icon src="images/icon_downtime.gif">', row, 'downtimes_of_' + what)

    # Comments
    comments = row[prefix + "comments_with_info"]
    if len(comments) > 0:
        text = ""
	for id, author, comment in comments:
	    text += "%s: \"%s\" \n" % (author, comment)
	output += link_to_view('<img class=icon title=\'%s\' src="images/icon_comment.gif">' % text, row, 'comments_of_' + what)
	
    # Notifications disabled
    if not row[prefix + "notifications_enabled"]:
	output += '<img class=icon title="notifications are disabled for this %s" src="images/icon_ndisabled.gif">' % \
		  what

    # Flapping
    if row[prefix + "is_flapping"]:
	output += '<img class=icon title="This %s is flapping" src="images/icon_flapping.gif">' % what
    
    # Setting of active checks modified by user
    if "active_checks_enabled" in row[prefix + "modified_attributes_list"]:
	if row[prefix + "active_checks_enabled"] == 0:
	    output += '<img class=icon title="Active checks have been manually disabled for this %s!" '\
		      'src="images/icon_disabled.gif">' % what
	else:
	    output += '<img class=icon title="Active checks have been manually enabled for this %s!" '\
		      'src="images/icon_enabled.gif">' % what
    
    # Passive checks disabled manually?
    if "passive_checks_enabled" in row[prefix + "modified_attributes_list"]:
	if row[prefix + "accept_passive_checks"] == 0:
	    output += '<img class=icon title="Passive checks have been manually disabled for this %s!" '\
		      'src="images/icon_npassive.gif">' % what


    if not row[prefix + "in_notification_period"]:
        output += '<img class=icon title="Out of notification period" src="images/icon_outofnot.gif">'

    return "icons", output

def iconpainter_columns(what):
    cols = [ what + "_" + c for c in icon_columns ]
    cols += [ "host_name" ]
    if what == "service":
        cols += [ "service_description" ]
    return cols

multisite_painters["service_icons"] = {
    "title" : "Service icons",
    "short" : "Icons",
    "columns" : iconpainter_columns("service"),
    "paint" : lambda row: paint_icons("service", row)
}

multisite_painters["host_icons"] = {
    "title" : "Host icons",
    "short" : "Icons",
    "columns" : iconpainter_columns("host"),
    "paint" : lambda row: paint_icons("host", row)
}

# -----------------------------------------------------------------------

def paint_nagios_link(row):
    # We need to use the Nagios-URL as configured
    # in sites.
    baseurl = config.site(row["site"])["nagios_cgi_url"]
    url = baseurl + "/extinfo.cgi?host=" + htmllib.urlencode(row["host_name"])
    svc = row.get("service_description")
    if svc:
        url += "&type=2&service=" + htmllib.urlencode(svc)
        what = "service"
    else:
        url += "&type=1"
        what = "host"
    return "singleicon", "<a href=\"%s\"><img title=\"Show this %s in Nagios\" src=\"images/icon_nagios.gif\"></a>" % (url, what)

def paint_age(timestamp, has_been_checked, bold_if_younger_than):
    if not has_been_checked:
	return "age", "-"
	   
    age = time.time() - timestamp
    if age >= 48 * 3600 or age < -48 * 3600:
	return "age", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

    # Time delta less than two days => make relative time
    if age < 0:
	age = -age
	prefix = "in "
    else:
	prefix = ""
    if age < bold_if_younger_than: 
	age_class = "age recent"
    else:
	age_class = "age"
    return age_class, prefix + html.age_text(age)

def paint_future_time(timestamp):
    if timestamp <= 0:
        return "", "-"
    else:
        return paint_age(timestamp, True, 0)

def paint_day(timestamp):
    return "", time.strftime("%A, %Y-%m-%d", time.localtime(timestamp))

def paint_site_icon(row):
    if row["site"] and config.use_siteicons:
	return None, "<img class=siteicon src=\"icons/site-%s-24.png\">" % row["site"]
    else:
	return None, ""
	
multisite_painters["sitename_plain"] = {
    "title" : "Site id",
    "short" : "Site",
    "columns" : ["site"],
    "paint" : lambda row: (None, row["site"])
}

multisite_painters["sitealias"] = {
    "title" : "Site alias",
    "columns" : ["site"],
    "paint" : lambda row: (None, config.site(row["site"])["alias"])
}

#    ____                  _               
#   / ___|  ___ _ ____   _(_) ___ ___  ___ 
#   \___ \ / _ \ '__\ \ / / |/ __/ _ \/ __|
#    ___) |  __/ |   \ V /| | (_|  __/\__ \
#   |____/ \___|_|    \_/ |_|\___\___||___/
#                                          

def paint_service_state_short(row):
    if row["service_has_been_checked"] == 1:
	state = row["service_state"]
	name = nagios_short_state_names[row["service_state"]]
    else:
	state = "p"
	name = "PEND"
    return "state svcstate state%s" % state, name

def paint_host_state_short(row):
# return None, str(row)
    if row["host_has_been_checked"] == 1:
	state = row["host_state"]
	name = nagios_short_host_state_names[row["host_state"]]
    else:
	state = "p"
	name = "PEND"
    return "state hstate hstate%s" % state, name

multisite_painters["service_nagios_link"] = {
    "title" : "Icon with link to service in Nagios GUI",
    "short" : "",
    "columns" : [ "site", "host_name", "service_description" ],
    "paint" : paint_nagios_link
}

multisite_painters["service_state"] = {
    "title" : "Service state",
    "short" : "State",
    "columns" : ["service_has_been_checked","service_state"],
    "paint" : paint_service_state_short
}

multisite_painters["site_icon"] = {
    "title" : "Icon showing the site",
    "short" : "",
    "columns" : ["site"],
    "paint" : paint_site_icon
}

multisite_painters["svc_plugin_output"] = {
    "title" : "Output of check plugin",
    "short" : "Status detail",
    "columns" : ["service_plugin_output"],
    "paint" : lambda row: (None, row["service_plugin_output"])
}
multisite_painters["svc_perf_data"] = {
    "title" : "Service performance data",
    "short" : "Perfdata",
    "columns" : ["service_perf_data"],
    "paint" : lambda row: (None, row["service_perf_data"])
}
multisite_painters["svc_check_command"] = {
    "title" : "Service check command",
    "short" : "Check command",
    "columns" : ["service_check_command"],
    "paint" : lambda row: (None, row["service_check_command"])
}
    
multisite_painters["svc_contacts"] = {
    "title" : "Service contacts",
    "short" : "Contacts",
    "columns" : ["service_contacts"],
    "paint" : lambda row: (None, ", ".join(row["service_contacts"]))
}

multisite_painters["service_description"] = {
    "title" : "Service description",
    "short" : "Service",
    "columns" : ["service_description"],
    "paint" : lambda row: (None, row["service_description"])
}

multisite_painters["svc_state_age"] = {
    "title" : "The age of the current service state",
    "short" : "Age",
    "columns" : [ "service_has_been_checked", "service_last_state_change" ],
    "paint" : lambda row: paint_age(row["service_last_state_change"], row["service_has_been_checked"] == 1, 60 * 10)
}
multisite_painters["svc_check_age"] = {
    "title" : "The time since the last check of the service",
    "short" : "Checked",
    "columns" : [ "service_has_been_checked", "service_last_check" ],
    "paint" : lambda row: paint_age(row["service_last_check"], row["service_has_been_checked"] == 1, 0)
}

multisite_painters["svc_next_check"] = {
    "title" : "The time of the next scheduled service check",
    "short" : "Next check",
    "columns" : [ "service_next_check" ],
    "paint" : lambda row: paint_future_time(row["service_next_check"])
}

multisite_painters["svc_next_notification"] = {
    "title" : "The time of the next service notification",
    "short" : "Next notification",
    "columns" : [ "service_next_notification" ],
    "paint" : lambda row: paint_future_time(row["service_next_notification"])
}

multisite_painters["svc_last_notification"] = {
    "title" : "The time of the last service notification",
    "short" : "last notification",
    "columns" : [ "service_last_notification" ],
    "paint" : lambda row: paint_age(row["service_last_notification"], row["service_last_notification"], 0)
}


multisite_painters["svc_check_latency"] = {
    "title" : "Service check latency",
    "short" : "Latency",
    "columns" : [ "service_latency" ],
    "paint" : lambda row: ("", "%.3f sec" % row["service_latency"])
}

multisite_painters["svc_check_duration"] = {
    "title" : "Service check duration",
    "short" : "Duration",
    "columns" : [ "service_execution_time" ],
    "paint" : lambda row: ("", "%.3f sec" % row["service_execution_time"])
}
multisite_painters["svc_attempt"] = {
    "title" : "Current check attempt",
    "short" : "Att.",
    "columns" : [ "service_current_attempt", "service_max_check_attempts" ],
    "paint" : lambda row: (None, "%d/%d" % (row["service_current_attempt"], row["service_max_check_attempts"]))
}

multisite_painters["svc_check_type"] = {
    "title" : "Service check type",
    "short" : "Type",
    "columns" : [ "service_check_type" ],
    "paint" : lambda row: (None, row["service_check_type"] == 0 and "ACTIVE" or "PASSIVE")
}
def paint_nagiosflag(row, field, bold_if_nonzero):
    value = row[field]
    yesno = {True:"yes", False:"no"}[value != 0]
    if (value != 0) == bold_if_nonzero:
	return "badflag", yesno
    else:
	return "goodflag", yesno

multisite_painters["svc_in_downtime"] = {
    "title" : "Currently in downtime",
    "short" : "Dt.",
    "columns" : [ "service_scheduled_downtime_depth" ],
    "paint" : lambda row: paint_nagiosflag(row, "service_scheduled_downtime_depth", True)
}
multisite_painters["svc_in_notifper"] = {
    "title" : "In notification period",
    "short" : "in notif. p.",
    "columns" : [ "service_in_notification_period" ],
    "paint" : lambda row: paint_nagiosflag(row, "service_in_notification_period", False)
}
multisite_painters["svc_notifper"] = {
   "title" : "Service notification period",
   "short" : "notif.",
   "columns" : [ "service_notification_period" ],
   "paint" : lambda row: (None, row["service_notification_period"])
}
      
multisite_painters["svc_flapping"] = {
    "title" : "Is flapping",
    "short" : "flap",
    "columns" : [ "service_is_flapping" ],
    "paint" : lambda row: paint_nagiosflag(row, "service_is_flapping", True)
}

def paint_service_group_memberlist(row):
    links = []
    for group in row["service_groups"]:
        link = "view.py?view_name=servicegroup&servicegroup=" + group
        links.append('<a href="%s">%s</a>' % (link, group))
    return "", ", ".join(links)

multisite_painters["svc_group_memberlist"] = {
    "title"   : "Servicegroups the service is member of",
    "short"   : "Groups",
    "columns" : [ "service_groups" ],
    "paint"   : paint_service_group_memberlist
}

# PNP Graphs
def paint_pnpgraph(sitename, host, service = "_HOST_"):
    site = html.site_status[sitename]["site"]
    pnpurl = site["pnp_url"]
    htmlcode = ""
    for source in [ 1, 2, 3, 4, 5, 6, 7 ]:
        urlvars = '&host=%s&srv=%s&source=%d' % ( htmllib.urlencode(host), htmllib.urlencode(service), source)
        htmlcode += '<div class=pnpgraph><a href="%s/index.php/graph?%s"><img src="%s/image?%s&view=0"></a></div>' % \
            (pnpurl, urlvars, pnpurl, urlvars)
    return "pnpgraph", htmlcode
        
multisite_painters["svc_pnpgraph" ] = {
    "title"   : "PNP service graph",
    "short"   : "PNP graph",
    "columns" : [ "host_name", "service_description" ],
    "paint"   : lambda row: paint_pnpgraph(row["site"], row["host_name"], row["service_description"])
}

#   _   _           _       
#  | | | | ___  ___| |_ ___ 
#  | |_| |/ _ \/ __| __/ __|
#  |  _  | (_) \__ \ |_\__ \
#  |_| |_|\___/|___/\__|___/
#                           

multisite_painters["host_state"] = {
    "title" : "Host state",
    "short" : "state",
    "columns" : ["host_has_been_checked","host_state"],
    "paint" : paint_host_state_short
}

multisite_painters["host_plugin_output"] = {
    "title" : "Output of host check plugin",
    "short" : "Status detail",
    "columns" : ["host_plugin_output"],
    "paint" : lambda row: (None, row["host_plugin_output"])
}

multisite_painters["host_perf_data"] = {
    "title" : "Host performance data",
    "short" : "Performance data",
    "columns" : ["host_perf_data"],
    "paint" : lambda row: (None, row["host_perf_data"])
}

multisite_painters["host_check_command"] = {
    "title" : "Host check command",
    "short" : "Check command",
    "columns" : ["host_check_command"],
    "paint" : lambda row: (None, row["host_check_command"])
}

multisite_painters["host_state_age"] = {
    "title" : "The age of the current host state",
    "short" : "Age",
    "columns" : [ "host_has_been_checked", "host_last_state_change" ],
    "paint" : lambda row: paint_age(row["host_last_state_change"], row["host_has_been_checked"] == 1, 60 * 10)
}

multisite_painters["host_check_age"] = {
    "title" : "The time since the last check of the host",
    "short" : "Checked",
    "columns" : [ "host_has_been_checked", "host_last_check" ],
    "paint" : lambda row: paint_age(row["host_last_check"], row["host_has_been_checked"] == 1, 0)
}

multisite_painters["host_next_check"] = {
    "title" : "The time of the next scheduled host check",
    "short" : "Next check",
    "columns" : [ "host_next_check" ],
    "paint" : lambda row: paint_future_time(row["host_next_check"])
}

multisite_painters["host_next_notification"] = {
    "title" : "The time of the next host notification",
    "short" : "Next notification",
    "columns" : [ "host_next_notification" ],
    "paint" : lambda row: paint_future_time(row["host_next_notification"])
}

multisite_painters["host_last_notification"] = {
    "title" : "The time of the last host notification",
    "short" : "last notification",
    "columns" : [ "host_last_notification" ],
    "paint" : lambda row: paint_age(row["host_last_notification"], row["host_last_notification"], 0)
}

multisite_painters["host_check_latency"] = {
    "title" : "Host check latency",
    "short" : "Latency",
    "columns" : [ "host_latency" ],
    "paint" : lambda row: ("", "%.3f sec" % row["host_latency"])
}

multisite_painters["host_check_duration"] = {
    "title" : "Host check duration",
    "short" : "Duration",
    "columns" : [ "host_execution_time" ],
    "paint" : lambda row: ("", "%.3f sec" % row["host_execution_time"])
}

multisite_painters["host_attempt"] = {
    "title" : "Current host check attempt",
    "short" : "Att.",
    "columns" : [ "host_current_attempt", "host_max_check_attempts" ],
    "paint" : lambda row: (None, "%d/%d" % (row["host_current_attempt"], row["host_max_check_attempts"]))
}

multisite_painters["host_check_type"] = {
    "title" : "Host check type",
    "short" : "Type",
    "columns" : [ "host_check_type" ],
    "paint" : lambda row: (None, row["host_check_type"] == 0 and "ACTIVE" or "PASSIVE")
}

multisite_painters["host_in_downtime"] = {
    "title" : "Host currently in downtime",
    "short" : "Dt.",
    "columns" : [ "host_scheduled_downtime_depth" ],
    "paint" : lambda row: paint_nagiosflag(row, "host_scheduled_downtime_depth", True)
}
multisite_painters["host_in_notifper"] = {
    "title" : "Host in notification period",
    "short" : "in notif. p.",
    "columns" : [ "host_in_notification_period" ],
    "paint" : lambda row: paint_nagiosflag(row, "host_in_notification_period", False)
}
multisite_painters["host_notifper"] = {
   "title" : "Host notification period",
   "short" : "notif.",
   "columns" : [ "host_notification_period" ],
   "paint" : lambda row: (None, row["host_notification_period"])
}
      
multisite_painters["host_pnpgraph" ] = {
    "title"   : "PNP host graph",
    "short"   : "PNP graph",
    "columns" : [ "host_name" ],
    "paint"   : lambda row: paint_pnpgraph(row["site"], row["host_name"])
}

def paint_host_black(row):
    state = row["host_state"]
    if state != 0:
        return None, "<div class=hostdown>%s</div>" % row["host_name"]
    else:
        return None, row["host_name"]

multisite_painters["host_black"] = {
    "title" : "Hostname, red background if down or unreachable",
    "short" : "Host",
    "columns" : ["site", "host_name", "host_state"],
    "paint" : paint_host_black,
}

def paint_host_black_with_link_to_old_nagios_services(row):
    host = row["host_name"]
    baseurl = config.site(row["site"])["nagios_cgi_url"]
    url = baseurl + "/status.cgi?host=" + htmllib.urlencode(host)
    state = row["host_state"]
    if state != 0:
        return None, '<div class=hostdown><a href="%s">%s</a></div>' % (url, host) 
    else:
        return None, '<a href="%s">%s</a>' % (url, host)


multisite_painters["host_black_nagios"] = {
    "title" : "Hostname, red background if down, link to Nagios services",
    "short" : "Host",
    "columns" : ["site", "host_name", "host_state"],
    "paint" : paint_host_black_with_link_to_old_nagios_services,
}


multisite_painters["host_nagios_link"] = {
    "title" : "Icon with link to host to Nagios GUI",
    "short" : "",
    "columns" : [ "site", "host_name" ],
    "paint" : paint_nagios_link
}

def paint_host_with_state(row):
    if row["host_has_been_checked"]:
        state = row["host_state"]
    else:
        state = "p"
    return "state hstate hstate%s" % state, row["host_name"]

multisite_painters["host_with_state"] = {
    "title" : "Hostname colored with state",
    "short" : "Host",
    "columns" : ["site", "host_name", "host_state", "host_has_been_checked" ],
    "paint" : paint_host_with_state, 
}

multisite_painters["host"] = {
    "title" : "Hostname",
    "short" : "Host",
    "columns" : ["host_name"],
    "paint" : lambda row: ("", row["host_name"])
}

multisite_painters["alias"] = {
    "title" : "Host alias",
    "short" : "Alias",
    "columns" : ["host_alias"],
    "paint" : lambda row: ("", row["host_alias"])
}

multisite_painters["host_address"] = {
    "title" : "Host IP address",
    "short" : "IP address",
    "columns" : ["host_address"],
    "paint" : lambda row: ("", row["host_address"])
}

def paint_svc_count(id, count):
    if count > 0:
	return "count svcstate state%s" % id, str(count)
    else:
	return "count svcstate statex", "0"

def paint_host_count(id, count):
    if count > 0:
        if id != None:
            return "count hstate hstate%s" % id, str(count)
        else: # pending
            return "count hstate hstatep", str(count)

    else:
	return "count hstate hstatex", "0"

multisite_painters["num_services"] = {
    "title"   : "Number of services",
    "short"   : "",
    "columns" : [ "host_num_services" ],
    "paint"   : lambda row: (None, str(row["host_num_services"])),
}

multisite_painters["num_services_ok"] = {
    "title"   : "Number of services in state OK",
    "short"   : "OK",
    "columns" : [ "host_num_services_ok" ],
    "paint"   : lambda row: paint_svc_count(0, row["host_num_services_ok"])
}

multisite_painters["num_problems"] = {
    "title"   : "Number of problems",
    "short"   : "Pro.",
    "columns" : [ "host_num_services", "host_num_services_ok", "host_num_services_pending" ],
    "paint"   : lambda row: paint_svc_count('s', row["host_num_services"] - row["host_num_services_ok"] - row["host_num_services_pending"]),
}

multisite_painters["num_services_warn"] = {
    "title"   : "Number of services in state WARN",
    "short"   : "Wa",
    "columns" : [ "host_num_services_warn" ],
    "paint"   : lambda row: paint_svc_count(1, row["host_num_services_warn"])
}

multisite_painters["num_services_crit"] = {
    "title"   : "Number of services in state CRIT",
    "short"   : "Cr",
    "columns" : [ "host_num_services_crit" ],
    "paint"   : lambda row: paint_svc_count(2, row["host_num_services_crit"])
}

multisite_painters["num_services_unknown"] = {
    "title"   : "Number of services in state UNKNOWN",
    "short"   : "Un",
    "columns" : [ "host_num_services_unknown" ],
    "paint"   : lambda row: paint_svc_count(3, row["host_num_services_unknown"])
}

multisite_painters["num_services_pending"] = {
    "title"   : "Number of services in state PENDING",
    "short"   : "Pd",
    "columns" : [ "host_num_services_pending" ],
    "paint"   : lambda row: paint_svc_count("p", row["host_num_services_pending"])
}

def paint_service_list(row, columnname):
    h = "<div class=objectlist>"
    for entry in row[columnname]:
        if columnname.startswith("servicegroup"):
	    host, svc, state, checked = entry
	    text = host + " ~ " + svc
	else:
	    svc, state, checked = entry
	    host = row["host_name"]
	    text = svc
        link = "view.py?view_name=service&site=%s&host=%s&service=%s" % (
		htmllib.urlencode(row["site"]),
		htmllib.urlencode(host),
		htmllib.urlencode(svc))
	if checked:
	    css = "state%d" % state
	else:
	    css = "statep"
	h += "<div class=\"%s\"><a href=\"%s\">%s</a></div>" % (css, link, text) 
    h += "</div>"
    return "", h

multisite_painters["host_services"] = {
    "title"   : "Services colored according to state",
    "short"   : "Services",
    "columns" : [ "host_name", "host_services_with_state" ],
    "paint"   : lambda row: paint_service_list(row, "host_services_with_state")
}

def paint_host_list(site, hosts):
    h = ""
    first = True
    for host in hosts:
        if first:
            first = False
        else:
            h += ", "
        link = "view.py?view_name=hoststatus&site=%s&host=%s" % (htmllib.urlencode(site), htmllib.urlencode(host))
	h += "<a href=\"%s\">%s</a></div>" % (link, host) 
    return "", h

multisite_painters["host_parents"] = {
    "title"   : "Host's parents",
    "short"   : "Parents",
    "columns" : [ "host_parents" ],
    "paint"   : lambda row: paint_host_list(row["site"], row["host_parents"])
}

multisite_painters["host_childs"] = {
    "title"   : "Host's childs",
    "short"   : "childs",
    "columns" : [ "host_childs" ],
    "paint"   : lambda row: paint_host_list(row["site"], row["host_childs"])
}

def paint_host_group_memberlist(row):
    links = []
    for group in row["host_groups"]:
        link = "view.py?view_name=hostgroup&hostgroup=" + group
        links.append('<a href="%s">%s</a>' % (link, group))
    return "", ", ".join(links)

multisite_painters["host_group_memberlist"] = {
    "title"   : "Hostgroups the host is member of",
    "short"   : "Groups",
    "columns" : [ "host_groups" ],
    "paint"   : paint_host_group_memberlist
}

#    _   _           _                                  
#   | | | | ___  ___| |_ __ _ _ __ ___  _   _ _ __  ___ 
#   | |_| |/ _ \/ __| __/ _` | '__/ _ \| | | | '_ \/ __|
#   |  _  | (_) \__ \ || (_| | | | (_) | |_| | |_) \__ \
#   |_| |_|\___/|___/\__\__, |_|  \___/ \__,_| .__/|___/
#                       |___/                |_|        
#
def paint_hg_host_list(row):
    h = "<div class=objectlist>"
    for host, state, checked in row["hostgroup_members_with_state"]:
        link = "view.py?view_name=host&site=%s&host=%s" % (
		htmllib.urlencode(row["site"]),
		htmllib.urlencode(host))
	if checked:
	    css = "hstate%d" % state
	else:
	    css = "hstatep"
	h += "<div class=\"%s\"><a href=\"%s\">%s</a></div>" % (css, link, host) 
    h += "</div>"
    return "", h

multisite_painters["hostgroup_hosts"] = {
    "title"   : "Hosts colored according to state",
    "short"   : "Hosts",
    "columns" : [ "hostgroup_members_with_state" ],
    "paint"   : paint_hg_host_list,
}

multisite_painters["hg_num_services"] = {
    "title"   : "Number of services",
    "short"   : "",
    "columns" : [ "hostgroup_num_services" ],
    "paint"   : lambda row: (None, str(row["hostgroup_num_services"])),
}

multisite_painters["hg_num_services_ok"] = {
    "title"   : "Number of services in state OK",
    "short"   : "O",
    "columns" : [ "hostgroup_num_services_ok" ],
    "paint"   : lambda row: paint_svc_count(0, row["hostgroup_num_services_ok"])
}

multisite_painters["hg_num_services_warn"] = {
    "title"   : "Number of services in state WARN",
    "short"   : "W",
    "columns" : [ "hostgroup_num_services_warn" ],
    "paint"   : lambda row: paint_svc_count(1, row["hostgroup_num_services_warn"])
}

multisite_painters["hg_num_services_crit"] = {
    "title"   : "Number of services in state CRIT",
    "short"   : "C",
    "columns" : [ "hostgroup_num_services_crit" ],
    "paint"   : lambda row: paint_svc_count(2, row["hostgroup_num_services_crit"])
}

multisite_painters["hg_num_services_unknown"] = {
    "title"   : "Number of services in state UNKNOWN",
    "short"   : "U",
    "columns" : [ "hostgroup_num_services_unknown" ],
    "paint"   : lambda row: paint_svc_count(3, row["hostgroup_num_services_unknown"])
}

multisite_painters["hg_num_services_pending"] = {
    "title"   : "Number of services in state PENDING",
    "short"   : "P",
    "columns" : [ "hostgroup_num_services_pending" ],
    "paint"   : lambda row: paint_svc_count("p", row["hostgroup_num_services_pending"])
}
multisite_painters["hg_num_hosts_up"] = {
    "title"   : "Number of hosts in state UP",
    "short"   : "Up",
    "columns" : [ "hostgroup_num_hosts_up" ],
    "paint"   : lambda row: paint_host_count(0, row["hostgroup_num_hosts_up"])
}
multisite_painters["hg_num_hosts_down"] = {
    "title"   : "Number of hosts in state DOWN",
    "short"   : "Dw",
    "columns" : [ "hostgroup_num_hosts_down" ],
    "paint"   : lambda row: paint_host_count(1, row["hostgroup_num_hosts_down"])
}
multisite_painters["hg_num_hosts_unreach"] = {
    "title"   : "Number of hosts in state UNREACH",
    "short"   : "Un",
    "columns" : [ "hostgroup_num_hosts_unreach" ],
    "paint"   : lambda row: paint_host_count(2, row["hostgroup_num_hosts_unreach"])
}
multisite_painters["hg_num_hosts_pending"] = {
    "title"   : "Number of hosts in state PENDING",
    "short"   : "Pd",
    "columns" : [ "hostgroup_num_hosts_pending" ],
    "paint"   : lambda row: paint_host_count(None, row["hostgroup_num_hosts_pending"])
}
multisite_painters["hg_name"] = {
    "title" : "Hostgroup name",
    "short" : "Name",
    "columns" : ["hostgroup_name"],
    "paint" : lambda row: (None, row["hostgroup_name"])
}
multisite_painters["hg_alias"] = {
    "title" : "Hostgroup alias",
    "short" : "Alias",
    "columns" : ["hostgroup_alias"],
    "paint" : lambda row: (None, row["hostgroup_alias"])
}

#    ____                  _                                          
#   / ___|  ___ _ ____   _(_) ___ ___  __ _ _ __ ___  _   _ _ __  ___ 
#   \___ \ / _ \ '__\ \ / / |/ __/ _ \/ _` | '__/ _ \| | | | '_ \/ __|
#    ___) |  __/ |   \ V /| | (_|  __/ (_| | | | (_) | |_| | |_) \__ \
#   |____/ \___|_|    \_/ |_|\___\___|\__, |_|  \___/ \__,_| .__/|___/
#                                     |___/                |_|        

multisite_painters["sg_services"] = {
    "title"   : "Services colored according to state",
    "short"   : "Services",
    "columns" : [ "servicegroup_members_with_state" ],
    "paint"   : lambda row: paint_service_list(row, "servicegroup_members_with_state")
}

multisite_painters["sg_num_services"] = {
    "title"   : "Number of services",
    "short"   : "",
    "columns" : [ "servicegroup_num_services" ],
    "paint"   : lambda row: (None, str(row["servicegroup_num_services"])),
}

multisite_painters["sg_num_services_ok"] = {
    "title"   : "Number of services in state OK",
    "short"   : "O",
    "columns" : [ "servicegroup_num_services_ok" ],
    "paint"   : lambda row: paint_svc_count(0, row["servicegroup_num_services_ok"])
}

multisite_painters["sg_num_services_warn"] = {
    "title"   : "Number of services in state WARN",
    "short"   : "W",
    "columns" : [ "servicegroup_num_services_warn" ],
    "paint"   : lambda row: paint_svc_count(1, row["servicegroup_num_services_warn"])
}

multisite_painters["sg_num_services_crit"] = {
    "title"   : "Number of services in state CRIT",
    "short"   : "C",
    "columns" : [ "servicegroup_num_services_crit" ],
    "paint"   : lambda row: paint_svc_count(2, row["servicegroup_num_services_crit"])
}

multisite_painters["sg_num_services_unknown"] = {
    "title"   : "Number of services in state UNKNOWN",
    "short"   : "U",
    "columns" : [ "servicegroup_num_services_unknown" ],
    "paint"   : lambda row: paint_svc_count(3, row["servicegroup_num_services_unknown"])
}

multisite_painters["sg_num_services_pending"] = {
    "title"   : "Number of services in state PENDING",
    "short"   : "P",
    "columns" : [ "servicegroup_num_services_pending" ],
    "paint"   : lambda row: paint_svc_count("p", row["servicegroup_num_services_pending"])
}
multisite_painters["sg_name"] = {
    "title" : "Servicegroup name",
    "short" : "Name",
    "columns" : ["servicegroup_name"],
    "paint" : lambda row: (None, row["servicegroup_name"])
}
multisite_painters["sg_alias"] = {
    "title" : "Servicegroup alias",
    "short" : "Alias",
    "columns" : ["servicegroup_alias"],
    "paint" : lambda row: (None, row["servicegroup_alias"])
}

# Intelligent Links to PNP4Nagios 0.6.X

def pnp_url(row):
    sitename = row["site"]
    host = row["host_name"]
    svc = row["service_description"]
    svc = svc.replace(":", "_").replace("\\", "_")
    site = html.site_status[sitename]["site"]
    url = site["pnp_url"] + ("index.php/graph?host=%s&srv=%s" % (htmllib.urlencode(host), htmllib.urlencode(svc)))
    return url


def pnp_icon_link(row):
    a = "<a href=\"%s\"><img class=icon src=\"images/icon_pnp.gif\"></a>" % pnp_url(row)

    if config.site_is_local(row["site"]):
	# Where is our RRD?
	basedir = defaults.rrd_path + "/" + row["host_name"]
	xmlpath = basedir + "/" + row["service_description"].replace("/", "_").replace(" ", "_") + ".xml"
	if os.path.exists(xmlpath):
	    return a
	else:
	    return ""
    
    # Darn. Remote site. We cannot check for a file but rather use
    # (Lars' idea) the perfdata field
    elif row["service_perf_data"]:
	return  a
    else:
	return ""
        

multisite_painters["link_to_pnp_service"] = {
    "title"   : "Link to PNP4Nagios",
    "short"   : "PNP",
    "columns" : [ "site", "host_name", "service_description", "service_perf_data"],
    "paint"   : lambda row: ("", pnp_icon_link(row))
}

#     ____                                     _       
#    / ___|___  _ __ ___  _ __ ___   ___ _ __ | |_ ___ 
#   | |   / _ \| '_ ` _ \| '_ ` _ \ / _ \ '_ \| __/ __|
#   | |__| (_) | | | | | | | | | | |  __/ | | | |_\__ \
#    \____\___/|_| |_| |_|_| |_| |_|\___|_| |_|\__|___/
#                                                      

multisite_painters["comment_id"] = {
    "title" : "Comment id",
    "short" : "ID",
    "columns" : ["comment_id"],
    "paint" : lambda row: (None, row["comment_id"])
}
multisite_painters["comment_author"] = {
    "title" : "Comment author",
    "short" : "Author",
    "columns" : ["comment_author"],
    "paint" : lambda row: (None, row["comment_author"])
}

multisite_painters["comment_comment"] = {
    "title" : "Comment text",
    "columns" : ["comment_comment"],
    "paint" : lambda row: (None, row["comment_comment"])
}

multisite_painters["comment_what"] = {
    "title" : "Comment type (host/service)",
    "short" : "Type",
    "columns" : ["comment_type"],
    "paint" : lambda row: (None, row["comment_type"] == 1 and "Host" or "Service")
}
multisite_painters["comment_time"] = {
    "title" : "Comment entry time",
    "short" : "Time",
    "columns" : ["comment_entry_time"],
    "paint" : lambda row: paint_age(row["comment_entry_time"], True, 3600)
}
multisite_painters["comment_expires"] = {
    "title" : "Comment expiry time",
    "short" : "Expires",
    "columns" : ["comment_expire_time"],
    "paint" : lambda row: paint_age(row["comment_expire_time"], row["comment_expire_time"] != 0, 3600)
}

def paint_comment_entry_type(row):
    t = row["comment_entry_type"]
    linkview = None
    if t == 1:   icon = "comment"
    elif t == 2:
	icon = "downtime"
	if row["service_description"]:
	    linkview = "downtimes_of_service"
	else:
	    linkview = "downtimes_of_host"
	
    elif t == 3: icon = "flapping"
    elif t == 4: icon = "ack"
    else:
	return "", ""
    code = '<img class=icon src="images/icon_%s.gif">' % icon
    if linkview:
	code = link_to_view(code, row, linkview)
    return "icons", code

multisite_painters["comment_entry_type"] = {
    "title" : "Comment entry type (user/downtime/flapping/ack)",
    "short" : "E.Type",
    "columns" : ["comment_entry_type", "host_name", "service_description" ],
    "paint" : paint_comment_entry_type
}

#    ____                      _   _                     
#   |  _ \  _____      ___ __ | |_(_)_ __ ___   ___  ___ 
#   | | | |/ _ \ \ /\ / / '_ \| __| | '_ ` _ \ / _ \/ __|
#   | |_| | (_) \ V  V /| | | | |_| | | | | | |  __/\__ \
#   |____/ \___/ \_/\_/ |_| |_|\__|_|_| |_| |_|\___||___/
#                                                        


multisite_painters["downtime_id"] = {
    "title" : "Downtime id",
    "short" : "ID",
    "columns" : ["downtime_id"],
    "paint" : lambda row: (None, row["downtime_id"])
}
multisite_painters["downtime_author"] = {
    "title" : "Downtime author",
    "short" : "Author",
    "columns" : ["downtime_author"],
    "paint" : lambda row: (None, row["downtime_author"])
}
multisite_painters["downtime_comment"] = {
    "title" : "Downtime comment",
    "short" : "Comment",
    "columns" : ["downtime_comment"],
    "paint" : lambda row: (None, row["downtime_comment"])
}

multisite_painters["downtime_fixed"] = {
    "title" : "Downtime is fixed",
    "short" : "Fixed",
    "columns" : ["downtime_fixed"],
    "paint" : lambda row: (None, row["downtime_fixed"] == "0" and "flexible" or "fixed")
}
multisite_painters["downtime_type"] = {
    "title" : "Downtime active or pending",
    "short" : "act/pend",
    "columns" : ["downtime_type"],
    "paint" : lambda row: (None, row["downtime_type"] == 0 and "active" or "pending")
}
multisite_painters["downtime_entry_time"] = {
    "title" : "Downtime entry time",
    "short" : "Entry",
    "columns" : ["downtime_entry_time"],
    "paint" : lambda row: paint_age(row["downtime_entry_time"], True, 3600)
}

multisite_painters["downtime_start_time"] = {
    "title" : "Downtime start time",
    "short" : "Start",
    "columns" : ["downtime_start_time"],
    "paint" : lambda row: paint_age(row["downtime_start_time"], True, 3600)
}
multisite_painters["downtime_end_time"] = {
    "title" : "Downtime end time",
    "short" : "End",
    "columns" : ["downtime_end_time"],
    "paint" : lambda row: paint_age(row["downtime_end_time"], True, 3600)
}

#    _                
#   | |    ___   __ _ 
#   | |   / _ \ / _` |
#   | |__| (_) | (_| |
#   |_____\___/ \__, |
#               |___/ 

multisite_painters["log_message"] = {
    "title" : "Log: complete message",
    "short" : "Message",
    "columns" : ["log_message"],
    "paint" : lambda row: ("", row["log_message"])
}
multisite_painters["log_plugin_output"] = {
    "title" : "Log: output of check plugin",
    "short" : "Check output",
    "columns" : ["log_plugin_output"],
    "paint" : lambda row: ("", row["log_plugin_output"])
}
multisite_painters["log_attempt"] = {
    "title" : "Log: number of check attempt",
    "short" : "Att.",
    "columns" : ["log_attempt"],
    "paint" : lambda row: ("", row["log_attempt"])
}
multisite_painters["log_state_type"] = {
    "title" : "Log: type of state (hard/soft/stopped/started)",
    "short" : "Type",
    "columns" : ["log_state_type"],
    "paint" : lambda row: ("", row["log_state_type"])
}
multisite_painters["log_type"] = {
    "title" : "Log: event",
    "short" : "Event",
    "columns" : ["log_type"],
    "paint" : lambda row: ("nowrap", row["log_type"])
}
def paint_log_icon(row):
    img = None
    log_type = row["log_type"]
    if log_type == "SERVICE ALERT":
        img = { 0: "ok", 1: "warn", 2:"crit", 3:"unknown" }.get(row["log_state"])
    elif log_type == "HOST ALERT":
        img = { 0: "up", 1: "down", 2:"unreach" }.get(row["log_state"])
    elif "DOWNTIME" in log_type:
        if row["log_state_type"] == "STOPPED":
            img = "downtimestop"
        else:
            img = "downtime"
    elif log_type.endswith("NOTIFICATION"):
        img = "notify"
    elif log_type == "EXTERNAL COMMAND":
        img = "command"
    elif "restarting..." in log_type:
        img = "restart"
    elif "starting..." in log_type:
        img = "start"
    elif "shutdown..." in log_type:
        img = "stop"

    if img:
        return "icon", '<img src="images/alert_%s.png">' % img
    else:
        return "icon", ""

multisite_painters["log_icon"] = {
    "title" : "Log: event icon",
    "short" : "",
    "columns" : ["log_type", "log_state", "log_state_type"],
    "paint" : paint_log_icon,
}
multisite_painters["log_options"] = {
    "title" : "Log: informational part of message",
    "short" : "Info",
    "columns" : ["log_options"],
    "paint" : lambda row: ("", row["log_options"])
}

multisite_painters["log_time"] = {
    "title" : "Log: entry time",
    "short" : "Time",
    "columns" : ["log_time"],
    "paint" : lambda row: paint_age(row["log_time"], True, 3600 * 24)
}

multisite_painters["log_date"] = {
    "title"   : "Log: day of entry",
    "short"   : "Date",
    "columns" : ["log_time"],
    "groupby" : lambda row: paint_day(row["log_time"])[1],
    "paint"   : lambda row: paint_day(row["log_time"])
}

def paint_log_state(row):
    state = row["log_state"]
    if row["log_service_description"]:
	return paint_service_state_short({"service_has_been_checked":1, "service_state" : state})
    else:
	return paint_host_state_short({"host_has_been_checked":1, "host_state" : state})

multisite_painters["log_state"] = {
    "title" : "Log: state of host/service at log time",
    "short" : "State",
    "columns" : ["log_state", "log_service_description"],
    "paint" : paint_log_state
}
