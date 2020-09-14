---
title: "Download & Install"
description: ""
draft: false
bg_image: ""
---

# Quick Install

To get started quickly, ensure [Python 3.6+](https://www.python.org/downloads/) is installed on your system.

--------------------- 

## Step 1: Set up a Python virtual environment (optional)

Setting up a virtual environment will keep your installation seperate from any other Python packages that you have installed and allows you to manage different versions of Python easily. This step is optional but recommended.

### Option 1: virtualenv

Navigate to a directory where you want the virtual environment to be located.

#### Windows

```
python3 -m pip install virtualenv
python3 -m venv icu
./icu/Scripts/activate
```

#### Linux / MacOS

```
python3 -m pip install virtualenv
python3 -m venv icu
source icu/bin/activate
```

In both cases the virtual environment can be deactivated with `deactivate`.

For more information and support for using virtualenv see [here](https://docs.python.org/3/library/venv.html).

### Option 2: Anaconda

Install [Anaconda](https://docs.anaconda.com/anaconda/install/).
```
conda create -n icu python=3.6
conda activate icu
```

The virtual environment can be deactivated with `deactivate`.

------------------------ 

## Step 2: Install

### Install with pip (recommended)

Use the command below to install ICU. 

```
pip install icu
```

### Install from source

ICU can be installed from [source](https://github.com/dicelab-rhul/ICU) (requires git).

```
git clone https://github.com/dicelab-rhul/ICU.git
pip install ICU
```

-------------------------- 

## Step 3: Run

You can verify your installation by running ICU with the following command:
```
python3 -m ICU
```

This will run the system with the default configuration. If everything is working, head over to [documentation]({{< ref "documentation" >}}) to start configuring the system. 