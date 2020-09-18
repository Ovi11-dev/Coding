#!/usr/bin/env python3
# This shebang is only for Linux. Without it many distros default to Python 2, 
# which cannot execute this script. Also for Linux, this file uses Unix line 
# endings. This is only for the shebang line. Python doesn't care.

# renet.py
# Updated: 2019.02.27
# Test program for rene.py
# Author David McCracken
# Released under GNU General Public License v3.0

# Full life-cycle tester for rene.py. Exercises the rene.py located in the same
# directory so a new version can be tested even if another is located on the
# path and even if this directory is not.
#
# Command line is renet.py tests options. tests is a comma-delimited list of 
# test numbers or 'ALL'. The test numbers may also include ranges, e.g. 
# 1,3,6-15,20. options is a string of single-letter options. These are Q, V, 
# and R. Q (Quiet mode) turns off most display except for result checking 
# status. V (Verbose) turns on more display than normal. R (Record) records 
# all output in the file test results. The two command line arguments are both 
# optional. If no argument is provided, a default test, including mode 
# settings, is exercised. This can only be changed by editing the main code. 
# Regression testing is normally ALL or ALL Q.
# Note: R remains unimplemented. It is more difficult than it seems because
# there are many sources of output, in both renet and rene, and having a record
# would not be especially useful.
#
# User interaction with rene is minimal, consisting mainly of answering Y or N 
# to whether to effect the reported name changes. This can be included in 
# automated testing by redirecting the input to the yes or no file. 
# Redirection has to be embedded in the test definition. 
# ANY TEST DEFINITION THAT DOESN'T CONTAIN -AS or -AR IN THE COMMAND MUST 
# REDIRECT INPUT TO YES OR NO. Otherwise, the test will inexplicably hang.
# Each test definition also determines the extent of automatic result 
# checking, of which there are two forms, compare the output display (from 
# rene) to what the test expects and checking the directory for expected 
# changes. If a test defines these they are unconditionally executed. 
# 
# ............................ FUNCTIONS ...................................
# Tests are functions named test1, test2, etc. The front end synthesizes the 
# function names from the tests argument and invokes them. Tests take no 
# arguments and nothing is assumed about them. They are free to do anything but
# the intent is to pare them down to a minimal description of the test with 
# all scaffolding provided in shared utility functions. Typically, they only 
# define the arguments to exercise rene against, the test conditions, and the 
# expected results. These are passed in a call to the engine function, which 
# performs everthing. The normal test is essentially declarative.
#
# Test names are numbered for convenience. They are in the same order as their
# names also for convenience, as this makes it easy to avoid duplicating a 
# name, but they may appear in any order. If many tests would have to be 
# renamed to insert one, it may be more convenient to just give it the next 
# available name. The name space can be sparse but every missing test in a 
# requested range is reported as undefined.
#
# The engine function manages test execution. On each invocation it performs 
# one invocation of rene. Only one argument is required. It is args, the rene 
# command arguments. engine itself assembles a complete command line, including
# output redirection. Input redirection, e.g. "yes" and "no" files, is 
# embedded in the args defined by each test. engine manages deleting and 
# creating files per the test definition and comparing results to expectations 
# but it doesn't do the detailed work. This is passed off to lower level 
# functions, which any test can invoke directly, bypassing engine, in special 
# circumstances. 
#
# Most tests provide lists of files to delete and create in order to ensure a 
# particular environment. Because they can't know what has already happened, 
# tests typically ask to delete all files with a list containing one string 
# "all". The actual job of deletion falls to delThese, which doesn't blindly 
# delete everything but only files that are not in the save list of files to 
# be protected from deletion. This enables rene.py and renet.py and their 
# support files to coexist in one directory without renet destroying 
# everything.
#
#                       Program Design Notes
# Originally, there was a command line option to turn on expected results 
# compare. Now it is automatically turned on by the test passing non-empty 
# expect argument to engine. Requiring this flag complicated regression 
# testing and giving the command line no means of stopping it means little 
# because a test that isn't ready for this kind of check can pass empty or 
# nothing at all (the default is empty). Even if it is unwelcome, all it does 
# from the user's POV is to announce the compare result. It does cause a 
# little more disk activity, as the output is redirected into a file and then 
# the contents of that file are both displayed and compared to the expected 
# results but that is a minor issue.
#
# All functions that do result checking compare results to the expected results
# from the test definition. If everything matches they return 0, else 1. The 
# rationale for this (instead of True/False or error count or error type) is 
# that callers can simply add the returns from multiple tests to determine how 
# many failed. However, this capability is not being utilized because it is 
# better to record and subsequently report all failed tests by name than to 
# simply report how many have failed. For this, it doesn't matter what the 
# compare functions return as long as it is consistent.
# -----------------------------------------------------------------------------
import os, stat, sys
Windows = os.name == 'nt'

Quiet = False
Verbose = False
Record = False

# ----------------------------------------------------------------------------
# saveThis determines (True/False) whether the given name is one of rene's own
# or renet's support support files, which should not be deleted even when we 
# say "all". Some of these are Windows-specfic and mean nothing in Linux.
# .............................................................................
def saveThis(n) :
    return n in ['no', 'yes', 'idle.lnk'] or len(n) > 3 and n[:4].lower() == 'rene'
    
# ------------------------------------------------------------------------
# delThese deletes the files in the given list. If the list is empty the 
# function silently returns. If the first string in the list is "all" then all 
# files in the current directory are deleted. In both the "all" case and when 
# a list of specific files is provided, directories and the protected save 
# files are skipped.
def delThese(flist) :
    if len(flist) == 0 :
        return
    if flist[0] == 'all' :
        flist = os.listdir()
    for f in flist :
        if not saveThis(f) and os.path.exists(f) and \
        stat.S_ISREG(os.stat(f).st_mode) :
            os.remove(f)

# ------------------------------------------------------------------
# createThese creates the files in the given list. Files that already exist 
# are not touched. The new files are opened in text mode and one line contain 
# only 'hi' and newline is written. 
def createThese(flist) :
    for filename in flist :
        if not os.path.exists(filename) :
            fo = open(filename, mode = 'wt')
            fo.write('hi\n')
            fo.close()

# ------------------------------------------------------------------------
# showDir lists the files in the current directory, skipping files that are in
# the save list and directories, as these are of no interest in testing.
def showDir() :
    for f in os.listdir() :
        if stat.S_ISREG(os.stat(f).st_mode) and not saveThis(f) :
           print(f)

# ------------------------------------------------------------------------
# checkDir verifies that the expected files in dirIn list do exist and that
# unpected files in dirOut list do not exist.
def checkDir(dirIn, dirOut) :
    err  = 0
    for filename in dirIn :
        if not os.path.exists(filename) :
            print(filename, 'expected file is missing')
            err = 1
    for filename in dirOut :
        if os.path.exists(filename) :
            print(filename, 'unexpectedly exists')
            err = 1
    if err == 0 :
        print('The files are as expected')
    return err # 0 = all ok. 1 = not ok.

# ----------------------------------------------------------------------
# checkrec displays the contents of the testrec file and optionally compares
# it line-by-line to the given list of expected lines. This accepts an empty
# cmp list to allow its blind usage but that is not generally useful. Without
# comparing against expectations, the testrec file serves no purpose and it
# makes more sense to invoke rene without redirecting its output into testrec.
def checkrec(cmp = []) :
    try :
        with open('testrec', mode = 'rt') as fin :
            if len(cmp) == 0 or not Quiet :
                for line in fin :
                    print(line, end="")
                if Quiet :
                    return 0 # Consider this ok.
                fin.seek(0)
            err = 0
            for line in zip(fin, cmp) :
                if line[0][:-1] != line[1] :
                    print('ERROR', line[0][:-1], '!=', line[1])
                    err = 1
            return err # 0 if ok. 1 if not.
    except FileNotFoundError :
        print("testrec file doesn't exist")
        return 1 # Consider this bad

# ----------------------------------------------------------------------------
# engine is the test engine. Each test calls it, passing at least the args 
# string, which are the command line arguments used to invoke rene.py. engine 
# provides the rest of the command line, including whether to redirect the 
# output. If expect is not empty (the default) the output from rene.py is 
# redirected into the testrec file. This does not prevent display. If not 
# Quiet checkrec displays the contents of testrec as well as compare them to 
# the expected output for regression testing. preDel and preCreate are lists 
# of files (name strings) to delete and create to prepare the test environment 
# for rene.
#
# cmdErr is a notice from the test defining that we are expecting a non-0
# exit code from rene. This should also be accompanied by an expected output
# so that we can precisely verify the behavior. If rene's exit code is not
# 0 when cmdErr is False, it is considered a failure in either the test
# definition or rene.py (i.e. a bug)
# .........................................................................
def engine(args, preDel = [], preCreate = [], expect = [], cmdErr = False) :
    delThese(preDel)
    createThese(preCreate)
    if Verbose :
        print('pre-test directory contains:')
        showDir()
    cmd = pathrene + ' ' + args 
# Test option I says to use input instead of direct console single key for user
# input to enable redirect from no and yes files. S tells to sort directories 
# to get Linux to produce the same display output as Windows for regression 
# testing (the results are always the same regardless of display order).
    if Windows : 
        cmd += ' -TI'
    else : 
        cmd += ' -TIS'
    print(cmd)
    if len(expect) != 0 or Quiet :
        cmd += ' > testrec'
    try :
        if Windows :
            cmdret = os.system(cmd) 
        else :
            cmdret = os.system("set -f; " + cmd) # Turn off globbing
    except KeyboardInterrupt :
        exit(1)
    if Verbose :
        print('\npost-test directory contains:')
        showDir()
    if len(expect) != 0 :
        if checkrec(expect) == 0 :
            if cmdret != 0 and not cmdErr:
                print('Unexpected command error')
                return 1
            print('Output as expected')
            return 0 # ok
        else :
            return 1 # not ok
    return 0 # Treat not tested as no error.


# ========================== TESTS ===================================
all = ['all'] # Common preDel argument to engine

# ------------------------------------------------------------------
# test1-4. Realistic tests of basic operation, including undo. Given a set of 
# patent files with long numeric names whose only useful component is their 
# sequential number. Replace all of the useless stuff with something 
# meaningful while retaining the sequence number. This tests both / (discard) 
# and * (copy all) in replacement. These tests are related by files and by 
# skipping pointless reverifications, but they don't depend on each other. 
# They can be invoked in any order.
#
# In test1, the command line contains \AS, telling rene to just show the 
# proposed changes. This also asks engine to verify the interactive output, 
# i.e. the proposed changes. The other tests in this series don't bother with 
# this, as it would be the same for all of them.
#
# In test2 the action option is removed, causing the default action, which is 
# to ask. This is automatically answered by the no file and again no files are 
# changed, which is verified by calling checkDir.
#
# test3 is the same as test2 but input is redirected to the yes file. checkDir
# verifies that the files have been renamed as expected.
#
# test4 repeats test3 but adds another invocation of rene (through engine) with
# the simple command \U, which undoes the rename. checkDir confirms that the 
# original names are restored.
# ........................................................................
patents = ['08493357-001.tif', '08493357-002.tif', '08493357-003.tif', 
'08493357-004.tif', '08493357-005.tif']
newPatents = ['hap01.tif', 'hap02.tif', 'hap03.tif', 'hap04.tif', 'hap05.tif']

def test1() :
    return engine(r'08*-0* /hap* -AS', all, patents, [
'Rename 08493357-001.tif to hap01.tif',
'Rename 08493357-002.tif to hap02.tif',
'Rename 08493357-003.tif to hap03.tif',
'Rename 08493357-004.tif to hap04.tif',
'Rename 08493357-005.tif to hap05.tif'])

def test2() :
# Same as test1 except rene action argument is missing and action defaults to 
# asking. The input is redirected to the "no" file. checkDir is called to 
# verify that the files are not renamed.
    engine(r'08*-0* /hap* < no', all, patents)
    if not Quiet : print('N') 
    return checkDir(patents, newPatents) # original names are not changed.

def test3() :
# Identical to test2 except input is redirected to the yes file. In this case
# we should see the new file names and not the original ones.
    engine(r'08*-0* /hap* < yes', all, patents)
    if not Quiet : print('Y') 
    return checkDir(newPatents, patents) # original names are changed.

def test4() :
# Identical to test3 except that rene is invoked again with just -U to undo
# the changes and we should now see the oginal names again.
    engine(r'08*-0* /hap* < yes', all, patents)
    if not Quiet : print('Y') 
    engine(r'-U')
    return checkDir(patents, newPatents) # original names are changed.

# ---------------------------------------------------------------------------
def test5() :
# Uses the same patent files for input but tests a more complex mix of anchors
# and floaters. We want to see that no parts of anchors appear in the new names
# and that all parts of floaters correctly interleave with replacement
# literals. This also verifies that adjacent *s in the replacement are handled
# correctly. Unlike tests 1-4, this is not a practical use of rene.
    return engine(r'08*33*7*.tif *A**B -AS', all, patents, [
'Rename 08493357-001.tif to 49A5-001B',
'Rename 08493357-002.tif to 49A5-002B',
'Rename 08493357-003.tif to 49A5-003B',
'Rename 08493357-004.tif to 49A5-004B',
'Rename 08493357-005.tif to 49A5-005B'])

# --------------------------------------------------------------------------
# Slice rule tests. These use the patent files and action mode -AS. Since none
# of the files are changed, they only need to be set up once. Some of these
# tests deliberately specify slice parameters that the floater can't meet. 
def test6() :
# Uses the patent files for input. Default slice takes the first two and last
# two characters of the floater.
    return engine(r'*-0* ?* S -AS', all, patents, [
'Rename 08493357-001.tif to 085701.tif',
'Rename 08493357-002.tif to 085702.tif',
'Rename 08493357-003.tif to 085703.tif',
'Rename 08493357-004.tif to 085704.tif',
'Rename 08493357-005.tif to 085705.tif'])

def test7() :
# Mode 0 slice with specified number of characters.
    return engine(r'*-0* ?* S/3/2 -AS', [], [], [
'Rename 08493357-001.tif to 0845701.tif',
'Rename 08493357-002.tif to 0845702.tif',
'Rename 08493357-003.tif to 0845703.tif',
'Rename 08493357-004.tif to 0845704.tif',
'Rename 08493357-005.tif to 0845705.tif'])

def test8() :
# Mode 1 slice.
    return engine(r'*-0* ?* S/2/6/1 -AS', [], [], [
'Rename 08493357-001.tif to 493301.tif',
'Rename 08493357-002.tif to 493302.tif',
'Rename 08493357-003.tif to 493303.tif',
'Rename 08493357-004.tif to 493304.tif',
'Rename 08493357-005.tif to 493305.tif'])

def test9() :
# Mode 0 with insufficient floater contents to meet slice specs. rene issues
# a warning but does not abort the renaming because it is possible that only
# some files in the set have this problem and the rename is still valid, even
# if somewhat unexpected. This is a corner case failure. The slice specifies 
# one more character than the floater has.
    return engine(r'*-0* ?* S/3/6/0 -AS', [], [], [
'Warning: 08493357 is smaller than the slice',
'Rename 08493357-001.tif to 08449335701.tif',
'Warning: 08493357 is smaller than the slice',
'Rename 08493357-002.tif to 08449335702.tif',
'Warning: 08493357 is smaller than the slice',
'Rename 08493357-003.tif to 08449335703.tif',
'Warning: 08493357 is smaller than the slice',
'Rename 08493357-004.tif to 08449335704.tif',
'Warning: 08493357 is smaller than the slice',
'Rename 08493357-005.tif to 08449335705.tif'])

def test10() :
# Similar to test9 but a corner case success. The slice specifies exactly as 
# many characters as the floater has. It is still a silly use of slice for
# these files since they all have the same length and this just takes the
# entire floater.
    return engine(r'*-0* ?* S/3/5/0 -AS', [], [], [
'Rename 08493357-001.tif to 0849335701.tif',
'Rename 08493357-002.tif to 0849335702.tif',
'Rename 08493357-003.tif to 0849335703.tif',
'Rename 08493357-004.tif to 0849335704.tif',
'Rename 08493357-005.tif to 0849335705.tif'])

def test11() :
# Mode 1 with insufficient floater contents. Corner case failure (warning) with
# the sentinel index equal to floater length + 1.
    return engine(r'*-0* ?* S/4/9/1 -AS', [], [], [
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-001.tif to 335701.tif',
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-002.tif to 335702.tif',
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-003.tif to 335703.tif',
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-004.tif to 335704.tif',
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-005.tif to 335705.tif'])

def test12() :
# Mode 1 slice success corner case where the sentinel index is exactly equal to
# the floater contents length. 
    return engine(r'*-0* ?* S/4/8/1 -AS', [], [], [
'Rename 08493357-001.tif to 335701.tif',
'Rename 08493357-002.tif to 335702.tif',
'Rename 08493357-003.tif to 335703.tif',
'Rename 08493357-004.tif to 335704.tif',
'Rename 08493357-005.tif to 335705.tif'])

def test13() :
# Mode 1 with improperly specified slice, with starting index > sentinel. This
# could be detected before processing files but that would make it a special
# case. Instead, rene folds it into the general warning, which can't be done
# until the floater contents are known.
    return engine(r'*-0* ?* S/4/3/1 -AS', [], [], [
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-001.tif to 01.tif',
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-002.tif to 02.tif',
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-003.tif to 03.tif',
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-004.tif to 04.tif',
'Warning: 08493357 cannot satisfy the slice',
'Rename 08493357-005.tif to 05.tif'])

# ----------------------------------------------------------------------------
# Bump rule tests. The first of these is a very basic and common use for name 
# bumping a set of similarly named files. The second tests numeric carry using 
# the same (patent) file set. The rest exercise more complex bumping, which 
# requires more file variety.

def test14() :
# A realistic example where numbered files are bumped up to open up the name
# space to insert some new files. The entire original file name is unchanged
# except for the one bumped field. Therefore, the replacement exactly matches
# the filter except in this one field. Note that rene bumps the root, so the
# bumped floater can include the extension, in this example just for 
# convenience, as all files have the same extension, which could be a literal
# in the replacement.
    return engine(r'0849*-0* 0849*-0? B/10 -AS', all, patents, [
'Rename 08493357-001.tif to 08493357-011.tif',
'Rename 08493357-002.tif to 08493357-012.tif',
'Rename 08493357-003.tif to 08493357-013.tif',
'Rename 08493357-004.tif to 08493357-014.tif',
'Rename 08493357-005.tif to 08493357-015.tif'])

def test15() :
# Similar to the preceding test but testing bump's greedy carry for numeric 
# fields. Bump retains the current field width, expanding it only as needed
# to support the new value. The Bump argument does not support a width
# parameter (unlike sequential injector).
    return engine(r'0849*-0* 0849*-? B/997 -AS', [], [], [
'Rename 08493357-001.tif to 08493357-998.tif',
'Rename 08493357-002.tif to 08493357-999.tif',
'Rename 08493357-003.tif to 08493357-1000.tif',
'Rename 08493357-004.tif to 08493357-1001.tif',
'Rename 08493357-005.tif to 08493357-1002.tif'])

# All of the following tests use bumpNames as the original file set. The 
# renames are compared to expectations but not performed, so only the first 
# test needs to set up the starting conditions. Each file is an example of a 
# class of file names. This is not a realistic use. The names are designed to 
# appear in a predictable directory order and to test a variety of 
# characteristics. More typically, all of the files in a set would have greater
# commonality.
# my0ABC990 ends in numeric and has no extension.
# my0ABC999.txt ends in numeric and has one extension.
# my0ABC9999.tar.gzip ends in numeric and has two extensions.
# my1ABC ends in alpha and has no extension.
# my1ABC.txt ends in alpha and has one extension.
# my1ABC.tar.gzip ends in alpha and has two extensions.
# my2ABC{} ends in punctuatioh and has no extension.
# my2ABC{}.txt ends in punctuatioh and has one extension.
# my2ABC{}.tar.gzip ends in punctuatioh and has two extensions. 
bumpNames = [
'my0ABC990', 'my0ABC999.txt', 'my0ABC9999.tar.gzip', 
'my1ABC', 'my1Xzz.txt', 'my1ABZ.tar.gzip',
'my2ABC{}', 'my2ABC{}.txt', 'my2ABC{}.tar.gzip']

def test16() :
# Bump every file that passes the filter by the default step 1. 
    return engine(r'my* my? B -AS', all, bumpNames, [
'Rename my0ABC990 to my0ABC991',
'Rename my0ABC999.txt to my0ABC1000.txt',
'Rename my0ABC9999.tar.gzip to my0ABC10000.tar.gzip',
'Rename my1ABC to my1ABD',
'Rename my1ABZ.tar.gzip to my1ABAA.tar.gzip',
'Rename my1Xzz.txt to my1Xzaa.txt',
'Rename my2ABC{} to my2ABC{}1',
'Rename my2ABC{}.tar.gzip to my2ABC{}1.tar.gzip',
'Rename my2ABC{}.txt to my2ABC{}1.txt'])

def test17() :
# Bump every file by 10
    return engine(r'my* my? B/10 -AS', [], [], [
'Rename my0ABC990 to my0ABC1000',
'Rename my0ABC999.txt to my0ABC1009.txt',
'Rename my0ABC9999.tar.gzip to my0ABC10009.tar.gzip',
'Rename my1ABC to my1ABM',
'Rename my1ABZ.tar.gzip to my1ABAJ.tar.gzip',
'Rename my1Xzz.txt to my1Xzaj.txt',
'Rename my2ABC{} to my2ABC{}10',
'Rename my2ABC{}.tar.gzip to my2ABC{}10.tar.gzip',
'Rename my2ABC{}.txt to my2ABC{}10.txt'])

def test18() :
# Bump only numeric files (by default 1). Copy other floater types. This turns
# on display of files that pass the filter but are not changed by the 
# replacement. This is -P bit 3. Bit 0, which turns on rename display also
# must be set, even though it is the default, when the -P option is in the
# command. Both Bump mode and -P option mode are bit maps, for which binary
# or hexadecimal may be preferable to decimal. Binary is used for both in this
# command just to test it. Bump mode 5 and Show mode 9 would both be more
# convenient.
    return engine(r'my* my? B//0101 -AS -P01001', [], [], [
'Rename my0ABC990 to my0ABC991',
'Rename my0ABC999.txt to my0ABC1000.txt',
'Rename my0ABC9999.tar.gzip to my0ABC10000.tar.gzip',
'my1ABC is unchanged',
'my1ABZ.tar.gzip is unchanged',
'my1Xzz.txt is unchanged',
'my2ABC{} is unchanged',
'my2ABC{}.tar.gzip is unchanged',
'my2ABC{}.txt is unchanged'])

def test19() :
# Bump only alpha. Copy numeric and non-alphanumeric floaters. Coincidentally,
# test Bump mode and -P parameter as decimal.
    return engine(r'my* my? B//6 -AS -P9', [], [], [
'my0ABC990 is unchanged',
'my0ABC999.txt is unchanged',
'my0ABC9999.tar.gzip is unchanged',
'Rename my1ABC to my1ABD',
'Rename my1ABZ.tar.gzip to my1ABAA.tar.gzip',
'Rename my1Xzz.txt to my1Xzaa.txt',
'my2ABC{} is unchanged',
'my2ABC{}.tar.gzip is unchanged',
'my2ABC{}.txt is unchanged'])

def test20() :
# Bump only non-alphanumeric. Copy numeric and alpha floaters. Coincidentally,
# test Bump mode and -P parameter as hexadecimal.
    return engine(r'my* my? B//0x3 -AS -P0x9', [], [], [
'my0ABC990 is unchanged',
'my0ABC999.txt is unchanged',
'my0ABC9999.tar.gzip is unchanged',
'my1ABC is unchanged',
'my1ABZ.tar.gzip is unchanged',
'my1Xzz.txt is unchanged',
'Rename my2ABC{} to my2ABC{}1',
'Rename my2ABC{}.tar.gzip to my2ABC{}1.tar.gzip',
'Rename my2ABC{}.txt to my2ABC{}1.txt'])

def test21() :
# Bump numeric. Discard alpha and non-alphanumeric floaters. Turn on display of
# collision avoidance (-P bit 1) to show the origin of some new names caused by
# deleting distinquishing components of the original name. Collision avoidance
# display shows the proposed entire file name but only the root as it changes
# during the process. Note that the collisions are not with existing files but
# with preceding new names even though the files haven't been renamed yet (and
# won't be in this test because of option -AS).
    return engine(r'my* my? B//0x55 -AS -P0xB', [], [], [
'Rename my0ABC990 to my0ABC991',
'Rename my0ABC999.txt to my0ABC1000.txt',
'Rename my0ABC9999.tar.gzip to my0ABC10000.tar.gzip',
'Rename my1ABC to my',
'Rename my1ABZ.tar.gzip to my.tar.gzip',
'Rename my1Xzz.txt to my.txt',
'Name collision: my>my0',
'Rename my2ABC{} to my0',
'Name collision: my.tar.gzip>my0',
'Rename my2ABC{}.tar.gzip to my0.tar.gzip',
'Name collision: my.txt>my0',
'Rename my2ABC{}.txt to my0.txt'])

def test22() :
# Bump alpha. Discard numeric and non-alphanumeric floaters.
    return engine(r'my* my? B//0x66 -AS -P11', [], [], [
'Rename my0ABC990 to my',
'Rename my0ABC999.txt to my.txt',
'Rename my0ABC9999.tar.gzip to my.tar.gzip',
'Rename my1ABC to my1ABD',
'Rename my1ABZ.tar.gzip to my1ABAA.tar.gzip',
'Rename my1Xzz.txt to my1Xzaa.txt',
'Name collision: my>my0',
'Rename my2ABC{} to my0',
'Name collision: my.tar.gzip>my0',
'Rename my2ABC{}.tar.gzip to my0.tar.gzip',
'Name collision: my.txt>my0',
'Rename my2ABC{}.txt to my0.txt'])

def test23() :
# Bump non-alphanumeric. Discard numeric and alpha floaters.
    return engine(r'my* my? B//0x33 -AS -P11', [], [], [
'Rename my0ABC990 to my',
'Rename my0ABC999.txt to my.txt',
'Rename my0ABC9999.tar.gzip to my.tar.gzip',
'Name collision: my>my0',
'Rename my1ABC to my0',
'Name collision: my.tar.gzip>my0',
'Rename my1ABZ.tar.gzip to my0.tar.gzip',
'Name collision: my.txt>my0',
'Rename my1Xzz.txt to my0.txt',
'Rename my2ABC{} to my2ABC{}1',
'Rename my2ABC{}.tar.gzip to my2ABC{}1.tar.gzip',
'Rename my2ABC{}.txt to my2ABC{}1.txt'])

# --------------------------------------------------------------------------
# Inserter rule tests.

def test24() :
# Default I inserts sequential number starting at 0. 
    return engine(r'*.tif hap:.tif I -AS', all, patents, [
'Rename 08493357-001.tif to hap0.tif',
'Rename 08493357-002.tif to hap1.tif',
'Rename 08493357-003.tif to hap2.tif',
'Rename 08493357-004.tif to hap3.tif',
'Rename 08493357-005.tif to hap4.tif'])

def test25() :
# I with starting number and specified (minimum) width. In this example the 
# floater is not used but the replacement doesn't need to explicitly discard
# it with the / variable because it is inherently dicarded if there are no
# inclusive (*) variables.
    return engine(r'*.tif hap:.tif I/99//3 -AS', [], [], [
'Rename 08493357-001.tif to hap099.tif',
'Rename 08493357-002.tif to hap100.tif',
'Rename 08493357-003.tif to hap101.tif',
'Rename 08493357-004.tif to hap102.tif',
'Rename 08493357-005.tif to hap103.tif'])

def test26() :
# Insert incrementing string. 
    return engine(r'*.tif :-hap.tif I/A -AS', [], [], [
'Rename 08493357-001.tif to A-hap.tif',
'Rename 08493357-002.tif to B-hap.tif',
'Rename 08493357-003.tif to C-hap.tif',
'Rename 08493357-004.tif to D-hap.tif',
'Rename 08493357-005.tif to E-hap.tif'])

def test27() :
# Insert incrementing string with carry, illustrating that carry only goes to 
# the last character. This is not a very realistic example because alpha 
# sequences in file names typically involve a one-character field and short
# spans.
    return engine(r'*.tif :-hap.tif I/zy -AS', [], [], [
'Rename 08493357-001.tif to zy-hap.tif',
'Rename 08493357-002.tif to zz-hap.tif',
'Rename 08493357-003.tif to zaa-hap.tif',
'Rename 08493357-004.tif to zab-hap.tif'])

# --------------------------------------------------------------------------
# Collision avoidance tests. The conditions are most conveniently set up by 
# repeatedly renaming and saving the same set of original files. This is not a
# very realistic situation. Real collisions are more likely to occur more 
# randomly and unexpectly, as in the Bump rule examples, where specific types 
# of floaters don't fit a desired pattern and are discarded, reducing 
# distinguishing features of a name. -P11 option causes normal rename result
# and collision avoidance process to be displayed. We don't need checkDir to
# verify that the files are actually being renamed. The increasingly complex
# avoidance process proves that they are.

caNames = ['my-01.png', 'my-02.png', 'my-03.png', 'my-04.png']

def test28() :
# Set up conditions for name collisions. This creates the original name set of
# png files and renames them. It also creates some files with the same root but
# different extension to verify that there are no false collisions based on root
# even though collision avoidance is implemented on the root.
    delThese(all)
    createThese(['his-01.gif', 'his-010.gif', 'his-011.gif', 'his012.gif'])
    return engine(r'my-* his-* -AR -P11',[], caNames, [
'Rename my-01.png to his-01.png',
'Rename my-02.png to his-02.png',
'Rename my-03.png to his-03.png',
'Rename my-04.png to his-04.png'])


def test29() :
# This depends on being preceded by test28. It recreates the same original file
# set, caNames, and tries to do the same renaming. Each new name encounters
# collision and the default collision avoidance means is to append 0. The first
# file my-01.png would be renamed his-01.png but this is changed to 
# his-010.png, which is accepted. The existing his-010.gif is ignored. This
# represents a single-stage avoidance process.
    return engine(r'my-* his-* -AR -P11', [], caNames, [
'Name collision: his-01.png>his-010',
'Rename my-01.png to his-010.png',
'Name collision: his-02.png>his-020',
'Rename my-02.png to his-020.png',
'Name collision: his-03.png>his-030',
'Rename my-03.png to his-030.png',
'Name collision: his-04.png>his-040',
'Rename my-04.png to his-040.png'])

def test30() :
# This must be preceded by tests 28 and 29. The command is identical to test29 
# but the results are not. This time a two-stage collision avoidance process 
# is required to avoid the names created in test28 and in test29.
    return engine(r'my-* his-* -AR -P11', [], caNames, [
'Name collision: his-01.png>his-010>his-011',
'Rename my-01.png to his-011.png',
'Name collision: his-02.png>his-020>his-021',
'Rename my-02.png to his-021.png',
'Name collision: his-03.png>his-030>his-031',
'Rename my-03.png to his-031.png',
'Name collision: his-04.png>his-040>his-041',
'Rename my-04.png to his-041.png'])

def test31() :
# This must be preceded by tests 28-30. Again the command is identical to 
# test 29 but this time a three-stage avoidance process is required.
    return engine(r'my-* his-* -AR -P11', [], caNames, [
'Name collision: his-01.png>his-010>his-011>his-012',
'Rename my-01.png to his-012.png',
'Name collision: his-02.png>his-020>his-021>his-022',
'Rename my-02.png to his-022.png',
'Name collision: his-03.png>his-030>his-031>his-032',
'Rename my-03.png to his-032.png',
'Name collision: his-04.png>his-040>his-041>his-042',
'Rename my-04.png to his-042.png'])

# -XM collision avoidance by merge.
# The next series of collision avoidance tests uses merge instead of append. 
# The same file set is used. All of these files have numeric name tail. Merge
# automatically adapts to this.
# This series must be preceded by test28 but the effects of 29-31 can be 
# ignored because the two avoidance mechanisms don't collide in this case 
# (they can under deliberately contrived circumstances). With merge, collision
# is avoided by incrementing the tail of the root name. But with this file set
# that creates a name that is already used in the set. In the first test (32)
# the first file requires four stages to reach an unused name. Coincidentally,
# that same number of stages is needed for each successive file because the
# process must go one step further to avoid the preceding modified name but
# also the starting name has advanced by one step and the two cancel out. The
# preceding new names have not actually been applied to the files but collision
# avoidance includes them in its calculations.
def test32() :
    return engine(r'my-* his-* -AR -P11 -XM', [], caNames, [
'Name collision: his-01.png>his-02>his-03>his-04>his-05',
'Rename my-01.png to his-05.png',
'Name collision: his-02.png>his-03>his-04>his-05>his-06',
'Rename my-02.png to his-06.png',
'Name collision: his-03.png>his-04>his-05>his-06>his-07',
'Rename my-03.png to his-07.png',
'Name collision: his-04.png>his-05>his-06>his-07>his-08',
'Rename my-04.png to his-08.png'])

def test33() :
# Renaming the same original file set again now requires eight stages to avoid
# the original files and the preceding modified names.
    return engine(r'my-* his-* -AR -P11 -XM', [], caNames, [
'Name collision: his-01.png>his-02>his-03>his-04>his-05>his-06>his-07>his-08>his-09',
'Rename my-01.png to his-09.png',
'Name collision: his-02.png>his-03>his-04>his-05>his-06>his-07>his-08>his-09>his-10',
'Rename my-02.png to his-10.png',
'Name collision: his-03.png>his-04>his-05>his-06>his-07>his-08>his-09>his-10>his-11',
'Rename my-03.png to his-11.png',
'Name collision: his-04.png>his-05>his-06>his-07>his-08>his-09>his-10>his-11>his-12',
'Rename my-04.png to his-12.png'])

def test34() :
# Repeating the same renaming again further increases the number of collision 
# avoidance stages. The process stops at 10 because it indicates a misuse of 
# collision avoidance. Better would be more deliberate renaming using either 
# Bump or Insert rules in the replacement. In this test, the number of stages 
# is no longer the same for all files. The first two files are not renamed 
# because of the stage limit, giving the remainder enough head room to find a 
# new name under the limit. 
    return engine(r'my-* his-* -AR -P11 -XM', [], caNames, [
'Name collision: his-01.png>his-02>his-03>his-04>his-05>his-06>his-07>his-08>his-09>his-10>his-11',
'Unresolvable collision trying to rename my-01.png',
'Name collision: his-02.png>his-03>his-04>his-05>his-06>his-07>his-08>his-09>his-10>his-11>his-12',
'Unresolvable collision trying to rename my-02.png',
'Name collision: his-03.png>his-04>his-05>his-06>his-07>his-08>his-09>his-10>his-11>his-12>his-13',
'Rename my-03.png to his-13.png',
'Name collision: his-04.png>his-05>his-06>his-07>his-08>his-09>his-10>his-11>his-12>his-13>his-14',
'Rename my-04.png to his-14.png'])

# ---------------------------------------------------------------------------------
# Collision avoidance using alpha instead of numeric (the default). This still
# simply appends; it is not merge, which automatically adapts to the type of
# name tail. As with merge, this series depends on tests 28 and 29 but doesn't
# care about the preceding numeric and merge tests. Alpha collision avoidance 
# is selected by -Xstring. string is typically A but can be any alpha string
# that does not contains S, C, or M, which are reserved.
 
def test35() :
# This is a realistic example with just the single letter A starting the
# avoidance process.
    return engine(r'my-* his-* -AR -P11 -XA', [], caNames, [
'Name collision: his-01.png>his-01A',
'Rename my-01.png to his-01A.png',
'Name collision: his-02.png>his-02A',
'Rename my-02.png to his-02A.png',
'Name collision: his-03.png>his-03A',
'Rename my-03.png to his-03A.png',
'Name collision: his-04.png>his-04A',
'Rename my-04.png to his-04A.png'])

def test36() :
# This command line is identical to the previous but now previously renamed
# files also must be avoided. This looks like it might doing an alpha merge but
# that is not what is happening. The collision avoidance process first tries 
# appending A and, when that experiences collision, increments the appended
# character. i.e. it isn't incrementing the name tail.
    return engine(r'my-* his-* -AR -P11 -XA', [], caNames, [
'Name collision: his-01.png>his-01A>his-01B',
'Rename my-01.png to his-01B.png',
'Name collision: his-02.png>his-02A>his-02B',
'Rename my-02.png to his-02B.png',
'Name collision: his-03.png>his-03A>his-03B',
'Rename my-03.png to his-03B.png',
'Name collision: his-04.png>his-04A>his-04B',
'Rename my-04.png to his-04B.png'])

def test37() :
# This is another variation on alpha collision avoidance. It also depends on 
# tests 28 and 29 and is not impacted by any of the preceding collision 
# avoidance results, simply because it uses a different starting letter. 
# Independently of that, it uses 'z' as the starting point to test case 
# continuity and alpha carry.
    return engine(r'my-* his-* -AR -P11 -Xz', [], caNames, [
'Name collision: his-01.png>his-01z',
'Rename my-01.png to his-01z.png',
'Name collision: his-02.png>his-02z',
'Rename my-02.png to his-02z.png',
'Name collision: his-03.png>his-03z',
'Rename my-03.png to his-03z.png',
'Name collision: his-04.png>his-04z',
'Rename my-04.png to his-04z.png'])

def test38() :
# Command line identical to the preceding test. This tests case preservation 
# and alpha carry, i.e. z + 1 = aa, in collision avoidance. 
    return engine(r'my-* his-* -AR -P11 -Xz', [], caNames, [
'Name collision: his-01.png>his-01z>his-01aa',
'Rename my-01.png to his-01aa.png',
'Name collision: his-02.png>his-02z>his-02aa',
'Rename my-02.png to his-02aa.png',
'Name collision: his-03.png>his-03z>his-03aa',
'Rename my-03.png to his-03aa.png',
'Name collision: his-04.png>his-04z>his-04aa',
'Rename my-04.png to his-04aa.png'])

# --------------------------------------------------------------------------
# Collision avoidance string tests. Preceding tests are single-letter initial 
# value. 
def test39() :
    return engine(r'my-* his-* -AR -P11 -X/xxx0/', [], caNames, [
'Name collision: his-01.png>his-01xxx0',
'Rename my-01.png to his-01xxx0.png',
'Name collision: his-02.png>his-02xxx0',
'Rename my-02.png to his-02xxx0.png',
'Name collision: his-03.png>his-03xxx0',
'Rename my-03.png to his-03xxx0.png',
'Name collision: his-04.png>his-04xxx0',
'Rename my-04.png to his-04xxx0.png'])

def test40() :
    return engine(r'my-* his-* -AS -P11 -X/xxx0/', [], caNames, [
'Name collision: his-01.png>his-01xxx0>his-01xxx1',
'Rename my-01.png to his-01xxx1.png',
'Name collision: his-02.png>his-02xxx0>his-02xxx1',
'Rename my-02.png to his-02xxx1.png',
'Name collision: his-03.png>his-03xxx0>his-03xxx1',
'Rename my-03.png to his-03xxx1.png',
'Name collision: his-04.png>his-04xxx0>his-04xxx1',
'Rename my-04.png to his-04xxx1.png'])

def test41() :
    return engine(r'my-* his-* -AR -P11 -X/xxxZ/', [], caNames, [
'Name collision: his-01.png>his-01xxxZ',
'Rename my-01.png to his-01xxxZ.png',
'Name collision: his-02.png>his-02xxxZ',
'Rename my-02.png to his-02xxxZ.png',
'Name collision: his-03.png>his-03xxxZ',
'Rename my-03.png to his-03xxxZ.png',
'Name collision: his-04.png>his-04xxxZ',
'Rename my-04.png to his-04xxxZ.png'])

def test42() :
    return engine(r'my-* his-* -AS -P11 -X/xxxZ/', [], caNames, [
'Name collision: his-01.png>his-01xxxZ>his-01xxxAA',
'Rename my-01.png to his-01xxxAA.png',
'Name collision: his-02.png>his-02xxxZ>his-02xxxAA',
'Rename my-02.png to his-02xxxAA.png',
'Name collision: his-03.png>his-03xxxZ>his-03xxxAA',
'Rename my-03.png to his-03xxxAA.png',
'Name collision: his-04.png>his-04xxxZ>his-04xxxAA',
'Rename my-04.png to his-04xxxAA.png'])
    
# -------------------------------------------------------------------------
# Collision avoidance punctuation. This comprises punctuation 
# characters  `~!@#$%^&()_-+][}{ for which there is no incrementation. 
# Frequently, this doesn't encounter more than one stage of collision 
# avoidance but if more are needed they must be either alpha or numeric. The 
# punctuation string may be located in any one of three positions, prefix (at 
# the beginning of root), mid (immediately after the requested root name), and 
# suffix (at the end of the final root, including additional collision 
# avoidance characters). mid is the default. A single , at the begining of the 
# string definition makes it prefix. ,, makes it suffix.  Merge and mid 
# position are incompatible. If both are specified the position is 
# automatically changed to suffix. prefix can collide only with prefix.  mid 
# and suffix produce the same first avoidance name and can collide on this but 
# no further because they have reversed punctuation and additional character 
# groups.

def test43() : # CA punctuation suffix 
# Depends on all preceding tests from 28 to 38. ,, declares this to be suffix,
# but this is indistinguishable from mid on this first test. The difference 
# becomes apparent on subsequent collisions.
    return engine(r'my-* his-* -AR -P11 -X,,{$}', [], caNames, [
'Name collision: his-01.png',
'Rename my-01.png to his-01{$}.png',
'Name collision: his-02.png',
'Rename my-02.png to his-02{$}.png',
'Name collision: his-03.png',
'Rename my-03.png to his-03{$}.png',
'Name collision: his-04.png',
'Rename my-04.png to his-04{$}.png'])

def test44() : # CA punctuation suffix
# Depends on tests from 28 to 39. This is identical to test39 but this time 
# encounters the new names created by collision avoidance in test39. e.g.it 
# tries to rename my-01.png to his-01.png but that file already exists so it 
# tries his-01{$}.png but that already exists from test39 so it uses the 
# default CA numeric append his-010{$}, which is free.
    return engine(r'my-* his-* -AR -P11 -X,,{$}', [], caNames, [
'Name collision: his-01.png>his-010{$}',
'Rename my-01.png to his-010{$}.png',
'Name collision: his-02.png>his-020{$}',
'Rename my-02.png to his-020{$}.png',
'Name collision: his-03.png>his-030{$}',
'Rename my-03.png to his-030{$}.png',
'Name collision: his-04.png>his-040{$}',
'Rename my-04.png to his-040{$}.png'])

def test45() : # CA punctuation suffix
# Depends on tests from 28 to 40. This is identical to test39 and 40 but now 
# encounters the names created by 39 and 40. The collision-free names are much
# more like test 40 than 39 because the CA numeric field has already been 
# established in 40. e.g. test 40 renames my-01.png to his-010{$}.png while 
# test 41 renames it his-011{$}.png.
    return engine(r'my-* his-* -AR -P11 -X,,{$}', [], caNames, [
'Name collision: his-01.png>his-010{$}>his-011{$}',
'Rename my-01.png to his-011{$}.png',
'Name collision: his-02.png>his-020{$}>his-021{$}',
'Rename my-02.png to his-021{$}.png',
'Name collision: his-03.png>his-030{$}>his-031{$}',
'Rename my-03.png to his-031{$}.png',
'Name collision: his-04.png>his-040{$}>his-041{$}',
'Rename my-04.png to his-041{$}.png'])

def test46() : # CA punctuation mid
# Depends on tests from 28 to 41, which create his-01{$}.png. test42 is nearly 
# identical to 39 but declares the CA string as mid (default) instead of 
# suffix. The two collide only at this one point. e.g. we would like to rename
# my-01.png to his-01.png but this is a collision so we try his-01{$}.png but 
# that collides with a name produced by test39. Finally, we try his-01{$}0.png
# which is free because test40 generated his-010{$}.png to respond to this same
# collision.
    return engine(r'my-* his-* -AR -P11 -X{$}', [], caNames, [
'Name collision: his-01.png>his-01{$}0',
'Rename my-01.png to his-01{$}0.png',
'Name collision: his-02.png>his-02{$}0',
'Rename my-02.png to his-02{$}0.png',
'Name collision: his-03.png>his-03{$}0',
'Rename my-03.png to his-03{$}0.png',
'Name collision: his-04.png>his-04{$}0',
'Rename my-04.png to his-04{$}0.png'])

def test47() : # CA punctuation mid
# Depends on 28-42. This is the same as test42 but now has to avoid collision 
# with names created by that test. e.g. test42 created  his-01{$}0.png, which 
# we now avoid by creating his-01{$}1.png.
    return engine(r'my-* his-* -AR -P11 -X{$}', [], caNames, [
'Name collision: his-01.png>his-01{$}0>his-01{$}1',
'Rename my-01.png to his-01{$}1.png',
'Name collision: his-02.png>his-02{$}0>his-02{$}1',
'Rename my-02.png to his-02{$}1.png',
'Name collision: his-03.png>his-03{$}0>his-03{$}1',
'Rename my-03.png to his-03{$}1.png',
'Name collision: his-04.png>his-04{$}0>his-04{$}1',
'Rename my-04.png to his-04{$}1.png'])

def test48() : # CA punctuation prefix
# Depends on tests 28-38 but not 39-43 because this uses string prefix, which 
# cannot collide with mid and suffix. Nevertheless, it is good to run all of 
# the tests from 28 to 43 in order to show this independence. 
    return engine(r'my-* his-* -AR -P11 -X,{$}', [], caNames, [
'Name collision: his-01.png',
'Rename my-01.png to {$}his-01.png',
'Name collision: his-02.png',
'Rename my-02.png to {$}his-02.png',
'Name collision: his-03.png',
'Rename my-03.png to {$}his-03.png',
'Name collision: his-04.png',
'Rename my-04.png to {$}his-04.png'])

def test49() : # CA punctuation prefix
# Depends on test 28-38 and 44. This is identical to the previous but now 
# encounters names that it created. CA is by the default numeric append.
    return engine(r'my-* his-* -AR -P11 -X,{$}', [], caNames, [
'Name collision: his-01.png>{$}his-010',
'Rename my-01.png to {$}his-010.png',
'Name collision: his-02.png>{$}his-020',
'Rename my-02.png to {$}his-020.png',
'Name collision: his-03.png>{$}his-030',
'Rename my-03.png to {$}his-030.png',
'Name collision: his-04.png>{$}his-040',
'Rename my-04.png to {$}his-040.png'])

# All of the preceding CA examples with CA punctuation have allowed the default 
# numeric append resolve the collision when the punctuation alone did not. The 
# following tests use merge, which folds the iterating CA into the root name. 
# The preceding CA punctuation tests have produced interfering names. Pristine 
# conditions are established in the first of these tests by deleting all before
# creating caNames and then performing the rename, which won't encounter 
# collisions. Thus, it really doesn't test anything that we don't already
# know even though its command line does declare the CA scheme -XM,{$}.
# This and subsequent tests don't depend on any preceding tests.

def test50() : # CA punctuation prefix with merge. Conditions initializer.
    return engine(r'my-* his-* -AR -P11 -XM,{$}', all, caNames, [])

def test51() : # CA punctuation prefix with merge
# This time there are collisions with the new his-0x.png files but they are 
# resolved by the punctuation prefix and merge still isn't necessary.
    return engine(r'my-* his-* -AR -P11 -XM,{$}', [], caNames, [
'Name collision: his-01.png',
'Rename my-01.png to {$}his-01.png',
'Name collision: his-02.png',
'Rename my-02.png to {$}his-02.png',
'Name collision: his-03.png',
'Rename my-03.png to {$}his-03.png',
'Name collision: his-04.png',
'Rename my-04.png to {$}his-04.png'])

def test52() : # CA punctuation prefix with merge
# Identical to previous but this time merge is needed to avoid the names 
# created by that test.
    return engine(r'my-* his-* -AR -P11 -XM,{$}', [], caNames, [
'Name collision: his-01.png>{$}his-02>{$}his-03>{$}his-04>{$}his-05',
'Rename my-01.png to {$}his-05.png',
'Name collision: his-02.png>{$}his-03>{$}his-04>{$}his-05>{$}his-06',
'Rename my-02.png to {$}his-06.png',
'Name collision: his-03.png>{$}his-04>{$}his-05>{$}his-06>{$}his-07',
'Rename my-03.png to {$}his-07.png',
'Name collision: his-04.png>{$}his-05>{$}his-06>{$}his-07>{$}his-08',
'Rename my-04.png to {$}his-08.png'])

def test53() : # CA punctuation mid with merge. 
# Depends on 46-48
# The command line declares CA punctuation as mid but merge overrides this, making
# it suffix even though merge is not actually needed on this first round
# because the punctuation alone will clear the collision.
    return engine(r'my-* his-* -AR -P11 -XM{$}', [], caNames, [
'Name collision: his-01.png',
'Rename my-01.png to his-01{$}.png',
'Name collision: his-02.png',
'Rename my-02.png to his-02{$}.png',
'Name collision: his-03.png',
'Rename my-03.png to his-03{$}.png',
'Name collision: his-04.png',
'Rename my-04.png to his-04{$}.png'])

def test54() : # CA punctuation suffix with merge.
# Depends on 46-49
    return engine(r'my-* his-* -AR -P11 -XM,,{$}', [], caNames, [
'Name collision: his-01.png>his-02{$}>his-03{$}>his-04{$}>his-05{$}',
'Rename my-01.png to his-05{$}.png',
'Name collision: his-02.png>his-03{$}>his-04{$}>his-05{$}>his-06{$}',
'Rename my-02.png to his-06{$}.png',
'Name collision: his-03.png>his-04{$}>his-05{$}>his-06{$}>his-07{$}',
'Rename my-03.png to his-07{$}.png',
'Name collision: his-04.png>his-05{$}>his-06{$}>his-07{$}>his-08{$}',
'Rename my-04.png to his-08{$}.png'])

# ------------------------------------------------------------------
#                         FLOATER REORDERING TESTS
# These don't depend on any preceding tests. The first one deletes all and
# creates patents but all are -AS to just show the renames without doing them.

def test55() :
# Sanity check that -O in default order is identical to default.
    return engine(r'08*33*-*.tif ***.tif -AS -O0,1,2', all, patents, [
'Rename 08493357-001.tif to 4957001.tif',
'Rename 08493357-002.tif to 4957002.tif',
'Rename 08493357-003.tif to 4957003.tif',
'Rename 08493357-004.tif to 4957004.tif',
'Rename 08493357-005.tif to 4957005.tif'])

def test56() : # Reverse order
    return engine(r'08*33*-*.tif ***.tif -AS -O2,1,0', [], [], [
'Rename 08493357-001.tif to 0015749.tif',
'Rename 08493357-002.tif to 0025749.tif',
'Rename 08493357-003.tif to 0035749.tif',
'Rename 08493357-004.tif to 0045749.tif',
'Rename 08493357-005.tif to 0055749.tif'])

def test57() : # Scrambled order
    return engine(r'08*33*-*.tif *my*dog*.tif -AS -O1,0,2', [], [], [
'Rename 08493357-001.tif to 57my49dog001.tif',
'Rename 08493357-002.tif to 57my49dog002.tif',
'Rename 08493357-003.tif to 57my49dog003.tif',
'Rename 08493357-004.tif to 57my49dog004.tif',
'Rename 08493357-005.tif to 57my49dog005.tif'])

def test58() : # Auto-completion
    return engine(r'08*33*-*.tif ***.tif -AS -O1', [], [], [
'Rename 08493357-001.tif to 5749001.tif',
'Rename 08493357-002.tif to 5749002.tif',
'Rename 08493357-003.tif to 5749003.tif',
'Rename 08493357-004.tif to 5749004.tif',
'Rename 08493357-005.tif to 5749005.tif'])

def test59() : # Parameter error detection.
    return engine(r'08*33*-*.tif ***.tif -AS -O1,2,3', [], [], 
['Order option index 3 > maximum index 2'], True)

# ----------------------------------------------------------------------------------
#                     Dot Files
dotFiles = ['dog.cfg', 'cat.cfg', 'mouse.cfg', '.cfg', '.emacx', '.bashx']

def test60() : # *.* skips .name files.
    return engine(r'*.cfg *.food  -AS', all, dotFiles, [
'Rename cat.cfg to cat.food',
'Rename dog.cfg to dog.food',
'Rename mouse.cfg to mouse.food'])

def test61() : # Depends on test60.
# .* skips name.* files.
    return engine(r'.* .*.txt -AR', [], [], [
'Rename .bashx to .bashx.txt',
'Rename .cfg to .cfg.txt',
'Rename .emacx to .emacx.txt'])

def test62() : # Depends on 60-61
# Nearly the same as previous but the filter is .*. which allows only names 
# without extension through the filter. Otherwise, this would correctly rename 
# e.g. .bashx.txt to .bashx.txt.txt, which is not what we are trying to 
# achieve here. We only want to see that collision avoidance is correctly 
# applied to the root even if it begins with .
    return engine(r'.*. .*.txt -AR -P11', [], dotFiles, [
'Name collision: .bashx.txt>.bashx0',
'Rename .bashx to .bashx0.txt',
'Name collision: .cfg.txt>.cfg0',
'Rename .cfg to .cfg0.txt',
'Name collision: .emacx.txt>.emacx0',
'Rename .emacx to .emacx0.txt'])

def test63() : # Depends on 60-62
# Repeat previous to show next collision step (of default CA) Also this only 
# shows what would be done. We don't need any more of these.
    return engine(r'.*. .*.txt -AS -P11', [], dotFiles, [
'Name collision: .bashx.txt>.bashx0>.bashx1',
'Rename .bashx to .bashx1.txt',
'Name collision: .cfg.txt>.cfg0>.cfg1',
'Rename .cfg to .cfg1.txt',
'Name collision: .emacx.txt>.emacx0>.emacx1',
'Rename .emacx to .emacx1.txt'])

# -------------------------------------------------------------------------
#       Regular Expressions Option for filter and replacement
# In Windows the filters and replacement here don't need to be quoted. In Linux
# they all need to be quoted because the filters contain ( and ) and the 
# replacements /. The shell interprets these even with globbing disabled.
# .............................................................................
def test64() :
    return engine(r'"08.+-0(.*)" "hap\1" -E -AS', all, patents, [
'Rename 08493357-001.tif to hap01.tif',
'Rename 08493357-002.tif to hap02.tif',
'Rename 08493357-003.tif to hap03.tif',
'Rename 08493357-004.tif to hap04.tif',
'Rename 08493357-005.tif to hap05.tif'])

def test65() :
    return engine(r'"(.{3}).*(.{2})-0(.*)" "\1\2\3" -E -AS', [], [], [
'Rename 08493357-001.tif to 0845701.tif',
'Rename 08493357-002.tif to 0845702.tif',
'Rename 08493357-003.tif to 0845703.tif',
'Rename 08493357-004.tif to 0845704.tif',
'Rename 08493357-005.tif to 0845705.tif'])

def test66() :
    return engine(r'"08(.*)33(.*)-(.*)\.tif" "\3\2\1.tif" -E -AS', [], [], [
'Rename 08493357-001.tif to 0015749.tif',
'Rename 08493357-002.tif to 0025749.tif',
'Rename 08493357-003.tif to 0035749.tif',
'Rename 08493357-004.tif to 0045749.tif',
'Rename 08493357-005.tif to 0055749.tif'])

# -------------------------------------------------------------------------------
#                   Sub Option 
# The Sub option doesn't use a filter other than the -F option which can provide
# pre-filtering. To protect all of the rene* files during testing -Frene* is
# included in the command line.

subFiles = ['My_Test_File','some_other_file']

def test67() :
    if engine(r'-SL/_- -AR -Frene*', all, subFiles, [
'Rename My_Test_File to my-test-file',
'Rename some_other_file to some-other-file']) == 0 and \
    checkDir(['my-test-file', 'some-other-file'], subFiles) == 0 and \
    engine(r'-U') == 0 and \
    checkDir(subFiles, []) == 0 :
        return 0
    else :
        return 1

def test68() :
# Test that duplicated character means to delete it. This depends on preceding test.
    return engine(r'-S/__/  -AS -Frene*', [], [], [
'Rename My_Test_File to MyTestFile',
'Rename some_other_file to someotherfile'])


# ------------------------------------------------------------------------------
#                         Recursion Option 
#
# makeTree creates the given root directory and self-similar branches to the 
# requested depth (e.g. 2 makes two levels under the root). In each interior 
# and leaf directory, the given list of files is created. When this returns, 
# root is the current directory. No function is provided for deleting the 
# tree. The os library doesn't provide one and it would be too dangerous 
# anyway. Use direct OS facilities to delete it. Note, however, invoking this 
# function repeatedly doesn't hurt anything. Directories and files are skipped 
# if the already exists. The only potential problem is left-overs from 
# renaming and not undoing.
def makeTree(root, branch, depth = 1, files = []) :
    curDepth = 0
    def makeBranches() :
        nonlocal curDepth
        createThese(files)
        if curDepth < depth :
            for fd in branch :
                if not os.path.exists(fd) :
                    os.mkdir(fd)
                os.chdir(fd)
                curDepth += 1
                makeBranches()
                curDepth -= 1
                os.chdir('..')
    if not os.path.exists(root) :
        os.mkdir(root)
    os.chdir(root)
    makeBranches()

# setupRec creates the three level (root plus levels) tree for recursion tests.
# This is invoked only by the first test for all to share. This is handled
# differently from other tests because there is no automated tree delete 
# capability. setupRec isn't actually needed because the first test could do
# this but having a separate function simplifies recreating the tree without
# involving the first test (e.g. as renet's nameless operation)
def setupRec() :
    makeTree('recurse', ['X_Old', 'X_New'], 2,  ['my_Dog.png', 'my_Cat.png']) 
    os.chdir('..')

def test69() : # Unlimited recursion.
    setupRec()
    os.chdir('recurse')
    ret = engine(r'-SL/_-/  -AS -R', [], [], [
'recurse',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_New',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_New>X_New',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_New>X_Old',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_Old',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_Old>X_New',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_Old>X_Old',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png'])
    os.chdir('..')
    return ret

def test70() : # Recursion with depth limit.
    os.chdir('recurse')
    ret = engine(r'-SL/_-/  -AS -R1', [], [], [
'recurse',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_New',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_Old',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png'])
    os.chdir('..')
    return ret
    
def test71() : # Recursion with excluded directory list.
    os.chdir('recurse')
    ret = engine(r'-SL/_-/  -AS -R/X_Old/', [], [], [
'recurse',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_New',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_New>X_New',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png'])
    os.chdir('..')
    return ret

def test72() : # Recursion with inclusive directory list.
    os.chdir('recurse')
    ret = engine(r'-SL/_-/  -AS -R+/X_Old/', [], [], [
'recurse',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_Old',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_Old>X_Old',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png'])
    os.chdir('..')
    return ret

def test73() : # Recursion with inclusive directory list and depth limit.
    os.chdir('recurse')
    ret = engine(r'-SL/_-/  -AS -R1/+/X_Old/', [], [], [
'recurse',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'recurse>X_Old',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png'])
    os.chdir('..')
    return ret

def test74() : # Recursion with actual rename (preceding only showed). The only
# auto-verification here is by comparing what rene says it is doing to what is 
# expected. Proper verification would be to recursively invoke checkDir but 
# that is difficult to generalize and not worth the trouble for one test. 
# Indirect verification is provided by the next test, which does recursive 
# undo. It also verifies only by what rene says it is doing but, unless rene is 
# deliberately lieing, the two tests provide complementary validation.
    os.chdir('recurse')
    ret = engine(r'my_* his-* -AR -R', [], [], [
'recurse',
'Rename my_Cat.png to his-Cat.png',
'Rename my_Dog.png to his-Dog.png',
'recurse>X_New',
'Rename my_Cat.png to his-Cat.png',
'Rename my_Dog.png to his-Dog.png',
'recurse>X_New>X_New',
'Rename my_Cat.png to his-Cat.png',
'Rename my_Dog.png to his-Dog.png',
'recurse>X_New>X_Old',
'Rename my_Cat.png to his-Cat.png',
'Rename my_Dog.png to his-Dog.png',
'recurse>X_Old',
'Rename my_Cat.png to his-Cat.png',
'Rename my_Dog.png to his-Dog.png',
'recurse>X_Old>X_New',
'Rename my_Cat.png to his-Cat.png',
'Rename my_Dog.png to his-Dog.png',
'recurse>X_Old>X_Old',
'Rename my_Cat.png to his-Cat.png',
'Rename my_Dog.png to his-Dog.png'])
    os.chdir('..')
    return ret

def test75() : # Undo the previous
    os.chdir('recurse')
    ret = engine(r'-UR', [], [], [
'recurse>X_Old>X_Old',
'rename his-Cat.png back to my_Cat.png',
'rename his-Dog.png back to my_Dog.png',
'recurse>X_Old>X_New',
'rename his-Cat.png back to my_Cat.png',
'rename his-Dog.png back to my_Dog.png',
'recurse>X_Old',
'rename his-Cat.png back to my_Cat.png',
'rename his-Dog.png back to my_Dog.png',
'recurse>X_New>X_Old',
'rename his-Cat.png back to my_Cat.png',
'rename his-Dog.png back to my_Dog.png',
'recurse>X_New>X_New',
'rename his-Cat.png back to my_Cat.png',
'rename his-Dog.png back to my_Dog.png',
'recurse>X_New',
'rename his-Cat.png back to my_Cat.png',
'rename his-Dog.png back to my_Dog.png',
'recurse',
'rename his-Cat.png back to my_Cat.png',
'rename his-Dog.png back to my_Dog.png'])
    os.chdir('..')
    return ret
    
# Recurse including rename of directories as well as files. This also excludes
# a directory. Note that the new name is required because breadth-first 
# recursion changes the directory name before recursing into it.
def test76() : 
    os.chdir('recurse')
    ret = engine(r'-SL/_-/  -Fd -AR -R/x-old/', [], [], [
'recurse',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'Rename X_New to x-new',
'Rename X_Old to x-old',
'recurse>x-new',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png',
'Rename X_New to x-new',
'Rename X_Old to x-old',
'recurse>x-new>x-new',
'Rename my_Cat.png to my-cat.png',
'Rename my_Dog.png to my-dog.png'])
    os.chdir('..')
    return ret

def test77() : # Recursive undo the previous, which includes directories.
    os.chdir('recurse')
    ret = engine(r'-UR', [], [], [
'recurse>x-new>x-new',
'rename my-cat.png back to my_Cat.png',
'rename my-dog.png back to my_Dog.png',
'recurse>x-new',
'rename my-cat.png back to my_Cat.png',
'rename my-dog.png back to my_Dog.png',
'rename x-new back to X_New',
'rename x-old back to X_Old',
'recurse',
'rename my-cat.png back to my_Cat.png',
'rename my-dog.png back to my_Dog.png',
'rename x-new back to X_New',
'rename x-old back to X_Old'])
    os.chdir('..')
    return ret

def test78() : # Default insert-increment with recursion.
    os.chdir('recurse')
    ret = engine(r'my* my*: I -R -AS', [], [], [
'recurse',
'Rename my_Cat.png to my_Cat0.png',
'Rename my_Dog.png to my_Dog1.png',
'recurse>X_New',
'Rename my_Cat.png to my_Cat2.png',
'Rename my_Dog.png to my_Dog3.png',
'recurse>X_New>X_New',
'Rename my_Cat.png to my_Cat4.png',
'Rename my_Dog.png to my_Dog5.png',
'recurse>X_New>X_Old',
'Rename my_Cat.png to my_Cat6.png',
'Rename my_Dog.png to my_Dog7.png',
'recurse>X_Old',
'Rename my_Cat.png to my_Cat8.png',
'Rename my_Dog.png to my_Dog9.png',
'recurse>X_Old>X_New',
'Rename my_Cat.png to my_Cat10.png',
'Rename my_Dog.png to my_Dog11.png',
'recurse>X_Old>X_Old',
'Rename my_Cat.png to my_Cat12.png',
'Rename my_Dog.png to my_Dog13.png'])
    os.chdir('..')
    return ret

def test79() : # Complex insert-increment with recursion. 
# The replacement has two inserter rules. One is alpha starting at A and 
# reloading for each directory and the other with start 5, step 10, width 2, 
# and not reloading.
    os.chdir('recurse')
    ret = engine(r'my* my*:: I/A///R I/5/10/2 -R -AS', [], [], [
'recurse',
'Rename my_Cat.png to my_CatA05.png',
'Rename my_Dog.png to my_DogB15.png',
'recurse>X_New',
'Rename my_Cat.png to my_CatA25.png',
'Rename my_Dog.png to my_DogB35.png',
'recurse>X_New>X_New',
'Rename my_Cat.png to my_CatA45.png',
'Rename my_Dog.png to my_DogB55.png',
'recurse>X_New>X_Old',
'Rename my_Cat.png to my_CatA65.png',
'Rename my_Dog.png to my_DogB75.png',
'recurse>X_Old',
'Rename my_Cat.png to my_CatA85.png',
'Rename my_Dog.png to my_DogB95.png',
'recurse>X_Old>X_New',
'Rename my_Cat.png to my_CatA105.png',
'Rename my_Dog.png to my_DogB115.png',
'recurse>X_Old>X_Old',
'Rename my_Cat.png to my_CatA125.png',
'Rename my_Dog.png to my_DogB135.png'])
    os.chdir('..')
    return ret

# -------------------------------------------------------------------------------
#                    Filter Extension Tests
campics = ['IMAG0457.JPG', 'IMAG0458.JPG', 'IMAG0459.JPG', 'IMAG0460.JPG', 
'IMAG0461.JPG', 'IMAG0462.JPG', 'IMAG0463.JPG', 'IMAG461.JPG', 'IMAG.JPG'] 
# Note that IMAG0461.JPG != IMAG461.JPG

def test80() :
# Filter variable ? default 1 character without filter extension.
    return engine(r'IM??.JPG tree**.jpg -AS', [], campics, [
'Rename IMAG.JPG to treeAG.jpg'])

def test81() :
# Filter variable ? with width 1 specified in filter extension.
    return engine(r'IM??.JPG/1/1 tree**.jpg -AS', [], campics, [
'Rename IMAG.JPG to treeAG.jpg'])

def test82() :
# Filter variable ? with width 2 specified in extension.
    return engine(r'IM?.JPG/2 tree*.jpg -AS', [], campics, [
'Rename IMAG.JPG to treeAG.jpg'])

def test83() :
# Filter variable ? with width 4 specified in extension. All of the 
# IMAG0XXX.JPG files pass but IMAG461.JPG and IMAG.JPG are rejected.
    return engine(r'IMAG?.JPG/4 tree*.jpg -AS', [], campics, [
'Rename IMAG0457.JPG to tree0457.jpg',
'Rename IMAG0458.JPG to tree0458.jpg',
'Rename IMAG0459.JPG to tree0459.jpg',
'Rename IMAG0460.JPG to tree0460.jpg',
'Rename IMAG0461.JPG to tree0461.jpg',
'Rename IMAG0462.JPG to tree0462.jpg',
'Rename IMAG0463.JPG to tree0463.jpg'])

def test84() :
# Same as previous except that the extension specifies (by 0) unlimited width.
# Now IMAG461.JPG and IMAG.JPG are accepted.
    return engine(r'IMAG?.JPG/0 tree*.jpg -AS', [], campics, [
'Rename IMAG.JPG to tree.jpg',
'Rename IMAG0457.JPG to tree0457.jpg',
'Rename IMAG0458.JPG to tree0458.jpg',
'Rename IMAG0459.JPG to tree0459.jpg',
'Rename IMAG0460.JPG to tree0460.jpg',
'Rename IMAG0461.JPG to tree0461.jpg',
'Rename IMAG0462.JPG to tree0462.jpg',
'Rename IMAG0463.JPG to tree0463.jpg',
'Rename IMAG461.JPG to tree461.jpg'])

def test85() :
# Semantic filter for alpha range. The range looks numeric but the comparison
# is lexical so even though IMAG461.JPG is numerically in the filter range, it
# is rejected because 4 > 0. 
    return engine(r'IMAG?.JPG/0459-0462 tree*.jpg -AS', [], campics, [
'Rename IMAG0459.JPG to tree0459.jpg',
'Rename IMAG0460.JPG to tree0460.jpg',
'Rename IMAG0461.JPG to tree0461.jpg',
'Rename IMAG0462.JPG to tree0462.jpg'])

def test86() :
# Same as previous except the leading 0 is deleted from the range spec. Now
# IMAG461.JPG is the only one to pass the filter.
    return engine(r'IMAG?.JPG/459-462 tree*.jpg -AS', [], campics, [
'Rename IMAG461.JPG to tree461.jpg'])

def test87() :
# Changing to numeric range allows all of the names within the numeric range
# to pass the filter. Whether the leading 0 is absent or present is carried
# over into the replacement by the replacement variable *.
    return engine(r'IMAG?.JPG/#459-462 tree*.jpg -AS', [], campics, [
'Rename IMAG0459.JPG to tree0459.jpg',
'Rename IMAG0460.JPG to tree0460.jpg',
'Rename IMAG0461.JPG to tree0461.jpg',
'Rename IMAG0462.JPG to tree0462.jpg',
'Rename IMAG461.JPG to tree461.jpg'])

def test88() :
# The same semantic filter as in the previous but the replacement uses slice
# to try to normalize the new names but that causes a collision on the 461
# name. The default CA would be to append 0 but that is confusing because it
# makes the name 4610. Option -X+ tells to use + instead.
    return engine(r'IMAG?.JPG/#459-462 tree?.jpg S/0/3 -AS -X+', [], campics, [
'Rename IMAG0459.JPG to tree459.jpg',
'Rename IMAG0460.JPG to tree460.jpg',
'Rename IMAG0461.JPG to tree461.jpg',
'Rename IMAG0462.JPG to tree462.jpg',
'Rename IMAG461.JPG to tree461+.jpg'])

def test89() : 
# Unlimited width numeric range filter. The actual content is discarded and 
# replaced by a value synthesized by insert-increment replacement rule.
    return engine(r'IMAG?.JPG/#459-462 tree/:.jpg I -AS', [], campics, [
'Rename IMAG0459.JPG to tree0.jpg',
'Rename IMAG0460.JPG to tree1.jpg',
'Rename IMAG0461.JPG to tree2.jpg',
'Rename IMAG0462.JPG to tree3.jpg',
'Rename IMAG461.JPG to tree4.jpg'])

def test90() :
# Same as previous but the original field content is incorporated into the new
# name but with a negative bump equal to the lowest numeric value to pass the
# filter. The filter extension specifies numeric range for semantic filtering
# but the floater is still a character string. However, the Bump rule 
# interprets numeric text as intrinsic numeric. Consequently, IMAG461 is bumped
# just as the others are. But Bump retains the original width of numeric 
# fields, inherently avoiding collision.
    return engine(r'IMAG?.JPG/#459-462 tree?.jpg B/-459 -AS', [], campics, [
'Rename IMAG0459.JPG to tree0000.jpg',
'Rename IMAG0460.JPG to tree0001.jpg',
'Rename IMAG0461.JPG to tree0002.jpg',
'Rename IMAG0462.JPG to tree0003.jpg',
'Rename IMAG461.JPG to tree002.jpg'])

def test91() :
# Two floaters, each with filter extension, and both used in the new name. The 
# first one uses the extension only to specify 2 characters which can be built
# into the lexical filter. The second specifies numeric range, which is 
# semantic and must be processed after the RE filter.
    return engine(r'I?G?.JPG/2/#458-462 *tree*.jpg  -AS', [], campics, [
'Rename IMAG0458.JPG to MAtree0458.jpg',
'Rename IMAG0459.JPG to MAtree0459.jpg',
'Rename IMAG0460.JPG to MAtree0460.jpg',
'Rename IMAG0461.JPG to MAtree0461.jpg',
'Rename IMAG0462.JPG to MAtree0462.jpg',
'Rename IMAG461.JPG to MAtree461.jpg'])


alphaRange = ['myABC', 'myDEF', 'myGHI', 'myJKL', 'myMNO', 'myPQR', 'myJKLM' ]

def test92() :
# Alphabetic range semantic filter with specified width.
    return engine(r'my?/3,DEF-MNO his* -AS', all, alphaRange, [
'Rename myDEF to hisDEF',
'Rename myGHI to hisGHI',
'Rename myJKL to hisJKL',
'Rename myMNO to hisMNO'])

def test93() :
# Alphabetic range semantic filter with unlimited width.
    return engine(r'my?/DEF-MNO his* -AS', [], alphaRange, [
'Rename myDEF to hisDEF',
'Rename myGHI to hisGHI',
'Rename myJKL to hisJKL',
'Rename myJKLM to hisJKLM',
'Rename myMNO to hisMNO'])

def test94() :
# Alphabetic range with Bump (default +1) in replacement.
    return engine(r'my?/DEF-MNO his? B -AS', [], alphaRange, [
'Rename myDEF to hisDEG',
'Rename myGHI to hisGHJ',
'Rename myJKL to hisJKM',
'Rename myJKLM to hisJKLN',
'Rename myMNO to hisMNP'])

def test95() :
# Alphabetic range with Bump -2 in replacement.
    return engine(r'my?/DEF-MNO his? B/-2 -AS', [], alphaRange, [
'Rename myDEF to hisDED',
'Rename myGHI to hisGHG',
'Rename myJKL to hisJKJ',
'Rename myJKLM to hisJKLK',
'Rename myMNO to hisMNM'])

def test96() :
# Alphabetic range with Bump -10 in replacement. This is really a test of 
# negative alphabetic bump with borrow. It is incidental to range filter.
# Some of these have borrow and some do not. e.g. DEF - 10 = DEZV, an instance
# of borrow. JKL - 10 = JKB, an instance where borrow is not needed.
    return engine(r'my?/DEF-MNO his? B/-10 -AS', [], alphaRange, [
'Rename myDEF to hisDEZV',
'Rename myGHI to hisGHZY',
'Rename myJKL to hisJKB',
'Rename myJKLM to hisJKLC',
'Rename myMNO to hisMNE'])

# =============================================================================
# The rest of the tests have been added after initial release and are in no
# particular order.

def test97() : # Tests successive identical anchors bug fix in v1.0.1. Note 
# that the first three files trigger collision avoidance. A more practical
# solution would be to bump 50 and invoke twice, completely avoiding
# name collision.
    return engine(r'*_*_*_*  *_*_?_*  B/100 -AS', [], [
'Cyprinus_carpio_600_nanopore_trim_reads.fasta',
'Cyprinus_carpio_700_nanopore_trim_reads.fasta',
'Cyprinus_carpio_800_nanopore_trim_reads.fasta',
'Cyprinus_carpio_900_nanopore_trim_reads.fasta',
'Vibrio_cholerae_3900_nanopore_trim_reads.fasta'], [
'Rename Cyprinus_carpio_600_nanopore_trim_reads.fasta to Cyprinus_carpio_700_nanopore_trim_reads0.fasta',
'Rename Cyprinus_carpio_700_nanopore_trim_reads.fasta to Cyprinus_carpio_800_nanopore_trim_reads0.fasta',
'Rename Cyprinus_carpio_800_nanopore_trim_reads.fasta to Cyprinus_carpio_900_nanopore_trim_reads0.fasta',
'Rename Cyprinus_carpio_900_nanopore_trim_reads.fasta to Cyprinus_carpio_1000_nanopore_trim_reads.fasta',
'Rename Vibrio_cholerae_3900_nanopore_trim_reads.fasta to Vibrio_cholerae_4000_nanopore_trim_reads.fasta'])

# ----------------------------------------------------------------------------
# Tests for revised filter extension syntax in version v1.0.2. The syntax had 
# been /width,filter with both parts required because both could be ranging 
# with - delimiter and there was no general means of disambiguation. The new 
# canonical syntax is m,n,filter in which m and n define a width range. This 
# enables simplification by disambiguating all cases. A filter definition can't
# be just a number but a width must be. A single non-number is a filter with 
# default 0 (any) width. Also new is // placeholder alias of /1/

# Test all variations of filter extension width, // as placeholder, /m as 
# single required number, and /m,n as range. The accepted pattern 
# is xAxxBx|xx|xxx
def test98() :
    return engine(r'?A?B?//2/1,3 *C*D* -AS', [], [
'1A2B', # Rejected: A2 fails Axx width and B fails Bx width
'1A2Bx', # Rejected: A2 fails Axx width
'1A22Bx',  
'2A3Bxy', # Rejected: A3 fails Axx width
'2A33Bxy', 
'3A5Bxyz', # Rejected: A5 fails Axx width 
'3A55Bxyz', 
'3A555B66', # Rejected: A555 fails Axx width
'4A77Bxyzz'], # Rejected: xyzz > 3 
[ 'Rename 1A22Bx to 1C22Dx',
'Rename 2A33Bxy to 2C33Dxy',
'Rename 3A55Bxyz to 3C55Dxyz'])


# This tests the filter extension shortcut syntax, in which a single filter
# argument is accepted and assigned a default width of 0 (unlimited). This
# coincidentally illustrates one way to avoid name collision.
numNames = ['01.png', '02.png', '03.png', '03.svg', '04.png', '05.png', 
'06.jpg', '07.png', '08.png', '09.png', '09.svg', '10.png']
def test99() :
    engine(r'?.*/#7-80  %?.* B -AR', all, numNames, [])
    engine(r'%* * -AR', [], [], [])
    return checkDir(numNames[0:7] + ['08.png', '09.png', '10.png', '10.svg','11.png'], ['07.png'])

# Filter extension with ranging width and ranging lexical filter.
def test100() :
    return engine(r'hi?X*/2,3,B-D  bye*Y* -AS', [], [
'hiBX.png', # Rejected: one character < 2
'hiABX.png', # Rejected: A < B
'hiBBX.png','hiCDX', 'hiCXX', # Accepted
'hiDAX', # Rejected: D + anything > D (hiDX would be rejected for width)
'hiCABX', # Accepted
'hiCABBX'], # Rejected: four characters > 3
[ 'Rename hiBBX.png to byeBBY.png',
'Rename hiCABX to byeCABY',
'Rename hiCDX to byeCDY',
'Rename hiCXX to byeCXY'])

# Sub option U (upper case) added in v1.0.2 (see test67)
def test101() :
    return engine(r'-SU -F/rene*/*.lnk/yes/no/testrec -AS', all, subFiles, [
'Rename My_Test_File to MY_TEST_FILE',
'Rename some_other_file to SOME_OTHER_FILE'])


endFunc = 102 # For ALL limit last test name + 1

# ------------------------------------------------------------------------------------
testerr = []

def dotests(beg, end) :
    #if end > endFunc : end = endFunc
    for tnum in range(beg, end) :
        tname = 'test' + str(tnum)
        print('\n', tname, ': ', sep = "", end = "")
        try :
            if eval(tname + '()') != 0 :
                testerr.append(tname)
        except NameError :
            print('undefined')

# ======================= BEGIN HERE =========================================

pathrene = sys.argv[0].replace('renet.py', 'rene.py')
argc = len(sys.argv)

if argc == 1 : # Unnamed current single test or functions
# This can be convient to repeatedly invoke a single test but is more useful
# setting up conditions without actually invoking the test. Then rene can be
# invoked directly, which is better for debugging it.
    #createThese(caNames)
    delThese(all)
    #createThese(numNames)
    exit(0)

if argc > 2 :
    options = sys.argv[2].upper()
    if 'Q' in options :
        Quiet = True
    if 'V' in options :
        Verbose = True
    if 'R' in options :
        Record = True
if sys.argv[1][0].isdigit() :
    for tnum in sys.argv[1].split(',') :
        trange = tnum.split('-')
        tbegin = int(trange[0])
        tend = int(trange[1]) + 1 if len(trange) > 1 else tbegin + 1
        dotests(tbegin, tend)
elif sys.argv[1].upper() == "ALL" :
    dotests(1, endFunc)

if len(testerr) == 0 :
    print('\nAll results are as expected')
else :
    print('\nUnexpected results from', testerr)
