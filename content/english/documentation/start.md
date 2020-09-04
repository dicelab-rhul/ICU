---
title: "Getting Started"
description: ""
draft: false
weight: 1
bg_image: ""
toc : true
---

 <a href="{{<ref download.md >}}" class="btn btn-main"> Download & Install </a>

You can verify your installation by running ICU with the following command:
```
python -m ICU
```

This will run the system with the default configuration.

## Options

To see all available command line options: `python -m icu -help`

## Specifying a Configuration file

ICU uses a configuration file to allow users to modified many aspects of the system. The configuration file can be specified with the `-c` option.
```
python -m icu -c config.json
```
For details on configuring ICU see [Configuration]({{< ref "configuration" >}}) below.









