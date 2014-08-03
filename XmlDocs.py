import sublime, sublime_plugin, re

def read_line(view, point):
    if (point >= view.size()):
        return

    next_line = view.line(point)
    return view.substr(next_line)

class XmldocsCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    point = self.view.sel()[0].end()
    self.settings = self.view.settings()

    # keywords = ['public', 'private', 'static', 'virtual', 'override', 'abstract']

    # read the line below
    # self.refLine = read_line(self.view, self.view.line(point).end() + 1)
    self.refLine = ""

    # read ahead
    maxRead = 10
    pos = self.view.line(point).end() + 1
    for i in range(1, maxRead):
        line = read_line(self.view, pos)
        if line is None:
            break

        self.refLine += line
        pos += len(line) + 1

    # print(self.refLine)
    
    # Separate into parts
    sections = re.search(r'^(?P<keywords>[^\(\;{=]+)(?:\((?P<params>[^\)]*)\))?', self.refLine)

    # Keywords for the line (like public, static, etc...)
    keywords = str.strip(sections.group('keywords')).split(' ')

    # Break line up as if it is a function
    functionParts = re.search(r'(?P<function>[^<]*)(\<(?P<template>[^\>]*)\>)?', keywords[-1])
    functionName = functionParts.group('function')
    functionTemplate = functionParts.group('template')

    # get the return type
    returnType = keywords[-2]

    # Help for tab-stops
    ind = 1

    # Kick off the output string
    opStr = ' <summary>${{{0}:{1}}}</summary>'.format(ind, str.strip(functionName))

    if functionTemplate:
        ind+=1
        opStr += '\n/// <typeparam name="{1}">${{{0}:{1}}}</typeparam>'.format(ind, functionTemplate)

    if sections.groupdict()['params'] is not None:
        params = sections.group('params').split(',')
        params = list(map(str.strip, params))
        for param in params:
            if param:
                ind+=1
                p = str.strip(param.split('=')[0]).split(' ')[-1]
                opStr += '\n' + '/// <param name="{1}">${{{0}:{1}}}</param>'.format(ind, str.strip(p))

        if returnType and returnType != 'void':
            ind+=1
            opStr += '\n' + '/// <returns>${{{0}:{1}}}</returns>'.format(ind, returnType)
    
    # check if this is a property (get/setter)
    prop = re.match(r'([^;=\({}]*){\s*(get|set)\s*{', self.refLine)
    if prop is not None:
        ind+=1
        opStr += '\n' + '/// <value>${{{0}:value}}</value>'.format(ind)

        
    self.view.run_command(
        'insert_snippet', {
            'contents': opStr
        }
    )

