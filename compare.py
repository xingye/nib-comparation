#!/usr/bin/env python
import xml.etree.ElementTree
import sys
import os
import re
from shutil import copyfile

def compare(nib_set, class_set, type):
    if nib_set == class_set:
        return

    type_string = 'IBOutlet' if type == 'outlet' else 'IBAction'
    diff1 = nib_set - class_set
    diff2 = class_set - nib_set
    
    if len(diff1) > 0:
        print 'Below ' + type_string + ' missing in class file:'
        print '\n'.join(diff1)
    
    if len(diff2) > 0:
        print '----------------------------------------------'
        print 'Below ' + type_string + ' missing in nib file:'
        print '\n'.join(diff2)

if len(sys.argv) < 3:
    print "Arguments are not enough"
    print "./compare.py [path to nib file] [path to class file]"
    sys.exit(-1)

nib_file_path = str(sys.argv[1])
class_file_path = str(sys.argv[2])
class_name, _ = os.path.splitext(os.path.basename(class_file_path))
nib_name, _ = os.path.splitext(os.path.basename(nib_file_path))

xml_file_path = os.path.join(".", nib_name+".xml")
copyfile(nib_file_path, xml_file_path)

tree = xml.etree.ElementTree.parse(xml_file_path)
root = tree.getroot()
xpath = ".//*[@customClass='{0}']/..".format(class_name)

node = root.find(xpath) 

nib_outlets = set()
nib_actions = set()
class_outlets = set()
class_actions = set()

for coll in node.iter('connections'):
    for child in coll.findall('*'):
        if child.tag == 'action':
            nib_actions.add(child.get('selector'))
        elif child.tag == 'outlet':
            nib_outlets.add(child.get('property'))
  
outletReg = r'^\s?@IBOutlet\s+(weak|strong)\s+var\s+(\w+)\s?:\s?(\w+)!'
actionReg = r'^\s?@IBAction\s+func\s+(\w+)\s?\(\s?_\s+\w+\s?:\s?\w+\)'

with open(class_file_path) as f:
    for line in f:
        trip_line = line.strip()

        outletMatch = re.match(outletReg, trip_line)
        actionMatch = re.match(actionReg, trip_line)
        if outletMatch:
            class_outlets.add(outletMatch.group(2))

        if actionMatch:
            class_actions.add(actionMatch.group(1) + ':')

if class_actions == nib_actions and class_outlets == nib_outlets:
    print 'Exactlly same!'
else:
    compare(nib_actions, class_actions, 'action')
    compare(nib_outlets, class_outlets, 'outlet')

                

