# Basic Imports for readubg files and csv(pandas)
import sys
import pandas as pd
import os

#Class to containerise the combine function and other utility function
class CombineCSV():

    '''
    Function to check if files passed in the command line argument are valid
    '''
    def fileValid(self, fList):

        # If no file names are passed, print error and return False
        if len(fList) <= 1:
            print("No files provided in input.")
            return False
        
        #Iterate throught each file
        for f in fList:
            # If file does not exist in the path, print error and return False
            if not os.path.exists(f):
                print("File not found in directory.")
                return False
            
            # If file is empty, print error and return False
            if os.path.getsize(f) == 0:
                print("File is empty.")
                return False
        #Otherwise, all files are valid, return True
        return True

    '''
    To handle the case of different columns, iterate through first line of each file and maintain
    a set to keep track of new columns. Append the relevant columns to a list since sets are unordered in python
    File_1 has columns: A,B,C
    File_2 has columns: B,C,D
    This function will return a list of final columns => [A,B,C,D]
    '''
    def getAllColumns(self, fList):
        colSet = set()
        allCols = []
        for i in fList:
            f = open(i, "r")
            colList = f.readline().split(",")
            f.close()
            for idx,col in enumerate(colList):
                if idx == len(colList)-1:
                    temp = col[1:-2]
                else:
                    temp = col[1:-1]
                if temp not in colSet:
                    colSet.add(temp)
                    allCols.append(temp)
        allCols.append("filename")
        return allCols

    '''
    Function to perform the main task of combining the CSVs. If the columns across the files are same, the combining is trivial.
    However, if there are different columns in the CSV files, final CSV with all columns will be printed on stdout with null (NaN) 
    values in places where that column does not belong to that file. Additionally, a "filename" column is added to the combined CSV.
    To make sure that we don't encounter any memory error while mearging the files, the file is read in chunks of 10^4 rows at a time. 
    This chunk is stored as dataframe in dfList. Once the active row count reaches 10^5, the dataframes in the dfList are concatenated 
    using concat function of pandas library. Rowcount and dfList are reset.
    (Note: Rowcount and chunksize can be adjusted according to the system's memory limits)
    '''
    def combineCSV(self, args):
        #If all the files pass the validity check, combine them
        if self.fileValid(args):
            #Extract necessary file names from command line arguments
            fList = args[1:]
            #Create a dummy dataframe with all columns in the header and insert it into the the dataframe list, dfList
            dummyDF = pd.DataFrame(dict({i:[None] for i in self.getAllColumns(fList)}))
            dfList = [dummyDF]

            #Row count to keep track that we dont exceed memory limits.
            rowCount = 0
            #Flag to check if header of file was printed once
            flag = True
            #Iterate through every file
            for f in fList:
                #Read it chunk by chunk
                for fragment in pd.read_csv(f, chunksize=10**4):
                    #Add new column of filename and its value
                    fragment['filename'] = f
                    #Append the dataframe to dfList
                    dfList.append(fragment)
                    #Update rowcount with previous dataframe's rowcount
                    rowCount += fragment.shape[0]
                    #If threshold of rwocount is crossed, print the concatenated dfList
                    if rowCount > 10**5:
                        print(pd.concat(dfList, axis = 0, ignore_index=True).iloc[1:,:].to_csv(index=False),end="")
                        #Reset rowcount and dfList
                        dfList = [dummyDF]
                        rowCount = 0
                        #Toggle the header flag
                        flag = False
            #If the header flag was toggled, print the rest of rows without the header
            if flag == False:
                print(pd.concat(dfList, axis = 0, ignore_index=True).iloc[1:,:].to_csv(index=False, header=False))

            #Else, print with header(when total number of rows is less than rowcount threshold)
            else:
                print(pd.concat(dfList, axis = 0, ignore_index=True).iloc[1:,:].to_csv(index=False))

        #Else return
        else:
            return

    def main(self):
        self.combineCSV(sys.argv)

if __name__ == "__main__":
    cc = CombineCSV()
    cc.main()