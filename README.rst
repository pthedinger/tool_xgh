XCore/XMOS Repository Github Script
===================================

When XMOS maintained XCore repositories are released the information
about that release is put in a metainformation file called ``xpd.xml``
in the repository.

The ``xgh.py`` python script allows you to use this
information to see released versions of a repository and its
dependencies within the github repositories.


Usage
-----

The following will give you the possible commands::

  xgh.py help

The ``status`` command shows you the state of the repo and its
dependencies e.g.::

     $ xgh.py status
     Current Version: 1.0.1alpha0
     Dependencies:
        sc_i2c: 2.1.0rc0
        sc_i2s: 1.4.1alpha0
        sc_sdram_burst: 1.0.1rc0
        sc_util: 3f82b84639

The ``list`` command will show you the released versions of the
repository::

 $ xgh.py list
   1.0.0alpha0
   1.0.0alpha1
   1.0.0alpha2
   1.0.0alpha3
   1.0.0rc0
   1.0.1alpha0

The ``checkout`` command will checkout a version and checkout the
correct related version of all the dependent repos e.g.::
     
     $ xgh.py checkout 5.1.1.
     Checking out 5.1.1
     Note: checking out 'dc6f822b16674eafc0e32ed2ba24db5ec96cb397'.
      
     You are in 'detached HEAD' state. You can look around, make experimental
     ....
      
     sc_i2c: Checking out 6bc49309bfb86c7648c3988d661810f8870350a3
     Note: checking out '6bc49309bfb86c7648c3988d661810f8870350a3'.
      
     You are in 'detached HEAD' state. You can look around, make experimental
     ...
      
     sc_xtcp: Checking out 64e37067439ef669ea53f2b572f2b6885d01cb24
     Note: checking out '64e37067439ef669ea53f2b572f2b6885d01cb24'.
      
     You are in 'detached HEAD' state. You can look around, make experimental
     ...
     ...
     ...

You can also do ``xgh.py checkout master`` to checkout the repo and
all its dependencies back to the HEAD of the master branch.
