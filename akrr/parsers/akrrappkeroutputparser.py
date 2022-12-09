# Part of XDMoD=>AKRR
# parser AK output processing
#
# author: Nikolay Simakov
#

import re
import os
import datetime
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom
import traceback
import akrr.util.log as log
import json
from akrr.util import base_gzip_encode, get_float_or_int


# add total_seconds function to datetime.timedelta if python is old
def total_seconds(d):
    return d.days * 3600 * 24 + d.seconds + d.microseconds / 1000000.0


class AppKerOutputParser:
    METRIC_NAME = 0
    METRIC_VAL = 1
    METRIC_UNIT = 2
    METRIC_BETTER = 3
    METRIC_GROUP = 4
    METRIC_TYPE = 5
    def __init__(self, name='', version=1, description='', url='', measurement_name=''):
        self.name = name
        self.version = version
        self.description = description
        self.url = url
        if measurement_name != '':
            self.measurement_name = measurement_name
        else:
            self.measurement_name = name
        self.parameters = []
        self.statistics = []
        self.mustHaveParameters = []
        self.mustHaveStatistics = []
        # complete
        self.successfulRun = None
        self.completeOnPartialMustHaveStatistics = False

        self.nodesList = None
        self.startTime = None
        self.endTime = None
        self.wallClockTime = None
        self.appKerWallClockTime = None
        self.geninfo = None

        self.filesExistance = {}
        self.dirAccess = {}

    def set_parameter(self, name, val, units=None, set_none_value=False, better=None, group="summary", metric_type=None):
        if val is None and set_none_value is False:
            return

        #if not isinstance(val, str):
        #    val = str(val)
        self.parameters.append([name, val, units, better, group, metric_type])

    def set_statistic(self, name, val, units=None, set_none_value=False, better=None, group="summary", metric_type=None):
        """

        Parameters
        ----------
        name
        val
        units
        set_none_value
        better - better direction +1 better larger, -1 better smaller, 0 does not have sense
                 default behaviour: statistics: if units are Seconds then better smaller
                 otherwise better larger, parameters: doesn't have sense
        group - statistic/parameter group: 'summary' is main group, set 'details' is detailed metrics
        metric_type - data type by default parameters are str and statistics are float
                 with json replacement val should be in proper format by this time

        Returns
        -------

        """
        if val is None and set_none_value is False:
            return
        #if not isinstance(val, str):
        #    val = str(val)
        self.statistics.append([name, val, units, better, group, metric_type])

    def match_set_parameter(self, name, pattern, line, units=None, set_none_value=False, better=None, group="summary"):
        """
        Match pattern and set parameter
        """
        m = re.match(pattern, line)
        if m:
            self.set_parameter(name, m.group(1).strip(), units=units, set_none_value=set_none_value, better=better, group=group)
            return True
        return False

    def match_set_statistic(self, name, pattern, line, units=None, set_none_value=False, better=None, group="summary"):
        """
        Match pattern and set statistic
        """
        m = re.match(pattern, line)
        if m:
            self.set_statistic(name, m.group(1).strip(), units=units, set_none_value=set_none_value, better=better, group=group)
            return True
        return False

    def search_set_parameter(self, name, pattern, line, units=None, set_none_value=False, better=None,
                            group="summary"):
        """
        Match pattern and set parameter
        """
        m = re.search(pattern, line)
        if m:
            self.set_parameter(name, m.group(1).strip(), units=units, set_none_value=set_none_value, better=better, group=group)
            return True
        return False

    def search_set_statistic(self, name, pattern, line, units=None, set_none_value=False, better=None,
                            group="summary"):
        """
        Match pattern and set statistic
        """
        m = re.search(pattern, line)
        if m:
            self.set_statistic(name, m.group(1).strip(), units=units, set_none_value=set_none_value, better=better, group=group)
            return True
        return False

    def get_parameter(self, name):
        for p in self.parameters:
            if p[0] == name:
                return p[1]
        return None

    def get_statistic(self, name):
        for p in self.statistics:
            if p[0] == name:
                return p[1]
        return None

    def __str__(self):
        s = ""
        s += "name: %s\n" % self.name
        s += "version: %s\n" % self.version
        s += "description: %s\n" % self.description
        s += "measurement_name: %s\n" % self.measurement_name

        s += "parameters:\n"
        for p in self.parameters:
            s += "\t%s: %s %s\n" % (p[0], str(p[1]), str(p[2]))
        s += "statistics:\n"
        for p in self.statistics:
            s += "\t%s: %s %s\n" % (p[0], str(p[1]), str(p[2]))

        return s

    def get_unique_parameters(self):
        r = []
        names = []
        for i in range(len(self.parameters) - 1, -1, -1):
            if names.count(self.parameters[i][0]) == 0:
                r.append(self.parameters[i])
                names.append(self.parameters[i][0])
        r.sort(key=lambda x: x[0])
        return r

    def get_unique_statistic(self):
        r = []
        names = []
        for i in range(len(self.statistics) - 1, -1, -1):
            if names.count(self.statistics[i][0]) == 0:
                r.append(self.statistics[i])
                names.append(self.statistics[i][0])
        r.sort(key=lambda x: x[0])
        return r

    def add_must_have_parameter(self, name: str) -> None:
        """
        Add must have parameter, this parameter must be present after processing of AK output
        """
        self.mustHaveParameters.append(name)

    def add_must_have_statistic(self, name: str) -> None:
        """
        Add must have statistic, this parameter must be present after processing of AK output
        """
        self.mustHaveStatistics.append(name)

    def add_common_must_have_params_and_stats(self) -> None:
        """
        Add must have parameter and statistic used across all
        """
        self.add_must_have_parameter('App:ExeBinSignature')
        self.add_must_have_parameter('RunEnv:Nodes')

    def parse_common_params_and_stats(self, appstdout=None, stdout=None, stderr=None, geninfo=None,
                                      resource_appker_vars=None):
        # retrieve node lists and set respective parameter
        try:
            if geninfo is not None:
                if os.path.isfile(geninfo):
                    with open(geninfo, "r") as fin:
                        d = fin.read()

                    gi = eval("{" + d + "}")

                    import warnings
                    warnings_as_exceptions = False
                    # mapped renamed parameters
                    renamed_parameters = [
                        ('NodeList', 'node_list'),
                        ('StartTime', 'start_time'),
                        ('EndTime', 'end_time'),
                        ('appKerstartTime', 'appkernel_start_time'),
                        ('appKerendTime', 'appkernel_end_time'),
                        ('appKerStartTime', 'appkernel_start_time'),
                        ('appKerEndTime', 'appkernel_end_time'),
                        ('fileSystem', 'file_system'),
                        ('cpuSpeed', 'cpu_speed'),
                        ('startTime', 'start_time'),
                        ('endTime', 'end_time'),
                        ('nodeList', 'node_list')
                    ]

                    for old_key, new_key in renamed_parameters:
                        if old_key in gi:
                            gi[new_key] = gi[old_key]

                            if not warnings_as_exceptions:
                                warnings.warn("Resource parameter {} was renamed to {}".format(old_key, new_key),
                                              DeprecationWarning)
                            else:
                                raise DeprecationWarning(
                                    "Resource parameter {} was renamed to {}".format(old_key, new_key))
                    
                    if 'node_list' in gi:
                        self.nodesList = base_gzip_encode(gi['node_list'])
                    if 'start_time' in gi:
                        self.set_parameter("RunEnv:Script Start Time",
                                           self.get_datetime_utc(gi['start_time'], string=True))
                        self.startTime = self.get_datetime_local(gi['start_time'])
                    if 'end_time' in gi:
                        self.set_parameter("RunEnv:Script End Time",
                                           self.get_datetime_utc(gi['end_time'], string=True))
                        self.endTime = self.get_datetime_local(gi['end_time'])
                    if 'start_time' in gi and 'end_time' in gi:
                        self.wallClockTime = self.endTime - self.startTime
                    if 'appkernel_start_time' in gi and 'appkernel_end_time' in gi:
                        self.set_parameter("RunEnv:Script Start Time",
                                           self.get_datetime_utc(gi['appkernel_start_time'], string=True))
                        self.set_parameter("RunEnv:Appkernel End Time",
                                           self.get_datetime_utc(gi['appkernel_end_time'], string=True))
                        self.appKerWallClockTime = self.get_datetime_local(gi['appkernel_end_time']) - \
                                                   self.get_datetime_local(gi['appkernel_start_time'])
                    self.geninfo = gi
        except:
            log.exception("ERROR: Can not process gen.info file\n"+traceback.format_exc())

        self.set_parameter("RunEnv:Nodes", self.nodesList)

        if appstdout is not None:
            # read output
            lines = []
            if os.path.isfile(appstdout):
                fin = open(appstdout, "rt")
                lines = fin.readlines()
                fin.close()

            # process the output
            exe_bin_signature = ''

            j = 0
            while j < len(lines):
                m = re.search(r'===ExeBinSignature===(.+)', lines[j])
                if m:
                    exe_bin_signature += m.group(1).strip() + '\n'
                j += 1
            if exe_bin_signature != '':
                exe_bin_signature = base_gzip_encode(exe_bin_signature)
            else:
                exe_bin_signature = None
            self.set_parameter("App:ExeBinSignature", exe_bin_signature)

        if stdout is not None and os.path.isfile(stdout):
            # read output
            lines = ""
            if os.path.isfile(stdout):
                with open(stdout, "rt") as fin:
                    lines = fin.read()
            if stderr is not None and os.path.isfile(stderr):
                with open(stdout, "rt") as fin:
                    lines += fin.read()

            # process the output
            files_desc = ["App kernel executable",
                          "App kernel input",
                          "Task working directory",
                          "Network scratch directory",
                          "local scratch directory"]
            dirs_desc = ["Task working directory",
                         "Network scratch directory",
                         "local scratch directory"]

            for dir_desc in dirs_desc:
                m = re.search(r'AKRR:ERROR: ' + dir_desc + ' is not writable', lines)
                if m:
                    self.dirAccess[dir_desc] = False
                else:
                    self.dirAccess[dir_desc] = True

            for file_desc in files_desc:
                m = re.search(r'AKRR:ERROR: ' + file_desc + ' does not exists', lines)
                if m:
                    self.filesExistance[file_desc] = False
                    if file_desc in dirs_desc:
                        self.dirAccess[file_desc] = False
                else:
                    self.filesExistance[file_desc] = True

            for k, v in list(self.filesExistance.items()):
                self.set_statistic(k + " exists", int(v))
            for k, v in list(self.dirAccess.items()):
                self.set_statistic(k + " accessible", int(v))

        if resource_appker_vars is not None:
            if 'resource' in resource_appker_vars and 'name' in resource_appker_vars["resource"]:
                self.set_parameter("resource", resource_appker_vars["resource"]['name'])
            if 'app' in resource_appker_vars and 'name' in resource_appker_vars["app"]:
                self.set_parameter("app", resource_appker_vars["app"]['name'])

    def parsing_complete(self, verbose=False):
        """i.e. app output was having all mandatory parameters and statistics"""
        complete = True

        p = []
        for v in self.parameters:
            p.append(v[0])
        for v in self.mustHaveParameters:
            if p.count(v) == 0:
                if verbose:
                    print(("Must have parameter, %s, is not present" % (v,)))
                complete = False
        p = []
        for v in self.statistics:
            p.append(v[0])
        for v in self.mustHaveStatistics:
            if p.count(v) == 0:
                if verbose:
                    print(("Must have statistic, %s, is not present" % (v,)))
                complete = False
        if self.completeOnPartialMustHaveStatistics and complete is False:
            if 'Number of Tests Passed' in self.mustHaveStatistics and \
                    'Number of Tests Started' in self.mustHaveStatistics:
                if isinstance(self.get_statistic('Number of Tests Passed'), str) and \
                        isinstance(self.get_statistic('Number of Tests Started'), str) and \
                        self.get_statistic('Number of Tests Passed').isdigit() and\
                        self.get_statistic('Number of Tests Started').isdigit():
                    if int(self.get_statistic('Number of Tests Passed')) > 0:
                        complete = True
                else:
                    complete = False

        return complete
    def is_successfully_completed(self):
        """app is successfully completed and parsing is successfully completed"""
        if self.successfulRun is not None:
            if self.parsing_complete(True) and self.successfulRun:
                return True
            else:
                return False
        else:
            if self.parsing_complete(True):
                return True
            else:
                return False

    def get_xml(self):
        root = ElementTree.Element('rep:report')
        root.attrib['xmlns:rep'] = 'report'
        body = ElementTree.SubElement(root, 'body')
        performance = ElementTree.SubElement(body, 'performance')
        performance_id = ElementTree.SubElement(performance, 'ID')
        performance_id.text = self.measurement_name
        benchmark = ElementTree.SubElement(performance, 'benchmark')
        benchmark_id = ElementTree.SubElement(benchmark, 'ID')
        benchmark_id.text = self.measurement_name
        parameters = ElementTree.SubElement(benchmark, 'parameters')
        statistics = ElementTree.SubElement(benchmark, 'statistics')

        details = ElementTree.SubElement(performance, 'details')
        parameters_details = ElementTree.SubElement(details, 'parameters')
        statistics_details = ElementTree.SubElement(details, 'statistics')

        pars = self.get_unique_parameters()
        for par in pars:
            if par[AppKerOutputParser.METRIC_GROUP] == "details":
                e = ElementTree.SubElement(parameters_details, 'parameter')
            else:
                e = ElementTree.SubElement(parameters, 'parameter')
            ElementTree.SubElement(e, 'ID').text = par[0]
            ElementTree.SubElement(e, 'value').text = str(par[1])
            if par[2]:
                ElementTree.SubElement(e, 'units').text = par[2]

        pars = self.get_unique_statistic()
        for par in pars:
            if par[AppKerOutputParser.METRIC_GROUP] == "details":
                e = ElementTree.SubElement(statistics_details, 'statistic')
            else:
                e = ElementTree.SubElement(statistics, 'statistic')
            ElementTree.SubElement(e, 'ID').text = par[0]
            ElementTree.SubElement(e, 'value').text = str(par[1])
            if par[2]:
                ElementTree.SubElement(e, 'units').text = par[2]

        if len(parameters_details) == 0:
            details.remove(parameters_details)
        if len(statistics_details) == 0:
            details.remove(statistics_details)
        if len(details) == 0:
            performance.remove(details)

        exit_status = ElementTree.SubElement(root, 'exitStatus')
        completed = ElementTree.SubElement(exit_status, 'completed')
        completed.text = str(self.is_successfully_completed()).lower()
        return xml.dom.minidom.parseString(ElementTree.tostring(root)).toprettyxml(indent="  ")

    def get_json(self):
        results = {
            'resource': None,
            'app': self.name,
            'resource_request': {'cores': None,'nodes': None,'apus': None},
            'parameters':[],
            'statistics':[],
            'details':{
                'parameters':[],
                'statistics':[],
            },
            'completed': self.is_successfully_completed()
        }

        pars = self.get_unique_parameters()
        for par in pars:
            r = {'name': par[0]}
            if par[AppKerOutputParser.METRIC_TYPE] is not None:
                r['value'] = par[AppKerOutputParser.METRIC_TYPE](par[1])
            else:
                r['value'] = par[1]
            if par[2] is not None:
                r['units'] = par[2]
            if par[AppKerOutputParser.METRIC_BETTER] is not None:
                r['better'] = par[AppKerOutputParser.METRIC_BETTER]

            if par[AppKerOutputParser.METRIC_GROUP] == "details":
                results['details']['parameters'].append(r)
            else:
                results['parameters'].append(r)

        pars = self.get_unique_statistic()
        for par in pars:
            r = {'name': par[0], 'value': (par[1])}
            if par[AppKerOutputParser.METRIC_TYPE] is not None:
                r['value'] = par[AppKerOutputParser.METRIC_TYPE](par[1])
            elif isinstance(par[1], str):
                r['value'] = get_float_or_int(par[1])
            else:
                r['value'] = par[1]
            if par[2] is not None:
                r['units'] = par[2]
            if par[AppKerOutputParser.METRIC_BETTER] is not None:
                r['better'] = par[AppKerOutputParser.METRIC_BETTER]

            if par[AppKerOutputParser.METRIC_GROUP] == "details":
                results['details']['statistics'].append(r)
            else:
                results['statistics'].append(r)
        return json.dumps(results, indent="  ")

    def print_params_stats_as_must_have(self):
        """print set parameters and statistics as part of code to set them as must have"""
        pars = self.get_unique_parameters()
        for par in pars:
            print(("parser.add_must_have_parameter('%s')" % (par[0],)))
        print()
        pars = self.get_unique_statistic()
        for par in pars:
            print(("parser.add_must_have_statistic('%s')" % (par[0],)))

    def print_template_for_pytest(self):
        """
        Print template for regrassion value checking in pytest
        """
        from akrr.util import is_int, is_float
        pars = self.get_unique_parameters()
        for par in pars:
            if is_int(par[1]):
                print('assert parstat_val_i(params, "%s") == %s' % (par[0], str(par[1])))
            elif is_float(par[1]):
                print('assert floats_are_close(parstat_val_f(params, "%s"), %s)' % (par[0], str(par[1])))
            else:
                print('assert parstat_val(params, "%s") == "%s"' % (par[0], str(par[1])))
        print()
        pars = self.get_unique_statistic()
        for par in pars:
            if is_int(par[1]):
                print('assert parstat_val_i(stats, "%s") == %s' % (par[0], str(par[1])))
            elif is_float(par[1]):
                print('assert floats_are_close(parstat_val_f(stats, "%s"), %s)' % (par[0], str(par[1])))
            else:
                print('assert parstat_val(stats, "%s") == "%s"' % (par[0], str(par[1])))
        print()

    @staticmethod
    def get_datetime_utc(datestr, usetz=True, string=False):
        """Return local datatime, will convert the other zones to local. If original datestr does not have
        zone information assuming it is already local"""
        import dateutil.parser
        from dateutil.tz import tzutc
        m_datetime = dateutil.parser.parse(datestr).astimezone(tzutc())
        if usetz is False:
            m_datetime = m_datetime.replace(tzinfo=None)
        if string is True:
            m_datetime = m_datetime.isoformat()
        return m_datetime
    @staticmethod
    def get_datetime_local(datestr):
        """Return local datatime, will convert the other zones to local. If original datestr does not have
        zone information assuming it is already local"""
        import dateutil.parser
        from dateutil.tz import tzlocal
        return dateutil.parser.parse(datestr).astimezone(tzlocal()).replace(tzinfo=None)
