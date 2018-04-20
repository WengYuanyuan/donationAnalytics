# coding: utf-8

import numpy as np
import sys
from datetime import datetime as dt

  
def check_record_validity(row):
    """
    check the validity of data entries
    delete the invalid data entries to ignore and skip an entire record
    """
    #ignore the record with non empty OTHER_ID 
    #ignore the record if empty in any of the following fields: CMTE_ID, NAME, TRANSACTION_DT, TRANSACTION_AMT   
    
    if(row[0]!= '' and row[7] != '' and row[13] != '' and row[14] != ''and row[15] == '' ): 
        
        # check the record if 'ZIP_CODE' is an invalid zipcode (i.e., empty, fewer than five digits)
        zip_code = row[10]
        if(len(zip_code) >= 5 and zip_code[:5].isdigit()):  
            return True
    return False

def main():
    """
    Process the input file line by line
    Compute the contributions from repeated donor so far
    as grouped by recipient, zip code and calendar year
    write to the output with only record of repeat donors
    """
    
    dict_donors = dict() # maintain a donor (name, zip)'s earliest contribution date
    dict_recipient = dict() # maintain a recipient's money from repeated donors in the certain year and zipcode
    
    f = open(sys.argv[2],'r') 
    percentile = float(f.read()) # read percentile for calculating running percentile
    
    with open(sys.argv[1]) as input_file: 
        
        repeat_donor_contri = [] # for documenting the contributions from repeated donors, for output file
        f_output = open(sys.argv[3], "w+") 
        
        for line in input_file: # streaming the input record  
            row = line.split('|')
            zip_code = row[10]
            if check_record_validity(row): # procede only with valid record 
                
                trans_date = dt.strptime(row[13], "%m%d%Y")
                donor_key = (row[7] , zip_code[:5]) # name and zip code for identifying same donor
                
                # check if the current processed record is from repeated donor                                         
                if donor_key not in dict_donors or dict_donors[donor_key] > trans_date: # identified not as repeated donor
                    dict_donors[donor_key] = trans_date
                
                else: # identified as repeated donor
                    # update dict_recipient
                    recipient_key = (row[0] , zip_code[:5], trans_date.year)
                    if recipient_key not in dict_recipient:
                        dict_recipient[recipient_key] = [int(row[14])]
                    else:
                        dict_recipient[recipient_key].append(int(row[14]))
                    
                    # adding the current record to repeated donor's contribution with required output format 
                    perc_value = np.percentile(np.array(dict_recipient[recipient_key]), percentile, interpolation='nearest')        
                    out_line = row[0] + "|" \
                               + zip_code[:5] + "|" \
                               + str(trans_date.year)+ "|" \
                               + str(perc_value) + "|" \
                               + str(sum(dict_recipient[recipient_key]))+ "|" \
                               + str(len(dict_recipient[recipient_key]))
                    
                    repeat_donor_contri.append(out_line)
                  
        f_output.write("\n".join(repeat_donor_contri))# save the results to output files 
        
    f_output.close()      
              

if __name__ == "__main__":
    main()
