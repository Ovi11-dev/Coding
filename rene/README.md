rene readme
Updated: 2019.02.27
This comprises only release notes. The manual, which describes installation and 
use, is rene.doc.

        Release 1.0.2 2019.02.27
- Changed native mode filter extension syntax from /width,rule to /m,n,rule. 
The resulting disambiguation enables abbreviated forms. These are described in
updated rene.doc.
- Correct rene.doc command line description. Arguments are optional but must
be in the indicated order if present.
- Added tests to renet.py for new features and previously overlooked cases.

        Release 1.0.1 2019.02.23
Corrects native mode filter bug where successive identical anchors allowed 
floaters to consume too much of the original file name. e.g. *_*_ was not taken 
as two floaters separated by _ but as one floater containing _. A test for this
was also added to renet.py, the regression test program.

        Release 1.0.0 2019.02.16
Initial release. Passes regression tests but has undergone no outside testing.
Expect frequent updates for a while.
