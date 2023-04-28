import re
import pandas as pd
from collections import defaultdict, Counter, OrderedDict
import os
from datetime import datetime
import multiprocessing as mp
import itertools
import hashlib
import numpy as np


log_format = r'\[(?P<Time>[^\]]+)\] \[(?P<Level>[^\]]+)\] (?P<Content>.*)'

class LogLoader(object):

    def __init__(self, logformat):
        self.logformat = logformat.strip()

    def load_to_dataframe(self, log_filepath):
        """ Function to transform log file to dataframe 
        """
        print('Loading log messages to dataframe...')
        lines = []
        with open(log_filepath, 'r') as fid:
            lines = fid.readlines()
        
        log_messages = []
        for line_count, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            line = re.sub(r'[^\x00-\x7F]+', '<N/ASCII>', line)
            match = re.match(self.logformat, line)
            if match is None:
                continue
            message = [match.group(key) for key in ['Time', 'Level', 'Content']]
            message.insert(0, line_count + 1)
            log_messages.append(message)

        if not log_messages:
            raise RuntimeError('Logformat error or log file is empty!')
        log_dataframe = pd.DataFrame(log_messages, columns=['LineId', 'Time', 'Level', 'Content'])
        success_rate = len(log_messages) / float(len(lines))
        print('Loading {} messages done, loading rate: {:.1%}'.format(len(log_messages), success_rate))
        return log_dataframe

template_match_dict = defaultdict(dict)

def read_template_from_csv(template_filepath):
    template_dataframe = pd.read_csv(template_filepath)
    #print(template_dataframe)
    for idx, row in template_dataframe.iterrows():
        event_Id = row['EventId']
        event_template = row['EventTemplate']
        add_event_template(event_template, event_Id)
    return template_dataframe

def add_event_template(event_template, event_Id=None):
    if not event_Id:
        event_Id = generate_hash_eventId(event_template)
    template_match_dict[generate_template_regex(event_template)] = (event_Id, event_template)

def generate_hash_eventId(template_str):
    return hashlib.md5(template_str.encode('utf-8')).hexdigest()[0:8]


def generate_template_regex(template):
    template = re.sub(r'(<\*>\s?){2,}', '<*>', template)
    regex = re.sub(r'([^A-Za-z0-9])', r'\\\1', template)
    regex = regex.replace('\<\*\>', '(.*?)')
    regex = regex.replace('\<NUM\>', '(([\-|\+]?\d+)|(0[Xx][a-fA-F\d]+))')
    regex = regex.replace('\<IP\>', '((\d+\.){3}\d+)')
    regex = '^' + regex + '$'
    return regex

def match_logs_with_templates(log_filepath, template_filepath, log_format):
    print('Processing log file: {}'.format(log_filepath))
    start_time = datetime.now()
    loader = LogLoader(log_format)
    template_match_dict = read_template_from_csv(template_filepath)
    log_dataframe = loader.load_to_dataframe(log_filepath)
    print('Matching event templates...')
    match_list, paras = match_event(log_dataframe['Content'].tolist(), template_match_dict)
    #print(match_list[0:9])
    log_dataframe = pd.concat([log_dataframe, pd.DataFrame(match_list, columns=['EventId'])], axis=1) #columns to be changed id and tempelate
    #print(log_dataframe.head())
    log_dataframe['ParameterList'] = paras
    match_rate = sum(log_dataframe['EventId'] != 'NONE') / float(len(log_dataframe))
    print('Matching done, matching rate: {:.1%} [Time taken: {!s}]'.format(match_rate, datetime.now() - start_time))
    return log_dataframe

def match_event(event_list, template_match_dict):
    match_list = []
    paras = []
    results = match_fn(event_list, template_match_dict)
    for event, parameter_list in results:
        paras.append(parameter_list)
        match_list.append(event)
    return match_list, paras

def match_fn(event_list, template_match_dict):
    print("Matching {} lines.".format(len(event_list)))
    #print(event_list[0:7])
    print('\n')
    #print(template_match_dict)
    match_list = [regex_match(event_content, template_match_dict)
                  for event_content in event_list]
    #print(match_list)
    return match_list
    
def regex_match(msg, template_match_dict):
    matched_event = None
    template_freq_dict = Counter()
    parameter_list = []

    for index, row in template_match_dict.iterrows():
        template = row['EventTemplate']
        regex_pattern = ''
        last_pos = 0
        for match in re.finditer(r'<\*>', template):
            regex_pattern += re.escape(template[last_pos:match.start()])
            regex_pattern += r'(.*)'
            last_pos = match.end()
        regex_pattern += re.escape(template[last_pos:])
        
        if re.match(regex_pattern, msg.strip()):
            matched_event = row['EventId']
            matches = re.findall(regex_pattern, msg.strip())
            parameter_list = list(matches[0]) if matches else []
            break

    if not matched_event:
        matched_event = 'NONE'
    if not parameter_list:
        parameter_list = ['NONE'] * (regex_pattern.count('(.*)'))

    return matched_event, parameter_list




log_loader = LogLoader(log_format)
log_dataframe = log_loader.load_to_dataframe('apache_formatted_logs.log')
print(log_dataframe.head())
print("\n\n")
structured_dataframe = pd.read_csv('Apache_2k.log_structured.csv')
print(structured_dataframe)
print("\n\n")
#x = read_template_from_csv('Apache_2k.log_templates.csv')
#print (x)
#y = match('Apache_2k.log', 'Apache_2k.log_templates.csv')
#print(y)
matched_logs =match_logs_with_templates('apache_formatted_logs.log', 'Apache_2k.log_templates.csv', log_format)
print(matched_logs)
print("\n\n")
 # merge the two dataframes on line_id and Event_Id columns
merged_logs = matched_logs.merge(structured_dataframe, on=['LineId', 'EventId'], how='inner')
print(merged_logs)
# count the number of rows in the merged dataframe
count = merged_logs.shape[0]

# print the count
print(f'{(count/2000) *100}% logs are parsed correctly.')

