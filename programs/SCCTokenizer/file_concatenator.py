import glob2
from subprocess import Popen, PIPE
import os, sys, traceback
import datetime as dt


file_id_list = []
starting_postid = 0
starting_blockid = 0


def get_methods(file):
    p = Popen(["java", "-jar", "MethodExtractor-1.0-SNAPSHOT.jar", file], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    # print output.strip()
    # print err.strip()
    try:
        with open("methods.txt", "r") as f:
            all_methods = f.read()
            methods = all_methods.split("@@==UCL==@@")
        return methods
    except Exception as e:
        print file + ": no method found."

    return []


def get_file_list(home_dir, filter):
    """
    Get all files with the given extension in a folder recursively
    :param home_dir: the location to search for files
    :param filter: filter of the file's extension (e.g. *.java)
    :return: list of files
    """
    all_files = glob2.glob(home_dir + '/**/' + filter)
    return all_files


def createFileId(file):
    global file_id_list
    global starting_blockid
    file_id_list.append(file)
    fileid = file_id_list.index(file) + starting_blockid
    writefile("so-headers.txt", str(fileid) + "," + file + "\n", "a", False)

    return fileid


def saveFileId():
    global file_id_list
    # print file_id_list
    try:
        os.remove("so-headers.txt")
    except Exception as e:
        print "couldn't remove so-headers.txt file."

    for index, file in enumerate(file_id_list):
        writefile("so-headers.txt", str(index) + "," + file + "\n", "a", False)

    print "saved so-headers.txt."


def writefile(filename, fcontent, mode, isprint):
    """
    Write the string content to a file
    copied from
    http://www.pythonforbeginners.com/files/reading-and-writing-files-in-python
    :param filename: name of the file
    :param fcontent: string content to put into the file
    :param mode: writing mode, 'w' overwrite every time, 'a' append to an existing file
    :return: N/A
    """
    # try:
    file = open(filename, mode)
    file.write(fcontent)
    file.close()

    if isprint:
        print "saved:" + filename


def main():

    if len(sys.argv) == 1:
        print '-' * 60
        print 'Usage: python file_concatenator.py <location of SO snippets> <starting ID>'
        print '-' * 60
        exit()

    # remove the old output file
    try:
        os.remove("so.txt")
    except Exception as e:
        print "No so.txt file ..."

    # remove file_id_list
    try:
        os.remove("so-headers.txt")
    except Exception as e:
        print "couldn't remove so-headers.txt file."

    # get list of Java files
    javafiles = get_file_list(sys.argv[1], "*.java");

    # get the starting id, if not, start at 0
    global starting_blockid
    global starting_postid

    starting_blockid = int(sys.argv[2])

    # if len(sys.argv) == 4:
        # starting_postid = int(sys.argv[2])

    print "files: ", len(javafiles)
    
    p_start = dt.datetime.now()

    # start method extraction
    for index, jfile in enumerate(javafiles):
        try:
            sys.stdout.write(str(index) + ": " + jfile)
            sys.stdout.flush()
            methods = get_methods(jfile)
            print ":", len(methods), "methods."
            for i, method in enumerate(methods):
                # print method
                method_parts = method.split("@@UCL@@")
                lines = len(method_parts[1].strip().split("\n"))

                # filter for only the one with more than 10 lines
                if lines >= 10:
                    writefile("so.txt", "===@@@UCI===\n", "a", False)
                    id = createFileId(jfile + "," + method_parts[0].strip())
                    # writefile("so.txt", str(index + starting_postid) + "\n", "a", False)
                    # -1 means we don't care about parentId
                    writefile("so.txt", "-1\n", "a", False)
                    writefile("so.txt", str(id) + "\n", "a", False)
                    writefile("so.txt", method_parts[1].strip() + "\n", "a", False)
        except Exception as e:
            writefile("errors.txt", "error processing " + jfile + ".\n", "a", False)
            traceback.print_exc(file=sys.stdout)
    # saveFileId()

    p_elapsed = dt.datetime.now() - p_start
    print "all done in ", p_elapsed


main()
