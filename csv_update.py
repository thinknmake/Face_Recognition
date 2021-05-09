from csv import DictWriter
  
# list of column names 
file_name = "detection_data.csv"
field_names = ['NAME','DATE',
               'TIME']
def update(name,date,time):  
    # Dictionary
    dict={'NAME':name,'DATE':date,
      'TIME':time }
  
    # Open your CSV file in append mode
    # Create a file object for this file
    with open(file_name, 'a') as f_object:
      
        # Pass the file object and a list 
        # of column names to DictWriter()
        # You will get a object of DictWriter
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)
  
        #Pass the dictionary as an argument to the Writerow()
        dictwriter_object.writerow(dict)
  
        #Close the file object
        f_object.close()
