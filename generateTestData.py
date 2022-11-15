#Referred the generate fixtures file in the assessment description to generate test_data for unit testing
import csv
import hashlib
import os
import random
import os.path as path

DIR = path.abspath(path.dirname(__file__))
FILES = {
    'clothing.csv': ('Blouses', 'Shirts', 'Tanks', 'Cardigans', 'Pants', 'Capris', '"Gingham" Shorts',),
    'accessories.csv': ('Watches', 'Wallets', 'Purses', 'Satchels',),
    'household_cleaners.csv': ('Kitchen Cleaner', 'Bathroom Cleaner',),
}


def write_file(writer, length, categories):
    writer.writerow(['email_hash', 'category'])
    for i in range(0, length):
        writer.writerow([
            hashlib.sha256('tech+test{}@pmg.com'.format(i).encode('utf-8')).hexdigest(),
            random.choice(categories),
        ])


def main():
    #If the test_data directory is not present, make a test_data directory
    if not os.path.exists('./test_data'):
        os.makedirs('test_data')
    for fn, categories in FILES.items():
        with open(path.join(DIR, 'test_data', fn), 'w', encoding='utf-8') as fh:
            write_file(
                csv.writer(fh, doublequote=False, escapechar='\\', quoting=csv.QUOTE_ALL),
                random.randint(100, 1000),
                categories
            )


if __name__ == '__main__':
    main()