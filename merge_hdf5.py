# 
import tables
import numpy as np
import sys
if sys.version_info[0] >= 3:
    import pickle
else:
    import cPickle as pickle

#--------------------------------------------------
import glob
def glob_filenames(tablelist) :
    """
    Function to generate filename list.

    Parameters
    ----------
    tablelist : str
        Could be a name of list file that contains 
        list of h5 files, or a name of h5 file 
        with wildcard

    Returns
    ----------
    filenames : list
        list of string(name of h5 files)
    """

    if type(tablelist) != str :
        print("glob_filenames takes string argument.")
        sys.exit(0)

    filenames = []
    if "*" in tablelist :
        '''
        tablelist contains wildcard. glob it.
        '''
        filenames = glob.glob(tablelist)

    elif ".h5" in tablelist or ".hdf5" in tablelist:
        '''
        tablelist is a name of an hbook file.
        '''
        filenames.append(tablelist)

    else :
        '''
        tablelist is a name of a listfile that
        contains names of hbook file.
        '''
        flist = open(tablelist)
        for i, fname in enumerate(flist):
            if fname.count("#") :
                continue
            print(fname)
            filenames.append(fname.strip())
        flist.close()

    if len(filenames) == 0 :
        print("glob is failed, is the path %s exist?" % (tablelist))
        sys.exit(0)
    return filenames

#--------------------------------------------------
def load_a_table(fname) :
    """
    loading all tables listed in the filelist

    Parameters
    ----------
    fname: 
        name of h5 file

    Returns
    ----------
    tablelist : list
        list of tables
    """
    tablelist = []
    myt = tables.open_file(fname)
    tablelist.append(myt)
    return tablelist


#--------------------------------------------------
def load_tables(filelist) :
    """
    loading all tables listed in the filelist

    Parameters
    ----------
    filelist : 
        Could be a name of list file that contains 
        list of h5 files, or a name of h5 file 
        with wildcard

    Returns
    ----------
    tablelist : list
        list of tables
    """
    tablelist = []
    filenames = glob_filenames(filelist)
    for i, fname in enumerate(filenames) :
        myt = tables.open_file(fname)
        tablelist.append(myt)

    print("tablelist %s is successfully loaded" % (filelist))
    return tablelist

#--------------------------------------------------
def close_tables(tablelist) :
    """
    function to close all tables.

    Parameters
    ----------
    tablelist : list of tables
    """

    for myt in tablelist :
        myt.close()
    print("tablelist %s is successfully closed" % (tablelist))

#--------------------------------------------------
def check_tables(tablelist, nodename, leafname) :
    """
    function to check whether the nodename and leafname exist
    in tables or not.
    if succeed, it returns number of tables.
    if failed it returns -1.
    """
    if nodename[0] != "/" :
        nodename = "/%s" % nodename

    nfiles = 0
    if type(tablelist) == str :
        '''
        tablelist is not loaded yet. load tables first
        and check nodename and leafname.
        ''' 
        filenames = glob_filenames(tablelist)
        for i, fname in enumerate(filenames):
            myt = tables.open_file(fname)
            if not nodename in myt :
                print("nodename %s does not exist." % (nodename))
                myt.close()
                return -1

            node = myt.get_node(nodename)
            if not leafname in node.colnames :
                print("leafname %s does not exist." % (leafname))
                myt.close()
                return -1
            myt.close()
            nfiles = nfiles + 1
        return nfiles

    else :
        '''
        tablelist is a list of tables
        ''' 
        for myt in tablelist:
            if not nodename in myt :
                print("nodename %s does not exist." % (nodename))
                return False

            node = myt.get_node(nodename)
            if not leafname in node.colnames :
                print("leafname %s does not exist." % (leafname))
                return False

            nfiles = nfiles + 1
        return nfiles

#--------------------------------------------------
def check_leaf(tablelist, nodename, leafname) :
    """
    function to check whether the nodename and leafname exist
    in tables or not.
    It checks the first table only.
    To check whole tables, use check_tables.
    """
    if nodename[0] != "/" :
        nodename = "/%s" % nodename

    if type(tablelist) == str :
        '''
        tablelist is not loaded yet. load tables first
        and check nodename and leafname.
        ''' 
        filenames = glob_filenames(tablelist)
        myt = tables.open_file(filenames[0])
        if not nodename in myt :
            myt.close()
            return False

        node = myt.get_node(nodename)
        if not leafname in node.colnames :
            myt.close()
            return False
        myt.close()
        return True

    else :
        '''
        tablelist is a list of tables
        ''' 
        myt = tablelist[0]
        if not nodename in myt :
            return False

        node = myt.get_node(nodename)
        if not leafname in node.colnames :
            return False

        return True

#--------------------------------------------------
def read_tables(tablelist, nodename, leafname) :
    """
    Read data named leafname from tables and merge 
    them to one (n, 1) array
    If tablelist is string, it leads only one table 
    at a time and append the data to a buffer.

    Parameters
    ----------
    tablelist : str or list of tables
        filename of list of h5 files or 
        filename that contains wildcard or
        list of opened h5 objects stored with load_tables

    nodename : str
        name of branch of h5 file

    leafname : str
        name of leaf of h5 file

    Returns
    ----------
    buf : (n, 1) numpy array

    """

    buf = "notyetfilled" # dummy
    if nodename[0] != "/" :
        nodename = "/%s" % nodename

    if isinstance(tablelist, str) :
        '''
        load one h5 table at a time, slow but 
        uses less runtime memory
        '''
        filenames = glob_filenames(tablelist) 
        for i, fname in enumerate(filenames):
            #print("open file %s" % (fname))
            if fname[0] == "#" :
                continue
            myt = tables.open_file(fname)
            filesize = myt.get_filesize()
            if filesize < 2800 :
                # this is empty file. skip it.
                continue

            if isinstance(buf, str) :
                buf = myt.get_node(nodename).col(leafname)
                
            else :
                buf = np.hstack((buf, myt.get_node(nodename).col(leafname)))

            #myt.close()

    else :
        '''
        tablelist is list of tables filled with 
        load_tables.
        fast, but uses more runtime memory
        '''
        for i, t in enumerate(tablelist):
            #print i, t
            filesize = tablelist[i].get_filesize()
            if filesize < 2800 :
                # this is empty file. skip it.
                continue
     
            if i == 0 :
                buf=tablelist[i].get_node(nodename).col(leafname)
            else :
                buf = np.hstack((buf, tablelist[i].get_node(nodename).col(leafname)))

    #print nodename, leafname, buf.shape
    return buf

#--------------------------------------------------
def read_pickles(tablelist, leafname) :
    """
    Read data named leafname from dictionaries and merge 
    them to one (n, 1) array
    If tablelist is string, it leads only one dictionary
    at a time and append the data to a buffer.

    Parameters
    ----------
    tablelist : str or list of tables
        filename of list of pickles files or 
        filename that contains wildcard or
        list of opened dictionaries 

    leafname : str
        name of key of dictionary

    Returns
    ----------
    buf : (n, 1) numpy array

    """

    buf = "notyetfilled" # dummy

    if isinstance(tablelist, str) :
        '''
        load one pickle at a time, slow but 
        uses less runtime memory
        '''
        filenames = glob_filenames(tablelist) 
        for i, fname in enumerate(filenames):
            #print("open file %s" % (fname))
            myt = pickle.load(open(fname))
            if isinstance(buf, str) :
                buf = myt[leafname]
                
            else :
                buf = np.hstack((buf, myt[leafname]))


    else :
        '''
        tablelist is list of dictionary filled with 
        load_tables.
        fast, but uses more runtime memory
        '''
        for i, t in enumerate(tablelist):
            #print i, t
            if i == 0 :
                buf=tablelist[i][leafname]
            else :
                buf = np.hstack((buf, tablelist[i][leafname]))

    print(leafname, buf.shape)
    return buf


