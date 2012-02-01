#!/usr/bin/python

templates = [
    { "label" : "titleheader",
      "template" : "${call} Duration: ${duration}",
      "dict" : "titlepageDict"
      },
    { "label" : "partnerTableRow",
      "template" : "Name: ${Name} &  ${Nation} & ${Type}",
      "list" : "partnerList",
      "joiner" : "\\\\ \n"
      },
    { "label" : "partnerTableRowsAsList",
      "template" : "Name: ${Name} &  ${Nation} & ${Type}",
      "list" : "partnerList",
      },
    { "label" : "partnerTableRowsWithNumber",
      "template" : "Name: ${Name} &  ${Nation} & ${Type}",
      "list" : "partnerList",
      "numerator" : "i",
      },
    { "label" : "partnerTableRowsWithShortname",
      "template" : "Name: ${Name} &  ${Nation} & ${Type}",
      "list" : "partnerList",
      "numerator" : "value['Shortname']",
      },
    { "label" : "titelpage",
      "template" : "HEre comes the header ${titleheader} and here comes the partner table: ${partnerTableRow}",
      "dict" : "expanded",
      "file" : True
      },
    { "label" : "effortPerPartner",
      "template" : "Task: ${task} Resource: ${resources}",
      "list" : "allEfforts",
      "joiner" : "\\\\ \n",
      "groupby" : "partner"},
    { "label" : "effortPerPartnerAsList",
      "template" : "Task: ${task} Resource: ${resources}",
      "list" : "allEfforts",
      "groupby" : "partner"},
    { "label" : "effortPerPartner",
      "template" : "Task: ${task} Resource: ${resources}",
      "list" : "allEfforts",
      "numerator" : "value['task']",
      "groupby" : "partner"},
    ]
