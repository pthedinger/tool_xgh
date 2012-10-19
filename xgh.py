#!/usr/bin/python
import xml.dom.minidom
import sys
import platform
import subprocess
import re
import os

ostype = platform.system()

if not re.match('.*Darwin.*',ostype) and re.match('.*[W|w]in.*',ostype):
    concat_args = True
    use_shell = True
else:
    concat_args = False
    use_shell = False

def Popen(*args, **kwargs):    
    kwargs['shell'] = use_shell
    if concat_args:
        args = (' '.join(args[0]),) + args[1:]
    try:
        return subprocess.Popen(*args,**kwargs)
    except:
        sys.stderr.write("ERROR: Cannot run command `%s'\n"%' '.join(args[0]))
        sys.stderr.write("ABORTING\n")
        sys.exit(1)

def call(*args, **kwargs):
    kwargs['shell'] = use_shell
    if concat_args:
        args = (' '.join(args[0]),) + args[1:]
    try:
        return subprocess.call(*args,**kwargs)
    except:
        sys.stderr.write("ERROR: Cannot run command `%s'\n"%' '.join(args[0]))
        sys.stderr.write("ABORTING\n")
        sys.exit(1)


def parse_version(v):
    m = re.match(r'(\d*)\.(\d*)\.(\d*)(alpha|beta|rc|)(\d*)', v)
    if not m:
        print "Error parsing version: %s" % v
    else:
        if (m.groups(0)[3] == 'alpha'):
            stage = 0
        elif (m.groups(0)[3] == 'beta'):
            stage = 1
        else:
            stage = 3

        if m.groups(0)[4] in ['',None]:
            relnum = 10000
        else:
            relnum = int(m.groups(0)[4])

        return (int(m.groups(0)[0]),
                int(m.groups(0)[1]),
                int(m.groups(0)[2]),
                stage,
                relnum)

def compare_versions(a,b):
    return cmp(parse_version(a), parse_version(b))


def exec_and_match(command, regexp, cwd=None):
    process = Popen(command, cwd=cwd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    lines = process.stdout.readlines()
    for line in lines:
        m = re.match(regexp, line)
        if m:
            return m.groups(0)[0]
    return None


def current_githash(path=None):
    return exec_and_match(["git","rev-parse","HEAD"],r'(.*)',cwd=path)

def get_child_hash(parenthash,path=None):
    return exec_and_match(["git","rev-list","--parents","--all","--date-order","--reverse"],
                          r'(.*) %s'%parenthash,
                          cwd=path)

def get_version_or_githash(path=None):
    githash = current_githash(path)
    rels = get_releases(path)
    for rel in rels:
        if rel['githash'] == githash:
            return rel['version']

    return githash[:10]


def get_on_version(path=None):
    githash = current_githash(path)
    rels = get_releases(path)
    for rel in rels:
        if rel['githash'] == githash:
            return True

    return False

def get_xpd_xml(path=None):
    if (path==None):
        path = ''
    xpdxml_path = os.path.join(path,"xpd.xml")
    try:
        if os.path.exists(xpdxml_path):
            return xml.dom.minidom.parse(xpdxml_path)
        else:
            return xml.dom.minidom.parseString("<xpd/>")
    except:
        print "ERROR opening xpd.xml"
        sys.exit(1)

def get_master_xpd_xml(path=None):
    process = Popen(["git","show","master:xpd.xml"],
                    cwd=path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            
    err_lines = process.stderr.readlines()
    if err_lines == []:
        read_file = False
        return xml.dom.minidom.parseString(process.stdout.read())
    else:
        print "ERROR: Cannot find version of xpd.xml on HEAD of master branch"
        sys.exit(1)


def get_releases(path=None):
    dom = get_master_xpd_xml(path)
    rels = []
    for node in  dom.getElementsByTagName('release'):
        version = node.getAttribute("version")
        githash = node.getAttribute("githash")
        if not githash:
            githash = get_child_hash(node.getAttribute("parenthash"),path)
        rels.append({'version':version, 'githash':githash})
    return rels

def get_dependencies(path=None):
    dom = get_xpd_xml(path)
    deps = []
    for node in dom.getElementsByTagName('dependency'):
        repo = node.getAttribute('repo')
        githash = node.getElementsByTagName('githash')[0].childNodes[0].wholeText
        try:
            version = node.getElementsByTagName('version')[0].childNodes[0].wholeText
        except:
            version = node.getElementsByTagName('githash')[0].childNodes[0].wholeText[:10]
        deps.append({'name':repo,'version':version,'githash':githash})

    return deps


def status():
    v = get_version_or_githash()
    print "Current Version: " + v
    on_version = get_on_version()
    print "Dependencies:"
    for dep in get_dependencies():
        depv = get_version_or_githash(os.path.join('..',dep['name']))
        if on_version and depv != dep['version']:
            expected = " (" + v + " expects " + dep['version'] + ")"
        else:
            expected = ""

        print "   " + dep['name'] + ": " + depv + expected

def list_versions():
    rels = get_releases()
    for v in sorted([rel['version'] for rel in rels],cmp=compare_versions):
        print v

def git(args):
    print "Main Repo:"
    call(["git"]+args)
    for dep in get_dependencies():
        print dep['name']+":"
        call(["git"]+args,cwd=os.path.join('..',dep['name']))

def getdeps():
    for dep in get_dependencies():
        print "Cloning " + dep['name']
        call(["git","clone",
              "https://github.com/xcore/%s.git"%dep['name'],
              os.path.join("..",dep['name'])])

def checkout(args):
    if args == []:
        print "Please specify version to checkout"
        sys.exit(1)

    version = args[0]

    if version == "master":
        print "Checking out master"
        call(["git","checkout","master"])
        for dep in get_dependencies():
            print dep['name'] + ": Checking out master"
            call(["git","checkout","master"],
                 cwd=os.path.join('..',dep['name']))
        return

    rels = get_releases()
    for rel in rels:
        if rel['version'] == version:
            print "Checking out " + version
            call(["git","checkout",rel['githash']])
            for dep in get_dependencies():
                print dep['name'] + ": Checking out " + dep['githash']
                call(["git","checkout",dep['githash']],
                     cwd=os.path.join('..',dep['name']))

    print "Unknown version"
    sys.exit(1)



def show_help():
    print """\
usage: xgh command [options]

Commands:

    help                display this message
    status              show the status of this repo and its dependencies
    git <cmd>           apply the git command to the repo and its dependencies
    list                list all release versions of a repo
    checkout <version>  checkout a particular version of a repo
    getdeps             clone the dependencies of this repo
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command in ["help","-help","--help"]:
        show_help()
    elif command == "status":
        status()
    elif command == "git":
        git(args)
    elif command == "list":
        list_versions()
    elif command == "checkout":
        checkout(args)
    elif command == "getdeps":
        getdeps()
    else:
        print "UNKNOWN COMMAND: %s\n" % command
        show_help()
        sys.exit(1)

