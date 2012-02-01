#!/usr/bin/python

templates = [
    # we build the titlepage in three steps: the header,
    # the table rows for the partners, and then the titlepage complete
    # out of these two parts. This third part is then written to file 
    { "label" : "titleheader",
      "template" : r"""
    \begin{center}
    {\LARGE  ${instrument}  } \\[.2cm]
    {\large  ${call}   } \\[.4cm]
    {\LARGE \textbf{  ${projectname}  }} \\[.3cm]
    {\LARGE Acronym: \textbf{  ${projectshort}  }} \\[.3cm]
    \end{center}

    {\large Date of Preparation: \today }\\[1em]
    \begin{large}
    \begin{description}
    \item[Work program topics  addressed:]  ${topics}
    \item[Coordinator:] ${coordinatorname}
    \item[e-mail:] {\url{${coordinatoremail}}} 
    \item[tel/fax:]   ${coordinatorphone}

    \end{description}
    \end{large}
    % \begin{center}
    \noindent 
      """,
      "dict" : "titlepageDict"
      },
    # rows for partner table on titlepage: 
    { "label" : "partnerTableRow",
      "template" : "${Number} & ${Name} &  ${Shortname} & ${Nation}",
      "list" : "partnerList",
      "joiner" : "\\\\ \n"
      },
    # and the actual titlepage: 
    { "label" : "titlepage",
      "template" : r"""
      ${titleheader}
      {
      \begin{tabular}{cp{8cm}ll}
      \toprule
      Participant no. & Participant organisation & Short name & Country \\
      \midrule
      ${partnerTableRow}
      \bottomrule
      \end{tabular}
      }
      """,
      "dict" : "expanded",
      "file": True,
      },
    ############################
    # the wp summary list
    { "label": "wpsummaryRows",
      "template" : """WP ${Number} & ${Name} & ${Type} & ${Leadernumber} & ${Leadership} & ${wpeffort} & ${Start} & ${End}""",
      "list" : "allWPDicts",
      'joiner': "\\\\ \n",
      },
    { "label" : "wpsummarytable",
      "template" : r"""
    \begin{table}[bhtp]
    \caption{Summary table of all work packages}
    \label{tab:wpsummary}
    \begin{tabular}{cp{0.25\textwidth}cccrcc}
    \toprule
    WP No. & WP name & Type of & Lead & Lead & Person- & Start & End \\
        & & activity & part. no. & short name & months & month & month \\
    \midrule
    ${wpsummaryRows}
    \midrule
    \multicolumn{2}{l}{Total:} & & & & \totalPM & & \\
    \bottomrule
    \end{tabular}
    \end{table}""",
      "dict" : "expanded",
      "file" : True,
      "dir" : "tables",
      },
    #######################
    # initial demo trials, not important for content, just for testing 
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
    { "label" : "effortPerPartner",
      "template" : "Task: ${task} Resource: ${resources}",
      "list" : "allEfforts",
      "joiner" : "\\\\ \n",
      "groupby" : "partner",
      "file" : True,
      "dir" : "wp"},
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
