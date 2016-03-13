# To verify log and determine the no. of packet drops.
# supply log file on the command line 

import sys 
import pdb 

debug_mode=1

# Open the file
if len(sys.argv) < 2: 
    # no file name, inform user
    print("no filename entered.")
    exit()
filename=str(sys.argv[1])
f=open(filename, 'r')


# Read a line until # hit
l=""
current_line_no=0
while(l.find('#') == -1):
    pl=l
    l=f.readline()
    current_line_no=current_line_no+1
   

# Get the first number 
index_of_pound=l.find('#')
data_number=int(l[index_of_pound+1:])
while(data_number == 2560):
    pl=l
    l=f.readline()
    current_line_no=current_line_no+1
    index_pount=l.find('#')
    data_number=int(l[index_of_pound+1:])
data_start_line=current_line_no
data_start = data_number

num_errors=0
prev_data_number=data_number
pl=l
l=f.readline()
current_line_no=current_line_no+1
while(l != ""): 
    #Get line number 
    index_of_pound=l.find('#')
    
    #Ignore if no pound sign found on the line
    if(index_of_pound != -1):   

        #Ignore heartbeat signal
        if(int(l[index_of_pound+1:]) != 2560):         
            prev_data_number=data_number
            data_number=int(l[index_of_pound+1:])           
          
            if(data_number != prev_data_number + 1): 
                print("----------------------------")
                print("%d,%d" %(data_number, prev_data_number))             
                print("%d: %s" %(current_line_no-1, pl)),       
                print("%d: %s" %(current_line_no, l)),
                num_errors=num_errors+(data_number-prev_data_number)+1
                                 
            pl=l

    l=f.readline()
    current_line_no=current_line_no+1
  
data_end=data_number
print("%s: Errors %d / %d" %(sys.argv[1], num_errors, (data_end-data_start)))
print("~%%Error: %f" %(float(num_errors)/(data_start-data_end) * 100))

f.close()
