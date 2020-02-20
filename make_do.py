from sys import argv
import os
import csv

def _read(filename):
    with open(filename) as inf, open(os.path.join("output", "merge_returns.do"), 'w') as mr, open(os.path.join("output","all_tkrs.do"), 'w') as outf:
        reader = csv.reader(inf)

        mr_output = r'use "C:\Users\Anne\Box Sync\December 2018 downloads\stata returns\dates.dta"' + '\n\n'
        do_out = ""
        for line in reader:
            try:
                name = line[3] # this assumes the name is in the 4th column and ticker is in the 5th
                ticker = line[4]
                if len(name.strip()) == 0 or len(ticker.strip()) == 0:
                    continue

                mr_output += generate_merge(name,ticker)
                do_out += generate_out(name, ticker)

            except Exception as e:
                print ("Error on line: {}".format(line))
                print (e)
        outf.write(do_out)
        mr.write(mr_output)

def generate_merge(name, tckr):
    out = r'merge m:m caldt using "C:\Users\Anne\Box Sync\December 2018 downloads\stata returns\{}-{}.dta'.format(tckr, name) + '\n'
    out += r'drop _merge ticker' + '\n'
    out += r'rename mret {}'.format(tckr) + '\n\n'
    return out

def generate_out(name, tckr):
    out = r'use "C:\Users\Anne\Box Sync\December 2018 downloads\epic wrds mutual funds list.dta"' + "\n"
    out += r'drop if permno != "{}"'.format(tckr) + "\n"
    out += r'save "C:\Users\Anne\Box Sync\December 2018 downloads\stata returns\{}-{}.dta", replace'.format(tckr, name) + "\n"
    out += r'use "C:\Users\Anne\Box Sync\December 2018 downloads\stata returns\dates.dta"' + "\n"
    out += r'merge m:m caldt using "C:\Users\Anne\Box Sync\December 2018 downloads\stata returns\{}-{}.dta"'.format(tckr, name) + "\n"
    out += r'drop _merge crsp_fundno' + "\n"
    out += r'save "C:\Users\Anne\Box Sync\December 2018 downloads\stata returns\{}-{}.dta", replace'.format(tckr, name) + "\n"
    out += r'export excel using "C:\Users\Anne\Box Sync\December 2018 downloads\monthly returns\{}-{}.xls", replace'.format(tckr, name) + "\n"
    out += r'export delimited using "C:\Users\Anne\Box Sync\December 2018 downloads\monthly returns\{}-{}.csv", replace'.format(tckr, name) + "\n\n"
    return out

if __name__ == '__main__':
    filename = argv[1]  #filename is name of csv
    _read(filename)
