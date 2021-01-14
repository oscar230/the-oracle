#!/usr/bin/env python3
# This is a exitmap module

import os
import sys
import logging
import random
import string
import torsocks
import time
import configparser
import csv
import datetime

#
#   LOGGER
#

log = logging.getLogger(__name__)

#
#   CONFIG LOADER
#

config_path = "theoracle.conf"

def get_config(section, variable):
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
    except Exception as ex:
        print("Failed to read config, exception: " + str(ex))
        exit(-1)
    else:
        #print("Read config successfully.")
        return config.get(section, variable)

def get_white_flag():
    return get_config("DOMAIN", "WhiteFlag")

def get_subdomain_base():
    return get_config("DOMAIN", "SubDomainBase")

def get_subdomain_length():
    return get_config("DOMAIN", "SubDomainLength")

def get_resolves():
    return get_config("DOMAIN", "Resolves")

def get_output_directory():
    return get_config("OUTPUT", "ResultDirectory")

def get_tries():
    return get_config("DOMAIN", "Tries")

#
#   CSV AND SAVING RESULTS
#

result_directory = str(get_output_directory() + "/" + datetime.datetime.now().isoformat())

def setup_result_directory():
    try:
        if (os.path.isdir(str(get_output_directory())) == False):
            os.mkdir(str(get_output_directory()))
        if (os.path.isdir(result_directory) == False):
            os.mkdir(result_directory)
    except Exception as ex:
        log.error("Result directory exception " + str(ex))

def save_results_as_csv(filename, data):
    with open(str(result_directory + "/" + filename + ".csv"), mode='w') as F:
        csv_writer = csv.DictWriter(F, fieldnames=['directory', 'fingerprint', 'domain', 'time', 'timestamp', 'status', 'tries'])
        csv_writer.writeheader()
        csv_writer = csv.writer(F)
        for row in data:
            csv_writer.writerow([
                row['directory'],
                row['fingerprint'],
                row['domain'],
                row['time'],
                row['timestamp'],
                row['status'],
                row['tries']
                ])

#
#   GENERATE DOMAIN
#

def get_random_subdomain():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(int(get_subdomain_length()))) + "." + str(get_subdomain_base())

def get_set_of_random_domains():
    return [get_random_subdomain() for x in [" "]*int(get_resolves())]

#
#   TOR RESOLVE
#

def resolve_domain(exit_desc, url, tries=0):
    sock = torsocks.torsocket()
    sock.settimeout(10) # 10 second timeout before socket closes the TCP connection

    try:
        t = time.time()
        ipv4 = sock.resolve(url) # Try to resolve the domain
    except Exception as err:
        log.debug("Error: " + str(err) + " " + str(url) + " on exit " + str(exit_desc.fingerprint))
        if (tries < int(get_tries())):
            #time.sleep(0.01 * tries)
            return resolve_domain(exit_desc, url, tries=tries + 1)
        else:
            log.warn(str(tries) + " tries, abandoning " + str(url) + " on exit " + str(exit_desc.fingerprint))
            return url, -1, tries
    else:
        t = time.time() - t
        log.debug(str(url) + " resolved to " + str(ipv4))
        return url, t, tries

def resolve_list(exit_desc, domains, status):
    data = []
    for url, t, tries in [resolve_domain(exit_desc, url) for url in domains]:
        a = {}
        a['directory'] = str(result_directory)
        a['fingerprint'] = str(exit_desc.fingerprint)
        a['domain'] = str(url)
        a['time'] = str(t)
        a['timestamp'] = str(time.time())
        a['status'] = str(status)
        a['tries'] = str(tries)
        data.append(a)
    return data

def test_domains_and_save(exit_desc):
    # Print how many domains will be resolved.
    log.debug("Resolving " + str(int(get_resolves()) * 3) + " (2*" + str(get_resolves()) + "+" + str(get_resolves()) + ") domains on exit relay " + str(exit_desc.fingerprint) + ".")

    # Notify the exit relay that research is performed.
    data = resolve_list(exit_desc, [get_white_flag()], "white flag")

    # Resolve a set of random domains once
    data.extend(resolve_list(exit_desc, get_set_of_random_domains(), "not cached"))

    # This set will be resolved twice and measured once
    cached_domains_twice = get_set_of_random_domains()
    # First resolve will cache the domains in the exit relay
    data.extend(resolve_list(exit_desc, cached_domains_twice, "now caching"))
    # Second resolve will only be used to measure the cache speed
    data.extend(resolve_list(exit_desc, cached_domains_twice, "pre cached"))

    # Store data in a CSV file named after the current date and time
    save_results_as_csv(str(exit_desc.fingerprint), data)

    log.debug("Done on exit relay " + str(exit_desc.fingerprint) + " collected " + str(len(data)) + " lines of data.")

#
#   MODULE BOOTSTRAP
#

def probe(exit_desc, run_python_over_tor, run_cmd_over_tor, **kwargs):
    setup_result_directory()
    run_python_over_tor(test_domains_and_save, exit_desc)

if __name__ == "__main__":
    # When invoked over the command line
    log.critical("Module can only be run over Tor, not stand-alone.")
    exit(1)