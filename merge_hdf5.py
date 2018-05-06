# 
import tables
import numpy as np


def load_tables(filelist) :
    """
    loading all tables listed in filelist
    """
    tablelist = []
    if ".h5" in filelist or ".hdf5" in filelist:
        '''
        this is not a list, but .h5 file name.
        just load the table.
        '''
        myt = tables.open_file(filelist)
        tablelist.append(myt)

    else :
        for i, fname in enumerate(open(filelist)) :
            if fname.count("#") :
                continue
            print fname
            myt = tables.open_file(fname.strip())
            tablelist.append(myt)
            #myt.close()

    print "tablelist %s is successfully loaded" % (filelist)

    return tablelist

def close_tables(tablelist) :
    for myt in tablelist :
        myt.close()
    print "tablelist %s is successfully closed" % (tablelist)

def check_table(tablelist, nodename, leafname) :
    if nodename[0] != "/" :
        nodename = "/%s" % nodename

    if type(tablelist) == str :

        if ".h5" in tablelist or ".hdf5" in tablelist:
            '''
            this is not a list, but .h5 file name.
            just load the table.
            '''
            myt = tables.open_file(tablelist)
            if not nodename in myt :
                #print("nodename %s does not exist." % (nodename))
                myt.close()
                return False

            node = myt.get_node(nodename)
            if not leafname in node.colnames :
                #print("leafname %s does not exist." % (leafname))
                myt.close()
                return False
            myt.close()
            return True

        else :
 
            flist = open(tablelist)
            for i, fname in enumerate(flist):
                if fname.count("#") :
                    continue
                print fname

                myt = tables.open_file(fname.strip())
                if not nodename in myt :
                    #print("nodename %s does not exist." % (nodename))
                    myt.close()
                    return False

                node = myt.get_node(nodename)
                if not leafname in node.colnames :
                    #print("leafname %s does not exist." % (leafname))
                    myt.close()
                    return False
                myt.close()
                return True
               
    else :
        myt=tablelist[0]
        if not nodename in myt :
            #print("nodename %s does not exist." % (nodename))
            myt.close()
            return False

        node = myt.get_node(nodename)
        if not leafname in node.colnames :
            #print("leafname %s does not exist." % (leafname))
            myt.close()
            return False
        myt.close()
        return True

import copy
def read_tables(tablelist, nodename, leafname) :
    """
    Read data named leafname from tables and merge them to one (n, 1) array
    If tablelist is string, it leads only one table at a time and append the data to a buffer.
    :param tablelist: filename list of h5 files or list of opened h5 objects stored by load_tables()
    :param nodename:  name of branch of h5 file,
    :param leafname: name of leaf of h5 file
    :return (n, 1) numpy array
    """
    buf = "notyetfilled" # dummy
    if nodename[0] != "/" :
        nodename = "/%s" % nodename

    if type(tablelist) == str :
        '''
        load one h5 table at a time, slow but uses less runtime memory
        '''
        if ".h5" in tablelist or ".hdf5" in tablelist:
            '''
            this is not a list, but .h5 file name.
            just load the table.
            '''
            myt = tables.open_file(tablelist)
            buf = myt.get_node(nodename).col(leafname)
            myt.close()

        else :
            flist = open(tablelist)
            for i, fname in enumerate(flist):

                if fname.count("#") :
                    continue
                print fname

                myt = tables.open_file(fname.strip())
                if buf == "notyetfilled" :
                    #buf = copy.deepcopy(myt.get_node(nodename).col(leafname))
                    buf = myt.get_node(nodename).col(leafname)
                    
                else :
                    #buf = np.hstack((buf, copy.deepcopy(myt.get_node(nodename).col(leafname))))
                    buf = np.hstack((buf, myt.get_node(nodename).col(leafname)))

                myt.close()
            flist.close()

    else :
        '''
        fast, but uses more runtime memory
        '''
        for i, t in enumerate(tablelist):
            #print i, t
            if i == 0 :
                buf=tablelist[i].get_node(nodename).col(leafname)
            else :
                buf = np.hstack((buf, tablelist[i].get_node(nodename).col(leafname)))

    print nodename, leafname, buf.shape
    return buf


