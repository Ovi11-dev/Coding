#!/usr/bin/env python3
# This shebang is only for Linux. Without it many distros default to Python 2, 
# which cannot execute this script. Also for Linux, this file uses Unix line 
# endings. This is only for the shebang line. Python doesn't care.

# rene.py
# Updated: 2019.02.27
# Extended file rename utility for Windows and Linux.
# Author David McCracken
# Released under GNU General Public License v3.0

# See help for a brief usage description. See rene.doc for a more complete
# description of use and program design. See the automated test program
# renet.py for more examples.
#
#                          GENERAL OUTLINE
#   Rene has four modes of renaming, native, regular expression (option -E) 
# substitution (option -S) and Undo (option -U). For native mode, the command 
# line is rene.py filter replacement rules options, with rules and options 
# being optional. For RE mode, it is rene.py filter replacement options, with 
# options being optional. For Sub and Undo, it is rene.py options. Undo 
# supports only one option, -U. Sub requires -S option and also supports 
# option -F, which provides file exclusion. Native and RE modes require filter 
# and replacement.
#   The command line is completely processed before looking at any files. 
# Syntactic and semantic errors are detected and either corrected or the 
# program exits. Incomplete rule and option parameters are initiallized to 
# default values. No command error checking is needed during the renaming 
# process.
#   Undo is simple. It reads the reneAct file, which records all renaming in 
# the last invocation and reverses the changes. This is done entirely in the 
# command parsing loop and then the program exits.
#   Except for Undo, renaming iterates over files in the current directory. 
# Recursion is not supported. Files and directories that don't meet filter 
# specs are skipped. An initial filter controlled by -F option applies to all 
# modes. Files that pass this are then processed according to one of the three 
# modes, Sub, native, and RE. The modes cannot be combined. They individually 
# apply their own filter while simultaneously computing a new name. After this 
# the modes converge onto a comman path where the new name is validated. 
# Nothing further is done if the name has not changed. If the new name is the 
# same as an existing one or one about to be created by renaming, collision 
# avoidance is engaged to systematically modify it until a collision-free name 
# is determined.
#   By default, all changes are display and the user asked whether to perform
# them. The -A (Act) option can change this to make the changes without asking
# or to only display the proposed changes.
#
#                            RULES AND OPTIONS
#   Rules and options have the same basic syntax except that options have - 
# prefix while rules all begin with a letter. For both, the first letter 
# identifies the type. Most have default values and may legally comprise only 
# that single letter. Parameters are alpha and numeric (decimal, hexadecimal, 
# or binary) strings divided into fields (where applicable) by /. Rules are 
# used only for native mode and only if the replacment contains rule 
# variables (? and :). The variables and rules are sequentially sychronized. 
# Most options apply to any mode. However, -U is its own complete mode. -O 
# applies only to native mode. Options and rules may appear anywhere in the 
# command line but, because of the synchronization between replacement and 
# rules, it is best for rules to appear immediately after replacement. 
# replacement must follow filter.
#   Regardless of where they appear in the command line, options are all 
# processed first because they can affect the preparation of the filter and 
# replacement. -E tells that they are standard regular expressions and not 
# native. -FC tells to make the filter case-insensitive. This information is 
# needed when the filter argument is compiled.
#
#                           INSERT-INCREMENT RULE
# Most rules are self-contained and statically defined in the repRules 
# dictionary after any changes to defaults by command arguments. The I rule is
# different. Its contribution to file names changes with each name that it is 
# applied to. For a single directory or normal recursion this can be simply 
# done by stepping the start value in the rule's descriptor. However, 
# sometimes we don't want continuous stepping but to reload the start value 
# for each directory. This requires the start value to stored in a hidden 
# reload value, which is copied back into the start value at each directory 
# transition. It would be simpler to use one global value for this but a 
# replacement might use more than one I rule and they would not be the same. 
# One might be continuous and the other reloaded and it is unlikely that they 
# would have the same start value. Also because of the possibility of multiple 
# I rules, the I rule processor itself can't reset a "new directory" flag set 
# by procTree. The only feasible solution is to have procTree find any I rules 
# in the rules list and reload the start value if requested in the command 
# argument (I////R). To make this a little more efficient, when the command 
# line is processed the indices of any I rules are added to the irules list. 
# If this is empty, procTree doesn't have to do anything, but it does reload 
# any that are listed and require reload. 
#
#                            DIRECTORY SORT
#   Windows directories are inherently case-insensitively sorted. Linux 
# directory contents are in random order. The results are identical unless the 
# native mode Insert-Increment rule is applied, as that increments the 
# insertion for each successive file. For consistent results in Linux, 
# directories are automatically sorted in this situation. A simple sort is 
# used. This does not exactly match Windows order because it is case-sensitive
# but it is adequate and  much less expensive than a case-insensitive sort.
#   That rene will normally process files in different order under Linux vs. 
# Windows is immaterial except under regression testing that verifies outcome 
# based on rene's output. For identical output, in Linux the directories must 
# be case-insensitively sorted. This is enabled by the test option -TS. -TS 
# overrides the simple sort used normally with Insert-Increment and may be 
# added to the commmand to force completely consistent results even when not 
# testing. See sortdir and getdir().
#
#                          COLLISION AVOIDANCE
#    If renaming (in any mode except Undo) a file produces a new name the same 
# as an existing file that is not the same one as being renamed (mainly a 
# Windows issue when only changing case) then collision avoidance (CA) is 
# engaged. 
#    CA modifies the new name in a specified way and checks this for 
# collision, repeating until there is no collision. The default scheme is to 
# append a number, starting at 0, to the root name, incrementing it as needed 
# to find a free name.
#    The command option -Xscheme specifies alternatives. scheme is a string, 
# without spaces, in which various characters independently control various 
# aspects of collision avoidance. S and C turn it off, with S saying to stop 
# immediately and C to contine, skipping the file. M tells to not append a 
# name fragment but to merge with the root by incrementing the numeric or 
# alphabetic tail of the root. Any other letter tells to use that as the 
# starting point (appended to the root). A number tells to use that as the 
# appended starting point. A string of punctuatiohs is added to the root, 
# identifying the name as not being exactly as requested, in addition to 
# participating in the avoidance process itself.
#
#                           FUNCTIONS
#- reRange converts a range string of the form m-n to the regular expression {m,n}.
#- scanint converts decimal, hexadecimal, and binary strings to int.
#- parmList converts /-delimited parameter string to list.
#- bitmapChars converts a parameter string to intrinsic bitmap.
#- greedyext divides a file name into root and all extensions. 
#- badChr examines a string for illegal characters.
#- nextName is the file name incrementer.
#- prepRule converts a command line rule argument string to a woking list.
#- avoid implements collision avoidance.
#- native is the native filter-replacment-rules processor.
#- getdir gets a list of the directory, possibly sorted (only in Linux).
#- procDir renames the files (and directories) in the current directory.
#- agnosticDir converts OS-specific absolute path to OS-agnostic relative.
#- procTree calls procDir and itself in recursive mode (-R option)
#- undo reverses the previous renaming in one directory.
#- recUndo reverses the previous recursive renaming.
# -----------------------------------------------------------------------
import sys,os,re,stat,fnmatch
Windows = os.name == 'nt'
if Windows :
    from msvcrt import getche, kbhit, getch
else :
    import tty, termios
    def lingetch(echo) :
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if echo :
            print(ch)
        return ch

# useInput is enabled by test option -TI. It tells to use the input function
# instead of single keypress for Y/N, which doesn't support input redirect.
useInput = False

sortdir = 0 # 0 = don't sort. 1 = simple sort. 2 = case-insensitive sort.

renePat = re.compile(r'rene(.py|t.py|Act)') # To block attempts to rename 
# our own files.

newList = [] # List of new names about to be created (if -AR or ask and user
# oks). This is global because procDir fills it (and uses it) and avoid reads
# it to avoid collision not only with existing files but also preceding 
# renamed ones.

fOpt = [] # -F option.
filterCase = re.IGNORECASE # -FC option. Makes the filter case-sensitive. 
# Default filter is case-insensitive. 
opdirs = 0 # -FD/d directories option. 0 (default) don't operate on directories. 
# 1 = include directories. 2 = operate only on directories, skipping files.

A_ASK = 0 ; A_REN = 1 ; A_SHOW = 2
aOpt = A_ASK # -A action option

P_NONE = 0 ; P_REN = 1 ; P_CA = 2 ; P_SKIP = 4 ; P_UNCHANGED = 8
pOpt = P_REN # -S pOpt option

# -X option controls collision avoidance (CA) alternatives.
caStop = False # Stop on file collision
caContinue = False # Skip file on collision
caPun = ""
caPunPos = 1 # 0 = root prefix, 1 = root suffix, 2 = CA suffix
caMerge = False
caStart = '0' # Default collision avoidance is by number starting at 0.

# -R option recurse
rDepth = 0
rInc = False 
rDirs = [] # Exclude these directories if rInc is false, else do only these.
rVisit = []
curDepth = 0
chopDir = len(os.path.dirname(os.getcwd())) + 1 # For recurse dir display.

eOpt = False # -E option. filter and repl args are regular expressions.
sOpt = [] # -S option.

#                     NATIVE MODE OPTIONS AND RULES
oOpt = [] # -O option. Alternative floater order.
# Filter extension rule IDs
FX_NRANGE = 1 # numeric range rule
FX_ARANGE = 2 # alpha range rule

# rv* are replacement argument variables. All but rvAdd consume floaters from 
# the original file. rvAdd insertes a completely synthetic name fragment. 
# rvCopy inserts the entire floater. rvSkip discards the floater. rvRule 
# transforms the floater. rvAdd and rvRule share the rules structure but no 
# specific rules.
rvAdd = r':'
rvRule = r'?'
rvSkip = r'/'
rvCopy = r'*'
rvars = rvAdd + rvRule + rvSkip + rvCopy
consumers = rvRule + rvSkip + rvCopy

rules = []
irules = [] # Indices of I rules (probably only one) for recursion reload.
bumpRule = 'B'
sliceRule = 'S'
incRule = 'I'
I_START = 1 ; I_STEP = 2 ; I_WIDTH = 3 ; I_MODE = 4 ; I_RELOAD = 5
I_E = 1 ; I_R = 2 # I rule mode bitmap

# repRules is a dictionary of rule descriptors. It is indexed by the letter 
# that identifies each rule argument. The value is a list that essentially 
# defines the default working list for each type of rule. The first item in 
# the actual working list is the rule ID. That is the index for the 
# dictionary. In the dictionary, that is replaced by the type of replacement 
# argument, rvRule or rvAdd, for which this particular rule is valid. This is 
# used when a rule argument is parsed to verify that it is being used properly.

repRules = {
     sliceRule:[rvRule, 2, 2, 0], # S Slice floater rule leading/trailing/mode. 
# This default specifies that the first two and last two characters of the 
# source will be used.

    bumpRule:[rvRule, 1, 0], # B Bump floater rule value/mode. 
# This default specifies incrementing (by 1) either numeric or alphabetic, 
# depending on source floater.

   incRule:[rvAdd, 0, 1, 1, 0, 0] # I Insert-Increment rule 
# start/step/width/mode/rstart. This default specifies a numeric field. If the 
# start value is a letter then an alphabetic field is inserted and step and 
# width are ignored. rstart is a hidden duplicate of start for recursion with 
# restart in each directory. mode "" means not E or R.
    }

# -------------------------------------------------------------------------
# reRange converts a range string of the form m-n to the regular expression {m,n}.
def reRange(str) :
    r = str.split('-')
    return '{' + r[0] + ',' + r[-1] + '}'

# -------------------------------------------------------------------------
# scanint converts decimal, hexadecimal (0x), or binary (0..) to intrinsic int.
# It correctly handles negative (leading -) for all radices.
def scanint(str) :
    if str == "" : return 0
    v = str if str[0] != '-' else str[1:]
    if v[0] != '0' :
        v = int(v)
    elif len(v) > 1 and v[1].upper() == 'X' :
        v = int(v, 16)
    else :
        v = int(v, 2)
    return v if str[0] != '-' else -v

# --------------------------------------------------------------------------
# parmList scans a command parameter string delimited by / (mainly rules)
# to produce a list of parameters. Each parameter is a non-empty string.
def parmList(parm, emptyok = False) :
    return [p for p in parm.split('/') if emptyok or p != ""]

# -------------------------------------------------------------------------
# bitmapChars transforms the given string into an intrinsic bitmap based on 
# the occurance of characters from the given pattern in the string. The 
# mapping is determined by the pattern. e.g. 'ER' maps E to b0 and R to b1. 
# These bits are set (in the return value) based on whether the string 
# contains E and R in any order. The purpose of this is to transform mnemonic 
# command parameters into more efficient bitmaps.
# ........................................................................
def bitmapChars(str, pat) :
    bm = 0
    for idx, chr in enumerate(pat) :
        if str.find(chr) >= 0 :
            bm |= 1 << idx
    return bm

# --------------------------------------------------------------------------
# greedyext divides the given file name into root and extension. This is 
# similar to os.path.splitext but includes intermediate extensions as part of 
# extension. e.g. name.tar.gzip is ['name', '.tar.gzip']. The purpose of this 
# is to get to the real root name for rename. We rarely want to change any 
# extension name, including intermediate ones.
# ..........................................................................
extpat = re.compile(r'(\.*[^.]+)(\..+)*')
def greedyext(str) :
    pm = re.match(extpat, str)
    if not pm : return ["", ""]
    rootx = list(pm.groups())
    if rootx[1] is None : rootx[1] = ""
    return rootx

# ---------------------------------------------------------------------------
# badChr inspects a given test string for any characters in a given string of 
# bad characters. On the first match, i.e. bad character, it prints a detailed 
# error message and raises ValueError exception.
# ..........................................................................
def badChr(chrs, s) :
    bad = re.search(chrs, s)
    if bad:
        idx = bad.span()[0]
        print('Illegal', s[idx], 'in', s, 'at', idx)
        raise ValueError

# -----------------------------------------------------------------------
# nextName computes the next name created by incrementing or decrementing by a 
# specified amount. 
#   The last character in str determines how it is handled. If it is a digit 
# then it and all preceding digits are converted to an intrinsic integer, step 
# argument added, and the result written back out as a string. Thus, the 
# entire field may be modified. 
#   If the last character is alphabetical, it is treated in a unique (to this 
# program) manner. Step is added to the ordinal of the last character and the 
# result is written back as a character. Case-sensitive alphabetic carry or
# borrow does not propagate leftward beyond the last original character but
# appends a new character. Z + 1 = AA, z + 1 = aa, A-1 = ZZ, a - 1 = zz.
#   The offset argument can be used to reduce numeric greediness. If it is 0 
# (and the last character of str is a digit) then all contiguous digits to the 
# left of the end are taken. When nextName is used to increment an appended 
# number a preexisting number can be preserved by passing offset equal to the 
# original string length. 
# .........................................................................
def nextName(str, step = 1, offset = 0) :
    if str[-1].isdigit() :
        ng = re.search(r'(.*?)([0-9]+$)',str[offset:])
        if ng :
            sn = ng.groups()[1]
            v = int(sn) + step
            return str[0:offset] + ng.groups()[0] + '%0*d' % (len(sn), v)
    elif str[-1].isalpha() :
        if str[-1].islower() :
            firstChr = 'a'
            lastChr = 'z'
        else :
            firstChr = 'A'
            lastChr = 'Z'
        end = ord(lastChr)
        nextord = ord(str[-1]) + step % 26
        if step < 0 : # e.g. B - 1 = A, A - 1 = ZZ
            return str[0:-1] + (
            chr(nextord - 26) if nextord > end else lastChr + chr(nextord))
        else : # e.g. Y + 1 = Z, Z + 1 = AA
            return str[0:-1] + (
            firstChr + chr(nextord - 26) if nextord > end else chr(nextord))

    else : # Punctuation
        return str + '%d' % step # Append step to increment.

# ----------------------------------------------------------------------------
# prepRule converts a command line rule argument string to a woking list.
# Returns the new working list.
#- arg is the command line rule argument string.
#- defRule is a properly initialized list of the same type as the rule. It
# provides default type/values for all unspecified parameters in arg.
#
#                             Operation
# The first character of arg identifies the type of rule. Parameters are 
# separated by /. i.e. R/p1/p2... Parameters may be decimal number, which is 
# converted to int in the working list, or string, which is copied to the 
# working list. All parameters are optional. Any that are missing are copied 
# from the default rule. Empty parameters are used as place holders to allow a 
# later parameter to be specified while accepting defaults for earlier ones. 
# e.g. N///10. The resulting empty strings are replaced by the corresponding 
# item (of any type) from the default rule.
# ...........................................................................
def prepRule(arg, defRule, rvType) :
    wlist = arg.split('/')
    if len(wlist[0]) > 1 :
        print('Bad syntax in rule', arg, 'Did you forget the first /?')
        raise ValueError
    if defRule[0] != rvType :
        print(arg, 'rule is not supported by', rvType, 'replacement variable')
        raise ValueError
    for i in range(1, len(defRule)) :
        if i > len(wlist) - 1 : # Missing optional parameter, e.g. B<nothing>
            wlist.append(defRule[i]) 
        elif wlist[i] == "" : # Blank placeholder, e.g. B//0x44
            wlist[i] = defRule[i]
        else :
            v = wlist[i]
            if v[0].isdigit() or v[0] == '-' and v[1].isdigit() :
                wlist[i] = (scanint(v))

# For I rule (insert-increment) additional pre-processing is needed. The start 
# parameter itself is the working incrementer. If recursive (option -R) with I 
# rule mode R the value restarts for each directory. A hidden copy of the 
# original start value provides the reload value. Additionally, the mode 
# parameter, which is a string containing E and/or R for command convenience, 
# is converted to bitmap for processing efficiency.
    if arg[0] == 'I' and wlist[I_MODE] != 0 : 
        wlist[I_MODE] = bitmapChars(wlist[I_MODE], 'ER')
        wlist[I_RELOAD] = wlist[I_START] 

    return wlist

# ---------------------------------------------------------------------------
# avoid implements collision avoidance when the proposed new name for a file 
# is the same as an existing file or name in newList (of files about to be 
# renamed). It does this by modifying the file name in specific ways until 
# finding a name that is not that of any existing file or one about to be 
# created by the program itself. See -X option for a description of the 
# default and alternate schemes implemented here.
# ...........................................................................
def avoid(name) :
    rootExt = greedyext(name)
    caNames = 'Name collision: ' + name
# If caPun exists it participates in collision avoidance. It can be in one of 
# three positions, identified by caPunPos. 0 is root prefix. 1 (default) is 
# root suffix, which is also CA prefix. 2 is CA prefix, i.e. at the end of the
# complete new root, including CA characters (if needed). Positions 0 and 1 
# require simply adding the string to the root and then engaging the iterative
# process. Position 2 is more involved. The string is appended to check for 
# collision but must be removed at each CA reiteration to avoid interferring 
# with the new name function. It would be easier to simply leave the string 
# off until finding a free name but adding the string to a free root name can 
# create a name that collides with an existing name made by previous collision 
# avoidance.caPunPos 1 is incompatible with merge but we don't have to deal 
# with that here because it will have been changed to 2 by the command line 
# processor.
    caPunLen = 0 
    if caPun != "" :
        if caPunPos == 0 :
            rootExt[0] = caPun + rootExt[0]
        elif caPunPos == 1 :
            rootExt[0] += caPun
        elif caPunPos == 2 :
            caPunLen = len(caPun) # Used only to peel off the CA str.
# An infinite (essentially) loop is used with an internal limiter in order to 
# test the name (possibly) with CA string before making any other name changes
# while still testing every synthesized name. To avoid repeating code, the 
# loop has to terminate in the middle of the block.
    for i in range(100) : 
        if caPunLen != 0 :
            rootExt[0] += caPun
        tname = rootExt[0] + rootExt[1]
        if not tname in newList and not os.path.exists(tname) :
            break;
        if i > 9 :
            print(caNames)
            return ""
        if caPunLen != 0 :
            rootExt[0] = rootExt[0][:-caPunLen]
        if caMerge :
            rootExt[0] = nextName(rootExt[0])
        else :
# With non-merging incrementing number collision avoidance, the number is
# appended to the root. If this reiterates and the root ends in digits
# nextName would force a merge. To avoid this, the original root length is
# passed as offset argument to nextName.
            if i == 0 :
                rootLen = len(rootExt[0])
                rootExt[0] += caStart
            else :
                rootExt[0] = nextName(rootExt[0], 1, rootLen)
        caNames += '>' + rootExt[0] + (caPun if caPunLen != 0 else "")

    if(pOpt & P_CA ) :
        print(caNames)
    return rootExt[0] + rootExt[1]

# ---------------------------------------------------------------------------
# native is rene's native filter-replacment-rules processor. This is the 
# default unless -S or -E option. Those two are much simpler and embedded in 
# procDir.
# old is the name of the file to test/rename.
# Returns "" if old doesn't meet the filter criteria. Otherwise the new name 
# based on replacement and rules.
# ................................... notes ..................................
#   If the old name (current file name) passes the RE pattern filter, then if
# there are semantic filter rules (filArgx is not empty) apply them against the
# corresponding match groups (floaters). If the name passes these filters then
# continue processing it.
#  The match groups are converted to floaters list in either normal order or 
# order as defined by -O option. The list is empty if the filter contains no 
# floaters (* and ?). This might be due to a specific file is being given a 
# completely new literal name, which is a poor use of rene, but it could also 
# be that the file is being given a synthesized (via rvAdd) name.
# ...........................................................................
def native(old) :
    filterMatch = filter.match(old)
    if filterMatch == None or noDotName and old[0] == '.' :
        return ""
    for rule in filArgx :
        v = filterMatch.group(rule[0])
# If the floater includes both root and extension, apply the semantic filter
# to the root. 
        rext = v.split('.')
        if len(rext) > 1 :
            v = rext[0]
        if rule[1][0] == FX_ARANGE :
            if v < rule[1][1] or v > rule[1][2] :
                return ""
        elif rule[1][0] == FX_NRANGE :
            try :
                v = int(v)
            except ValueError :
                return ""
            if v < rule[1][1] or v > rule[1][2] :
                return ""
            
    if len(oOpt) == 0 :
        floaters = filterMatch.groups() 
    else :
        floaters = [filterMatch.groups()[idx] for idx in oOpt]
    
# Scan over the replacement list, adding literals to the new name, and 
# processing variables, all of which except rvAdd consume one floater. If 
# there aren't enough floaters, these variables contribute nothing to the new 
# name. If there are more floaters than consumers all of the remaining ones 
# are concatenated and given to the last consumer.
    newName = ""
    floatIdx = 0 # floaters index
    ridx = 0 # rules index in case nRules > 0
    for idx,rep in enumerate(lrep) :
        if rep not in rvars :
            newName += rep # Literal replacement
            continue
        # Variable replacement
        if rep in consumers :
# If there are no more floaters then skip this consumer. If this is the last 
# consumer but there are more floaters then concatenate the remaining floaters 
# and treat them as one.
            if floatIdx > maxFloat :
                continue # There are no floaters left to consume.
            if idx == maxConsumer and floatIdx < maxFloat :
                src = "".join(v for v in floaters[floatIdx:])
            else :
                src = floaters[floatIdx]
            floatIdx += 1
            if rep == rvCopy :
                newName += src
                continue
            if rep == rvSkip or src == "" :
                continue
# End of rep in consumers. We are now done with rvCopy and rvSkip but not with 
# rvRule. We have taken care of its floater scaffold but still must process 
# the rule. rvRule and rvAdd share the rules list although they don't share 
# any specific rules. They also differ in that rvRule consumes a floater and 
# rvAdd does not but that difference is already accounted for in the preceding 
# block.
        if rules[ridx][0] == sliceRule :
            if rules[ridx][3] == 0 : # begin-end slice
                if len(src) < rules[ridx][1] + rules[ridx][2] :
                    print('Warning:', src, 'is smaller than the slice')
                newName += src[:rules[ridx][1]] + src[-rules[ridx][2]:]
            else : # Pythonic slice
                if rules[ridx][1] >= rules[ridx][2] or rules[ridx][2] > len(src) :
                    print('Warning:', src, 'cannot satisfy the slice')
                newName += src[rules[ridx][1]:rules[ridx][2]]

        elif rules[ridx][0] == bumpRule :
# Assume src contains an extension, in which case the root is modified without 
# touching the extension. If src doesn't contain an extension, rootExt[0] 
# contains the entire src while rootExt[1] is empty.
            rootExt = greedyext(src)
            mode = rules[ridx][2]
            if rootExt[0][-1].isalpha() : bsel = 1
            elif rootExt[0][-1].isdigit() : bsel = 2
            else : bsel = 4
            if (mode & bsel) != 0 :
                if (mode & (bsel << 4)) == 0 :
                    newName += src # Copy unchanged into the new name.
                elif rootExt[1] != "" :
                    newName += rootExt[1] # Discard root but not any extension.
            else : 
                newName += nextName(rootExt[0], rules[ridx][1]) + rootExt[1]

        elif rules[ridx][0] == incRule :
            if type(rules[ridx][I_START]) is int :
                incName = '%0*d' % (rules[ridx][I_WIDTH], rules[ridx][I_START])
                rules[ridx][I_START] += rules[ridx][I_STEP]
            else : # alpha
                incName = rules[ridx][I_START]
                rules[ridx][I_START] = nextName(rules[ridx][I_START], 
                                                rules[ridx][I_STEP])
            if rules[ridx][I_MODE] & I_E : # Exactly as specified
                newName += incName
            else : # Always apply to root (default mode)
                rootExt = greedyext(newName)
                newName = rootExt[0] + incName + rootExt[1]

        ridx += 1
    return newName

# ------------------------------------------------------------------------
# getdir returns the unmodified list from os.listdir if sortdir is 0, the list 
# simply sorted if sortdir is 1, or the list case-insensitively sorted if 
# sortdir is 2. Under Windows, sortdir is alwasy 0. Under Linux it is 2 for 
# regression testing (option -TS); otherwise 1 only when native mode Insert-
# Increment rule is being applied.
# ....................................................................
def getdir() : 
    dl = os.listdir()
    if sortdir == 0 :
        return dl
    elif sortdir == 1 :
        dl.sort()
        return dl
    dl = [(f.lower(), f) for f in dl]
    dl.sort()
    return [f[1] for f in dl]

# ----------------------------------------------------------------------------
# procDir processes the current directory.
# Return 0 if no errors. It is not an error if no files meet the filter.
#   Loop through all files (including regular files, directories, etc.). 
# Anything that isn't a regular file or directory is immediately skipped. By 
# default, directories are skipped. Option -Fd includes directories as well as 
# files. -FD does only directories, skipping files. None of these are reported 
# regardless of the -P option to avoid cluttering the display with easily 
# predicted status.
#   After the initial file/directory filtering, if -FD contains excluded names
# and the name  matches then it is skipped. This is reported if -P requests 
# that skipped files be reported. There is no more filtering for option -S 
# (substitute). Native and RE (-E) modes additionally have their own filters. 
# Files that fail these are skipped (and reported if requested by -P).
#   -E and -S processes are very simple and embedded in the loop. Native mode 
# is much more complicated. It is implemented in the 'native' function in order
# to focus the loop block on operations shared by all three modes. -S and -E 
# modes raise the locally defined SkipFileException. native returns the new 
# name, which, if empty, causes SkipFileException to be raised. All further 
# processing is the same for all three modes. If the name is unchanged, nothing
# more is done (this can be reported by -P option). If the new name is the same
# as an existing file or one about to be created by renaming, collision 
# avoidance (CA) is engaged. CA is the same mechanism for all three renaming 
# modes.
#    Finally, depending on option -A (action) the files are renamed immdiately,
# the user is asked whether to make the changes (the default) or they are just
# displayed. If the changes are made they are recorded in reneAct for undo 
# option -U.
# ...........................................................................
class SkipFileException(Exception):
    pass
def procDir() :
    global newList
    newList = []
    renFiles = 0
    oldList = []

# scandir is more efficient than listdir when checking attributes, as in this 
# situation, but it requires Python 3.6 and the last one to run in XP is 3.4.
    dirlist = getdir()
    for old in dirlist :
        oldstat = os.stat(old).st_mode
        if stat.S_ISREG(oldstat) : # regular file.
            if opdirs > 1 : continue # Only dirs.
            if renePat.match(old) : continue # Don't rename our own files.
        elif stat.S_ISDIR(oldstat) : # directory
            if opdirs == 0 : continue # Only files.
        else : continue # Not file or directory.

        try :
            if len(fOpt) != 0 :
                for pat in fOpt :
                    if fnmatch.fnmatch(old, pat) :
                        raise SkipFileException(old)
            if len(sOpt) != 0 :
                newName = old
                for sop in sOpt :
                    if sop.upper() == 'U' :
                        newName = newName.upper()
                    elif sop.upper() == 'L' :
                        newName = newName.lower()
                    elif len(sop) == 2 :
                        newName = newName.replace(sop[0], 
                        sop[1] if sop[0] != sop[1] else "")
            elif eOpt :
                if not filter.match(old) :
                    raise SkipFileException(old)
                newName = filter.sub(sys.argv[2], old)
            else : # Native
                newName = native(old)
                if newName == "" :
                    raise SkipFileException(old)
        except SkipFileException as f :
            if pOpt & P_SKIP :
                print('Skipping', f)
            continue

        if newName == old :
            if pOpt & P_UNCHANGED :
                print(old, 'is unchanged')
            continue # Skip renaming

# .......................... Collision Avoidance ..........................
# If the newName is the same as an existing file under case-insensitive Windows
# the user is making a case change. This is very unlikely in Linux but using 
# os.path.samefile removes all uncertainty. If it says that old and newName 
# are the same file then the file is renamed. Otherwise, collision avoidance 
# is required. Collision stop and continue options apply only on collision with
# existing files, not to new-new collisions.
        if os.path.exists(newName) and not os.path.samefile(old, newName) :
            if caStop or caContinue :
                print(newName, 'already exists. Unable to rename', old)
                if caStop : return(1)
                continue
            newName = avoid(newName)
        elif newName in newList :
            newName = avoid(newName)
        if newName == "" :
            print('Unresolvable collision trying to rename', old)
            if caStop : return(1)
            continue

        renFiles += 1
        if pOpt & P_REN :
            print('Rename', old, 'to', newName) 
        oldList.append(old)
        newList.append(newName)
        # End of loop over files in directory

    if renFiles == 0 :
        print("No files meet the criteria for renaming")
        return(0)
    if aOpt == A_SHOW :
        return(0)
    if aOpt == A_ASK :
        try :
            print("Do you want to make these changes now? Y/N", 
            end=' ' , flush=True)
# Single key response by direct console access is convenient but it doesn't 
# support the automated response used in regression testing. option -TI makes
# useInput True, telling to use the input function instead. Also, although
# the direct I/O is reliable under Windows, the more complex Linux version
# make not work in all systems.
            if useInput :
                inp = input()
                if inp[0].upper() != 'Y' :
                    return(0)
            elif Windows :
                if kbhit() : getch() # Pre-flush needed only by W10.
                if getche().upper() != b'Y' :
                    return(0)
            else :
                if lingetch(True).upper() != 'Y' :
                    return 0
        except KeyboardInterrupt :
            exit(1)
    # A_REN or A_ASK+Y
    with open('reneAct', 'wt') as actFile :
        for act in zip(oldList, newList) :
            actFile.write(act[0] + '>' + act[1] + '\n')
            try :
                os.rename(act[0], act[1])
            except FileExistsError :
                print('Unable to overwrite', act[1])
                #return(1)
            except PermissionError :
                print('Denied access to', act[0])
                #return(1)
    return(0)

# ------------------------------------------------------------------------
# agnosticDir transforms absolute OS-specific directory (string) to relative 
# (to CWD when rene starts) with instances of \ (Windows) and / (Linux) 
# replaced with >. This is to simplify regression testing. The ensemble of 
# rene.py, renet.py, and support files can be moved to any directory and 
# between Windows and Linux without changing tests that use rene's display for 
# verification. This also only involves recursive operations (-UR and -R) 
# because rene doesn't display directory in any other circumstances.
#
# Besides displaying the situation to the user (particularly important if -AA) 
# the directories are saved in reneActr during -R operations and retrieved 
# from that file for -UR. For that, absolute OS-specific directories simplify 
# code.
# ..........................................................................
def agnosticDir(dir) :
   return dir[chopDir:].replace('\\', '>').replace('/', '>') 

# ---------------------------------------------------------------------------
# procTree implements directory recursion. It is self-recursive. It operates
# only on globals. It returns 0 on reaching restricted depth or the end of a
# branch without procDir or the next lower instance of itself returning an
# error. Only procDir can actually produce an error. This bubbles up through
# the recursive stack.
# This is a breadth-first recursion. Before recursing procDir is called to 
# process the current directory. Then the current directory is scanned for
# directories to recurse into. Consequently, the command may include renaming
# directories (-Fd or -FD) without confusing the recursion.
# By default, all directories are included and there is no depth limit. This
# is -R. Depth can be limited by a numeric argument, e.g. -R3. A list of 
# directory names (namespec, including * and ?) delimited by / is, by default 
# excluded. It can be inverted to be inclusive by + in the option. e.g.
# -R4/+/bak/temp
# .........................................................................
def procTree() :
    global curDepth
    ret = 0
    rDir = os.getcwd()
    rVisit.append(rDir)
    print(agnosticDir(rDir))
    for idx in irules :
        if rules[idx][I_MODE] & I_R :
            rules[idx][I_START] = rules[idx][I_RELOAD]
    if procDir() != 0 :
        return 1
    if curDepth >= rDepth :
        return 0
    curDepth += 1
    dirlist = getdir()
    for fn in dirlist :
        if stat.S_ISDIR(os.stat(fn).st_mode) :
            if len(rDirs) == 0 : 
                doit = True # All dirs are included if no list.
            else :
                for pat in rDirs :
                    if fnmatch.fnmatch(fn, pat) :
                        doit = rInc # This dir is in include list.
                        break
                else : 
                    doit = not rInc # This dir is not in exclude list.
            if doit :
                os.chdir(fn)
                ret = procTree()
                os.chdir('..')
                if ret != 0 :
                    break
    curDepth -= 1
    return ret

# ---------------------------------------------------------------------
# undo reverses the previous renaming in one directory as described by the 
# reneAct file in that directory.
def undo() :
    if not os.path.exists('reneAct') :
        print('Missing reneAct file')
    else :
        with open('reneAct', 'rt') as actFile :
            for line in actFile :
                act = line.rstrip().split('>')
                print('rename', act[1], 'back to', act[0])
                if not os.path.exists(act[1]) :
                    print(act[1], 'does not exist')
                elif os.path.exists(act[0]) :
                    print(act[0], 'already exists')
                else :
                    os.rename(act[1], act[0])
    return(0)

# -----------------------------------------------------------------------
# recUndo is recursive undo (option -UR). It is guided by reneActr file to 
# visit each directory of the last recursive undo and undo the renaming in 
# each as described by its own reneAct file. Although both write and read of 
# reneAct files and write of reneActr are in temporal order, reading of 
# reneActr goes backwards. Otherwise, recursive renaming of directories could 
# not be undone.
def recUndo() :
    if not os.path.exists('reneActr') :
        print('Missing reneActr file')
    else :
        with open('reneActr', 'rt') as df :
            dlist = list(df)
        for dir in reversed(dlist) :
            dir = dir.rstrip()
            print(agnosticDir(dir))
            os.chdir(dir)
            undo()
    return 0

# ========================== BEGIN HERE =================================

# ----------------- Special debug begin ----------------------------------
if True == False : # != turns on, == turns off
# For debugging under Idle or PDB, this simulates a command line under test. 
# Alternatives can be commented out but it is easier to just move the one to 
# test to the end of the assignments.
    import shlex
    cmd = r"rene.py test*. test? B/10"
    cmd = r"rene.py -U"
    cmd = r"rene.py 08493357-0*.tif hap*:.tif I/BAA/10"
    cmd = r"rene.py test8.png test9.png -X`~!@#$%^&()_+[}{]-"
    cmd = r"rene.py test8.png test9.png -S011"

    sys.argv = shlex.split(cmd)

# ---------------- This is where we normally begin -----------------------    
argc = len(sys.argv)

if argc == 1 : 
    print(r'rene.py version 2019.02.27 file renamer.')
    print(r'Command is rene.py filter replacement rules options.')
    print(r'Options are identified by prefix "-". Any filter or replacement')
    print(r'  that begins with - must be quoted.')
    print(r'Options -U and -S are used without filter, replacement, or rules.')
    print(r'Option -U undoes the last set of name changes as described by reneAct file.')
    print(r'  Edit reneAct file before rene -U for selective undo.')
    print(r'  -UR is recursive undo (including directories) guided by reneActr file.')
    print(r'Option -S applies character substitutions to all files. L and U lower- or')
    print(r'  upper-case all letters. All others are pairs. e.g. -SL/_-/ lower-cases')
    print(r'  and replaces _ with -. Repeated character, e.g. -S/--/, deletes every instance.')
    print(r'Option -E makes filter and replacement Pythonic regular expressions.')
    print(r'  Otherwise, they are rene native.')

    print(r'Option -F controls filtering defined by fields separated by /.')
    print(r'  d includes directories (default is only files).')
    print(r'  D renames only directories.')
    print(r'  C makes the filter case-sensitive (not applicable to -S).')
    print(r'  Each additional field specifies an excluded name (* wildcard).')

    print(r'Option -R recurses into subdirectories. With no parameters, the')
    print(r'  entire tree, to unlimited depth, is included.')
    print(r'  A number, e.g. -R5, limits the depth. 1 means only children.')
    print(r'  filespecs delimited by / are directories to exclude.')
    print(r'  /+/ tells to make the filespec list inclusive, excluding all others.')
    print(r'  e.g. -R4/.*/bak/ recurses down no more than 4 levels, excluding')
    print(r'  any directories that begin with . or that are named bak.')

    print(r'Option -A controls action. -AA (default) shows proposed changes and asks')
    print(r'  whether to make them. -AS shows propsed changes and exits. -AR renames')
    print(r'  without asking. The changes can still be undone by rene -U.')

    print(r'Option -P tells what events to print. The parameter is a bitmap, b0 for renames,')
    print(r'  b1 for collision avoidance process, b2 for files that fail filtering,')
    print(r'  b3 for files unchanged by the replacement. Default is -P1.')

    print(r'Option -X controls collision avoidance (CA). The parameter is a string in which')
    print(r'  S (stop) says to stop at the first collision.')
    print(r'  C (continue) says to skip that file.')
    print(r'  M says to merge name modification into the root name.')
    print(r'  A number defines a CA starting number (default is 0).')
    print(r'  A letter (other than SCM) defines a starting letter (instead of number).')
    print(r'  An alphanumeric string enclosed in / (i.e. /string/) is a starting string.')
    print(r'  A string of punctuation characters is added to the name between root')
    print(r'  and any other CA characters. If it begins with , the string (without ,)')
    print(r'  is prefix to the root. If ,, it is suffix to the complete CA root name.')

    print(r'In native mode, filter and replacement are required. rules depend on')
    print(r'  replacement. filter comprises literal "anchors" and * and ? "floaters", which')
    print(r'  are assigned fragments of the original name. * is any number of characters')
    print(r'  (including none). ? is one character by default but this can be changed by')
    print(r'  filter extension, which is filter/extension. Extension is a /-delimited')
    print(r'  list of definitions applied to successive ?s in filter. Canonical definition')
    print(r'  is /m,n,filter/ where m-n is width range. /filter/ has default width 0 (any)')
    print(r'  /m,n/ and /m/ specify width without filter. // (alias /1/)is placeholder.')
    print(r'Option -O changes source floater order. The parameter is comma-delimited')
    print(r'  list of indices. e.g. -O0,1,2 would not change order; -O2,1,0 would')
    print(r'  reverse it; -O2 would make it 2,0,1.')
    print(r'Replacement comprises literals and single-character variables, which are:')
    print(r'  * retain all of the corresponding floater.')
    print(r'  / discard the floater.')
    print(r'  ? retain portions of or modify the floater according to corresponding')
    print(r'    S (slice) or B (bump) rule.')
    print(r'  : insert (without consuming a floater) name fragment according to I rule.')
    print(r'Slice rule is S/leading/trailing/mode. mode 0 takes leading and trailing')
    print(r'  characters of the floater. mode 1 is standard slice. Default S is S/2/2/0.')
    print(r'Bump rule is B/step/mode. It increments/decrements the floater by step.')
    print(r'  Default B/1/0 increments all name types by 1.') 
    print(r'  mode 1 copies alpha, 0x11 discards it.')
    print(r'  mode 2 copies numeric, 0x22 discards it.')
    print(r'  mode 4 copies punctuation, 0x44 discards it.')
    print(r'  mode 3 copies numeric and alpha, 0x33 discards them.')
    print(r'  mode 5 copies alpha and punctuation, 0x55 discards them.')
    print(r'  mode 6 copies numeric and punctuation, 0x66 discards them.')
    print(r'Insert-increment rule is I/start/step/width/mode. start is number or alpha string.')
    print(r'  step is increment for each file. width is minimum character width only for')
    print(r'  numeric. mode may be E and/or R. E means to insert the increment exactly as')
    print(r'  specified, even if that means to the extension. R means to reset to the start')
    print(r'  for each directory under recursion (option -R). Default I is I/0/1/1/"".')
    exit(0)

# Parse command line options before anything else because they may establish 
# conditions for others. e.g. -FC makes the filter case-sensitive (default is 
# case-insensitive). 
class BadOptionException(Exception):
    pass
for arg in sys.argv[1:] :
    if arg[0] == '-' : # Option is any arg with - prefix
        try:
            if len(arg) < 2 :
                raise BadOptionException(arg)

            if arg[1] == 'U' : # Undo the last set of changes.
                if len(arg) == 2 :
                    exit(undo())
                elif len(arg) == 3 and arg[2] == 'R' :
                    exit(recUndo())
                else :
                    raise BadOptionException(arg)
            
            elif arg[1] == 'X' : # collision avoidance control
                i = 2
                while i < len(arg) :
                    if arg[i] == '/' : # String field
                        i += 1
                        caStart = re.search(r'([^/]*)', arg[i:]).groups()[0]
                        i += len(caStart)
                    elif arg[i] == 'S' : caStop = True
                    elif arg[i] == 'C' : caContinue = True
                    elif arg[i] == 'M' : caMerge = True
                    elif arg[i].isdigit() :
                        caStart = re.search(r'([0123456789]+)', arg[i:]).groups()[0]
                        i += len(caStart)
                        continue
                    elif arg[i].isalpha() : # Single letter
                       caStart = arg[i]
                    i += 1
                pm = re.search(r"([,]*)([`~!@#$%^&()_+[}{\]\-]+)", arg[2:]) 
                if pm :
                    if pm.groups()[0] == ',' :
                        caPunPos = 0
                    elif pm.groups()[0] == ',,' :
                        caPunPos = 2
                    caPun = pm.groups()[1]

            elif arg[1] == 'A' : # Action control
                if len(arg) < 3 :
                    print(r'-A needs an argument, A, S, or R')
                    exit(1)
                i = 'ARS'.find(arg[2].upper())
                if(i < 0) :
                    print(r'-A parameter can only be A, S, or R')
                    exit(1)
                aOpt = i

            elif arg[1] == 'S' :
                sOpt = parmList(arg[2:])
                if len(sOpt) == 0 :
                    print(r'-S (Substitute) option requires parameters.')
                    exit(1)

            elif arg[1] == 'O' : # Floater order
                if len(arg) < 3 :
                    print(r'-O (Order) option requires parameters.')
                    exit(1)
                oOpt = [int(e) for e in arg[2:].split(',')]

            elif arg[1] == 'F' : # Pre-filter
                pl = parmList(arg[2:])
                for p in pl :
                    if p == 'C' : 
                        filterCase = 0 # case-sensitive filter. 
                    elif p == 'D' : 
                        opdirs = 2 # Operate only on directories.
                    elif p == 'd' :
                        opdirs = 1 # Include directories in operations.
                    else :
                        fOpt.append(p) # A namespec to exclude

            elif arg[1] == 'R' : # Recurse
                rDepth = 1000 # Default is essentially infinite
                for p in parmList(arg[2:]) :
                    if p.isdigit() : rDepth = int(p)
                    elif p == '+' : rInc = True
                    elif p == '-' : rInc = False
                    else : rDirs.append(p)

            elif arg[1] == 'E' : # RE filter and replacement
                eOpt = True

            elif arg[1] == 'P' : # -P bit-map of what events to print.
                pOpt = 0xFFFF if len(arg) == 2 else scanint(arg[2:])

            elif arg[1] == 'T' : # Special test options mostly related to OS.
                for p in arg[2:] :
                    if p == 'S' :
                        sortDir = True
                    elif p == 'I' :
                        useInput = True
            else :
                raise BadOptionException(arg)

        except BadOptionException as a :
            print('Unrecognized option', arg)
            exit(1)

if aOpt != A_REN and pOpt == 0 : pOpt = 1
if caMerge and caPunPos == 1 : caPunPos = 2 # See avoid function.

if len(sOpt) == 0 and argc < 3 :
    print(r'Filter and replacement are required unless -U or -S option.')
    exit(1)
if len(sOpt) != 0 :
    pass
elif eOpt :
    filter = re.compile(sys.argv[1], filterCase)
else : # Native filter-replacement-rules.
# If the filter argument contains a / then filArg is assigned everything 
# preceding the / and filArgx everything after it. Otherwise, filArg is
# assigned the entire argument.
    idx = sys.argv[1].find('/')
    if idx == -1 :
        filArg = sys.argv[1]
        filArgx = ""
    else :
        filArg = sys.argv[1][:idx]
        filArgx = parmList(sys.argv[1][idx + 1:], True) # string to list, empty ok.
# ?s in filArg and rules (elements of filArgx) are sequentially coordinated but
# there can be fewer rules (even none) than ?s because ? defaults to any one 
# character. More filArgx elements than ?s in the filter would just be ignored 
# but the results would probably not be as expected. Therefore, that situation
# is reported as an error.
        if filArg.count('?') < len(filArgx) :
            print('The filter extension contains more elements than ?s in the filter.')
            exit(1)
    
    aRep = sys.argv[2]
    # Check filter and replacement generally for illegal characters.
    try :
        badChr(r'[<>|",\\;:/]', filArg ) # Illegal file chars except * and ?
        badChr(r'[<>|",\\;]', aRep )
    except ValueError :
        exit(1)
# The filter may contain any number of *s but none adjacent to each other, as 
# it would be impossible to determine their internal boundary. 
    if filArg.find(r'**') >= 0 :
        print('Illegal adjacent *s in', filArg)
        exit(1)
# There is no boundary ambiguity for ? when the width is either the default 1
# or specified as anything other than 0, which means zero or any number of
# characters. This cannot be determined without coordinated analysis of 
# the filter extension and ?s in the base filter.

# A filter that begins "*." could accept dot names, e.g. .emacs, by the general
# rule that a floater could be empty. But this is not usually the intent. To 
# avoid accidental renaming of dot names make noDotName flag True to reject 
# dot names even if the have passed the filter. These names will not be 
# rejected by the filter ".name", i.e. without the leading *.
    noDotName = True if filArg[:2] == '*.' else False 

#   The filter string is converted to RE and then compiled to a pattern. string-
# RE conversion mainly entails replacing any . with \. and * with (.*?) making 
# it a retrievable group (floater source). Non-greedy qualifier *? is needed 
# only for the case of sequential identical anchors, e.g. *_*_.
#   If the filter ends with '.' or '*.', it needs special handling. Ending 
# in . alone is a conventional means of saying that there is no extension. We 
# don't need that and it complicates pattern matching, so it is removed. If 
# the pattern ends with * then all of the remainder of the filename, including 
# extension, is collected into one floater. Sometimes, this is exactly what we 
# want but if we want the floater to only take the remainder of the root, we 
# need to explicitly tell this. '*.' does this but it needs to be converted to 
# the RE ([^.]*), which rejects any file name with extension while collecting 
# the remainder of the root name into a group. 
#   Filter extension (if there is one) has to be parsed in concert with the 
# base filter because specified width becomes part of the RE.

    fadd = "" # Filter addition is empty unless the argument ends with '*.'
    maxFloat = -1
    if filArg[-2:] == '*.' :
        filArg = filArg[:-2]
        fadd = r'([^.]*)' # This is added after RE conversion but before compile.
        maxFloat = 0
    elif filArg[-1] == '.' :
        filArg = filArg[:-1]
    filRe = ""
    filxIdx = 0
    for c in filArg :
        if c == '.' :
            filRe += r'\.'
        elif c == '*' :
            maxFloat += 1
            filRe += '(.*?)'
        elif c == '?' :
            maxFloat += 1
            if filxIdx >= len(filArgx) :
                filRe += '(.)' # Default ? means any one character.
            else :
# The canonic filter extension is /width,filter, which can be split on ','. 
# Width is either a single number or a range m-n. Initially, value range is 
# the only type of semantic filter but additional types are anticipated. The 
# full canonic extension can be reduced for convenience in some cases. Because 
# extensions are sequentially associated with ?s in the base filter, 
# placeholder extensions /1/ are sometimes needed. These can be reduced to //. 
# A single clause (i.e. no ,) is assumed to be width but if it is not m or
# m-n, then it can be assumed to be filter with a default any (0) width. 
# /,filter can also be interpreted as 0 width. These small reductions can 
# emphasize the purpose by de-emphasizing don't care parameters.
#
# Split the rule into field width and filter criteria. If it only specifies 
# width then it can be converted to RE and deleted. Otherwise, the rule is 
# changed from one string to a tuple containing the associated floater index 
# and the filter criteria descriptor. In the end, filArgx is a condensed list 
# of semantic rules tagged with the floater index to which they apply. Note 
# that these indices start at 1 because they will be used to select groups 
# after re.match, where group 0 is the entire file name.
                fidx = 2 # rule[2] is filter for canonical case m,n,filter
                rule = filArgx[filxIdx].split(',')
                if rule == [""] : # Empty placeholder // = /1/
                    filRe += '(.)'
                elif rule[0].isnumeric() : # width
                    if len(rule) > 1 and rule[1].isnumeric() : # min,max width range
                        filRe += '(.{' + rule[0] + ',' + rule[1] + '})' # (.{m,n})
                    else :
                        fidx = 1
                        if rule[0] == '0' :
                            filRe += '(.*?)' # non-greedy any width.
                        else :
                            filRe += '(.{' + rule[0] + '})' # (.{m})
                else : # Non-empty and non-numeric must be filter without width.
                    fidx = 0 
                    filRe += '(.*?)' # Default width.
                if fidx >= len(rule) : # No filter argument
                    del(filArgx[filxIdx])
                else :
                    rule = rule[fidx]
                    rang = rule.split('-')
                    if len(rang) == 2 :
# Numeric or Alphabetic range. They are nearly the same but numeric works with
# numbers following normal arithmetic rules, regardless of span. Alpha compares
# LR making e.g. '98' < '99' but also '100' < '99'.
                        if rang[0][0] == '#' :
                            try :
                                rule = (FX_NRANGE, int(rang[0][1:]), int(rang[1]))
                            except ValueError :
                                print(rule, 'Incorrect numeric range')
                                exit(1)
                        else :
                            rule = (FX_ARANGE, rang[0], rang[1])
                    else :
                        print('Unrecognized semantic filter rule', rule)
                        exit(1)
                    filArgx[filxIdx] = (maxFloat + 1, rule)
                    filxIdx += 1
        else :
            filRe += c
    filRe += fadd + '$'        
    filter = re.compile(filRe, filterCase)

# If the order option (-O) redefines the floater source order, it must not 
# specify any index greater than maxFloat. If it doesn't specify all of them, 
# the unspecified ones are appended to it in numerical order. It could 
# theoretically specify more than there are source floaters by duplicating 
# some. However, this would complicate the replacement process too much for 
# something unlikely to get much use. Since any extras will just be ignored in 
# replacement there is no need to report this as an error.
    if len(oOpt) > 0 :
        for idx in oOpt : 
            if idx > maxFloat :
                print('Order option index', idx, '> maximum index', maxFloat)
                exit(1)
        missing = maxFloat + 1 - len(oOpt)
        for idx in range(0, maxFloat + 1) :
            if missing < 0 :
                break
            if idx in oOpt :
                continue
            oOpt.append(idx)
            missing -= 1

# split the replacement argument on single-char variables and remove all of 
# the empty strings resulting from leading, trailing and adjacent variables.
    lrep = [v for v in re.split(r'([' + rvars + r'])', aRep) if v != ""]

# Find the index of the last floater consumer in the replacement list. If 
# there are more floaters than consumers, the extras will be given to the last
# consumer as each file is processed.
    lastConsumer = -1
    for i,v in enumerate(lrep) :
        if v in consumers :
            maxConsumer = i

# Create a condensed tuple of replacement variables that require rules. This
# is used only for checking the rules as they are parsed and to verify that
# the number of rule arguments and rule consumers in the replacement are equal.

    rulevars = tuple(rep for rep in lrep if rep == rvRule or rep == rvAdd)

# Rules  are all arguments after filter and replacement. Rules typically are 
# all declared in one group followed by options but they may be mixed and in 
# any order. Options begin with -. Options are self-contained and relatively 
# simple to process. Rules can't be fully validated without knowing the 
# corresponding replacement variable. rulevars, created while parsing the 
# replacement argument
    rvIdx = 0 # rule variable index.
    if argc > 3 :
        for arg in sys.argv[3:] :
            if arg[0] != '-' : # rule is any arg without - prefix
                try :
                    if len(rulevars) <= rvIdx :
                        print('More rules than specified in the replacement')
                        exit(1)
                    rules.append(prepRule(arg, repRules[arg[0]], rulevars[rvIdx]))
                    if rules[rvIdx][0] == 'I' :
                        irules.append(rvIdx) # In case of recursion with reload.
                    rvIdx += 1
                except KeyError :
                    print('Unrecognized rule', arg)
                    exit(1)
                except ValueError :
                    exit(1)

    nRules = len(rules)

    if nRules < len(rulevars) :
        print(aRep, ' contains ', len(rulevars), ' rule-based variables (',
              rvRule, rvAdd, ') but only ', nRules, ' is/are defined', sep = "")
        exit(1)

    if not Windows and len(irules) != 0 and sortdir == 0 :
        sortdir = 1
        
if rDepth == 0 :
    exit(procDir())
ret = procTree()
with open('reneActr', 'wt') as rf :
    for dir in rVisit :
        rf.write(dir + '\n')
exit(ret)

 
        
