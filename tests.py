#Basic imports necessary for unit testing and importing the CombineCSV class from csvCombiner
from io import StringIO
import csv
from csvCombiner import CombineCSV
import generateTestData
import os
import sys
import pandas as pd
import unittest

#Class to containerise the unit testing functions and data members
class TestCombineCsv(unittest.TestCase):
    
    #File paths of test data files
    testOutputsPath = "./test_data/output.csv"
    csvCombinerFilePath = "./csvCombiner.py"
    accessoriesFilePath = "./test_data/accessories.csv"
    clothingFilePath = "./test_data/clothing.csv"
    householdFilePath = "./test_data/household_cleaners.csv"
    emptyFilePath = "./test_data/empty.csv"


    res = sys.stdout
    testOutput = open(testOutputsPath, "w+")
    #Creating the object of CombineCSV class
    cc = CombineCSV()

    '''
    Setup class method to perform some tasks before testing
    '''
    @classmethod
    def setUpClass(cls) -> None:
        #Generating the test data
        generateTestData.main()
        # Creating empty file for testing it later
        with open(cls.emptyFilePath, 'w', encoding='utf-8') as fh:
            pass
    
    '''
    Class method to clean up after the tests are executed
    '''
    @classmethod
    def tearDownClass(cls) -> None:
        #Closing the output file
        cls.testOutput.close()

        # Deleting the test data files if they exist
        if os.path.exists(cls.testOutputsPath):
            os.remove(cls.testOutputsPath)
        
        if os.path.exists(cls.accessoriesFilePath):
            os.remove(cls.accessoriesFilePath)
        
        if os.path.exists(cls.clothingFilePath):
            os.remove(cls.clothingFilePath)
        
        if os.path.exists(cls.householdFilePath):
            os.remove(cls.householdFilePath)
        
        if os.path.exists(cls.emptyFilePath):
            os.remove(cls.emptyFilePath)

    '''
    Setup function for tests
    '''
    def setUp(self):
        #Basic setup to get content of stdout and opening the test output file
        self.output = StringIO()
        sys.stdout = self.output
        self.testOutput = open(self.testOutputsPath, 'w+')
        
    '''
    Function to tear down the mess after testing like truncating output files, writing values from stdout 
    to test output file and then closing the test output file
    '''
    def tearDown(self):
        self.testOutput.close()
        self.testOutput = open(self.testOutputsPath, 'w+')
        sys.stdout = self.res
        self.testOutput.truncate(0)
        self.testOutput.write(self.output.getvalue())
        self.testOutput.close()

    '''
    Test to check if fileValid function detects if no files are provided in command line input and returs false
    '''
    def test_noFile(self):
        testResult = self.cc.fileValid([self.csvCombinerFilePath])
        self.assertFalse(testResult)

    '''
    Test to check if fileValid return false for empty file
    '''
    def test_emptyFile(self):
        self.cc.fileValid([self.csvCombinerFilePath, self.emptyFilePath])
        self.assertIn("File is empty.", self.output.getvalue())

    '''
    Test to check if fileValid return false for a non-existent file
    '''
    def test_nonExistentFile(self):
        testResult = self.cc.fileValid([self.csvCombinerFilePath, "random.csv"])
        self.assertFalse(testResult)

    '''
    Test to check if fileValid returns True if valid files are given
    '''
    def test_validFiles(self):
        testResult = self.cc.fileValid([self.csvCombinerFilePath, self.accessoriesFilePath, self.clothingFilePath, self.householdFilePath])
        self.assertTrue(testResult)

    '''
    Test to check if addition of new "filename" column is done
    '''
    def test_newColumnAdded(self):
        self.cc.combineCSV([self.csvCombinerFilePath, self.accessoriesFilePath, self.clothingFilePath, self.householdFilePath])
        self.testOutput.write(self.output.getvalue())
        self.testOutput.close()
        combined_df = pd.read_csv(self.testOutputsPath)
        self.assertIn('filename', list(combined_df.columns))

    '''
    Test to check if the filename column is not empty and has correct values filled in
    '''
    def test_newColumnNotEmpty(self):
        #Execute the combine csv on given test_data files as input and save the stdout content to test output file
        self.cc.combineCSV([self.csvCombinerFilePath, self.accessoriesFilePath, self.clothingFilePath, self.householdFilePath])
        self.testOutput.write(self.output.getvalue())
        self.testOutput.close()
        combined_df = pd.read_csv(self.testOutputsPath)
        #Checking if values in filename column match with actual filenames to which the record belongs
        self.assertIn(self.accessoriesFilePath, combined_df.loc[:,'filename'].values)
        self.assertIn(self.householdFilePath, combined_df.loc[:,'filename'].values)
        self.assertIn(self.clothingFilePath, combined_df.loc[:,'filename'].values)

    '''
    Test to check if the combining of csv is done correctly. Individual rows of each file are compared 
    with their row counts in the combined file by using pandas query option
    '''
    def test_mergeCorrectlyDone(self):
        #Execute the combine csv on given test_data files as input and save the stdout content to test output file
        self.cc.combineCSV([self.csvCombinerFilePath, self.accessoriesFilePath, self.clothingFilePath, self.householdFilePath])
        self.testOutput.write(self.output.getvalue())
        self.testOutput.close()

        #Reading the test data files
        accessories_df = pd.read_csv(self.accessoriesFilePath)
        clothing_df = pd.read_csv(self.clothingFilePath)
        housing_df = pd.read_csv(self.householdFilePath)
        #Reading the test output files
        combined_df = pd.read_csv(self.testOutputsPath)

        #Pandas query to fetch rwcounts of respective files in the combined file
        self.assertEqual(accessories_df.shape[0], combined_df[combined_df['filename'] == self.accessoriesFilePath].shape[0])
        self.assertEqual(clothing_df.shape[0], combined_df[combined_df['filename'] == self.clothingFilePath].shape[0])
        self.assertEqual(housing_df.shape[0], combined_df[combined_df['filename'] == self.householdFilePath].shape[0])
        
    '''
    Test to check if all possible columns across all files are present in the combined file
    '''
    def test_AllColumnsPresent(self):
        #Execute the combine csv on given test_data files as input and save the stdout content to test output file
        self.cc.combineCSV([self.csvCombinerFilePath, self.accessoriesFilePath, self.clothingFilePath, self.householdFilePath])
        self.testOutput.write(self.output.getvalue())
        self.testOutput.close()

        arguments = [self.accessoriesFilePath, self.clothingFilePath, self.householdFilePath]
        columnSet = set()
        #Iterate through all files to get unique column values and store them in columnSet
        for i in arguments:
            columnSet = columnSet.union(set(pd.read_csv(i).columns))
        columnSet.add('filename')
        combined_df = pd.read_csv(self.testOutputsPath)
        #Compare the columnSet and columns from test output file to validate correctness
        self.assertEqual(columnSet, set(combined_df.columns))


if __name__ == "__main__":
    unittest.main()